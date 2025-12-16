from typing import Optional, Type, TypeVar, Generic, get_args
from pydantic import BaseModel
from .gpt import (
    parse_with_model,
    process_items_in_already_chunked,
    process_items_in_chunks,
)
from .models import BaseResponse


# Generic type for your Pydantic response model
T = TypeVar("T", bound=BaseModel)


def create_response_model(item_model: type[T]):
    name = f"{item_model.__name__}_Response"
    return type(name, (BaseResponse[item_model],), {})


class BaseLLM(Generic[T]):
    response_model: Type[T]
    system_prompt: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Inspect the class's bases to find the Generic type [T]
        for base in getattr(cls, "__orig_bases__", []):
            args = get_args(base)
            if args:
                # Automatically set response_model to the first generic argument
                cls.response_model = args[0]
                break

    def __init__(
        self,
        chunk_size: int = 24,
        progress_desc: str = "Processing Chunks",
        max_workers: Optional[int] = None,
        model: Optional[str] = None,
        debug_print: bool = False,
    ):
        if not hasattr(self, "response_model"):
            raise ValueError("Subclasses must define a 'response_model' attribute.")

        if not hasattr(self, "system_prompt"):
            raise ValueError("Subclasses must define a 'system_prompt' attribute.")

        self.chunk_size = chunk_size
        self.progress_desc = progress_desc
        self.max_workers = max_workers
        self.memory = set()
        self.model = model
        self.usage = {"input_tokens": 0, "output_tokens": 0}
        self.debug_print = debug_print

    def process_chunk(self, items: list):
        """Calls the LLM for a chunk of text"""
        try:
            debug_print = self.debug_print
            self.debug_print = False  # only print first time
            chunk_data = self.format_input_data(items)
            model_response = parse_with_model(
                messages=[
                    {"role": "developer", "content": self.system_prompt},
                    {"role": "user", "content": chunk_data},
                ],
                response_format=create_response_model(self.response_model),
                model=self.model,
                debug_print=debug_print,
            )


            response = model_response.get("output")
            self.usage["input_tokens"] += model_response.get("input_tokens", 0)
            self.usage["output_tokens"] += model_response.get("output_tokens", 0)

            # update memory if model returns 'keyword'-like fields
            for item in getattr(response, "values", []):
                if hasattr(item, "keyword"):
                    self.memory.add(item.keyword)
            return response
        except Exception as e:
            print(f"Error processing chunk: {e}")
            return None

    def format_input_data(self, items) -> str:
        """Override this in subclasses to define how input is formatted."""
        raise NotImplementedError

    def run(self, data: list, is_chunked=False) -> BaseResponse[T]:
        """Main entry point"""
        chunk_fn = lambda chunk: self.process_chunk(chunk)
        self.usage = {"input_tokens": 0, "output_tokens": 0}

        if not is_chunked:
            responses = process_items_in_chunks(
                data,
                chunk_fn,
                max_workers=self.max_workers,
                progress_desc=self.progress_desc,
                chunk_size=self.chunk_size,
                usage=self.usage,
            )
        else:
            responses = process_items_in_already_chunked(
                data,
                chunk_fn,
                max_workers=self.max_workers,
                progress_desc=self.progress_desc,
                usage=self.usage,
            )

        results = []
        for response in responses:
            if response and hasattr(response, "values") and response.values:
                results.extend(response.values)

        response_instance = BaseResponse[self.response_model](values=results)
        return response_instance
