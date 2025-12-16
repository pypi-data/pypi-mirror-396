from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional, TypeVar, Callable, Dict, Any, Type
import math
import concurrent.futures
from tqdm import tqdm
import json

from .helpers import human_format

client = OpenAI()

DEFAULT_MODEL = "gpt-4.1-mini-2025-04-14"

T = TypeVar("T")  # Type variable for input items
R = TypeVar("R")  # Type variable for chunk processing result


def parse_with_model(
    messages: List[Dict[str, str]],
    response_format: Type[BaseModel],
    temperature: float = 0.3,
    model: Optional[str] = DEFAULT_MODEL,
    debug_print=False,
) -> Any:
    """
    Helper to parse structured responses using the OpenAI client.

    Args:
        model (str): Model name (e.g., "gpt-4o").
        messages (List[Dict[str, str]]): List of chat messages (role/content).
        response_format (Type[BaseModel]): Pydantic model for structured response.
        temperature (float): Sampling temperature.

    Returns:
        Parsed object as per response_format, or None on failure.
    """
    try:
        completion = client.beta.chat.completions.parse(
            model=model if model else DEFAULT_MODEL,
            messages=messages,  # type: ignore
            response_format=response_format,
            # temperature=temperature,
        )
        # json_str = json.dumps(completion.dict(), indent=2)
        # print(json_str)
        # return completion.choices[0].message.parsed
        if not completion.usage:
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "output": completion.choices[0].message.parsed,
            }

        if debug_print:
            new_messages = messages + [
                {
                    "role": "assistant",
                    "content": str(completion.choices[0].message.parsed),
                }
            ]
            string = json.dumps(new_messages, indent=2)
            string = string.replace("\\n", "\n")
            print(string)

        return {
            "input_tokens": completion.usage.prompt_tokens,
            "output_tokens": completion.usage.completion_tokens,
            "output": completion.choices[0].message.parsed,
        }
    except Exception as e:
        print(f"Error during model parsing: {e}")
        return None


def process_items_in_chunks(
    items: List[T],
    chunk_processor_fn: Callable[[List[T]], Optional[R]],
    chunk_size: int = 32,
    max_workers: Optional[int] = None,
    progress_desc: str = "Processing Chunks",
    usage: Optional[Dict[str, int]] = None,
) -> List[R]:
    """
    Generic helper to process a list of items in chunks, sequentially or concurrently.

    Args:
        items (List[T]): The list of items to process.
        chunk_processor_fn (Callable[[List[T]], Optional[R]]): Function that takes a chunk (list of items)
                                                              and returns a result (or None).
        chunk_size (int): Size of each processing chunk.
        max_workers (Optional[int]): Number of workers for concurrent execution.
                                     If None or 0, runs sequentially.
        progress_desc (str): Description for the tqdm progress bar.

    Returns:
        List[R]: A list of non-None results returned by chunk_processor_fn for each chunk.
    """
    if not items:
        return []

    num_chunks = math.ceil(len(items) / chunk_size)
    collected_results: List[R] = []

    if max_workers is not None and max_workers > 0:
        # Concurrent execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i in range(num_chunks):
                start_index = i * chunk_size
                end_index = min((i + 1) * chunk_size, len(items))
                chunk = items[start_index:end_index]
                if chunk:  # Ensure chunk is not empty
                    futures.append(executor.submit(chunk_processor_fn, chunk))

            pbar = tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc=progress_desc,
                unit="chunk",
            )

            # Progress bar for futures
            for future in pbar:
                try:
                    result = future.result()
                    if result is not None:
                        collected_results.append(result)
                    else:
                        print("Error: Received None result from ai.")
                    if usage is not None:
                        input_tokens = usage.get("input_tokens", 0)
                        output_tokens = usage.get("output_tokens", 0)
                        pbar.set_postfix(
                            {
                                "inTokens": human_format(input_tokens),
                                "outTokens": human_format(output_tokens),
                            }
                        )
                except Exception as exc:
                    # Log or handle exceptions from chunk processing
                    print(f"Chunk generated an exception: {exc}")
    else:
        pbar = tqdm(range(num_chunks), desc=progress_desc, unit="chunk")
        # Sequential execution
        for i in pbar:
            start_index = i * chunk_size
            end_index = min((i + 1) * chunk_size, len(items))
            chunk = items[start_index:end_index]
            if chunk:  # Ensure chunk is not empty
                try:
                    result = chunk_processor_fn(chunk)
                    if result is not None:
                        collected_results.append(result)
                    else:
                        print("Error: Received None result from ai.")

                    if usage is not None:
                        input_tokens = usage.get("input_tokens", 0)
                        output_tokens = usage.get("output_tokens", 0)
                        pbar.set_postfix(
                            {
                                "inTokens": human_format(input_tokens),
                                "outTokens": human_format(output_tokens),
                            }
                        )
                except Exception as exc:
                    # Log or handle exceptions from chunk processing
                    print(f"Chunk generated an exception: {exc}")

    return collected_results


def process_items_in_already_chunked(
    chunks: List[List[T]],
    chunk_processor_fn: Callable[[List[T]], Optional[R]],
    max_workers: Optional[int] = None,
    progress_desc: str = "Processing Chunks",
    usage: Optional[Dict[str, int]] = None,
) -> List[R]:
    if not chunks or len(chunks) == 0:
        return []

    num_chunks = len(chunks)
    collected_results: List[R] = []

    if max_workers is not None and max_workers > 0:
        # Concurrent execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i in range(num_chunks):
                chunk = chunks[i]
                if chunk:  # Ensure chunk is not empty
                    futures.append(executor.submit(chunk_processor_fn, chunk))

            pbar = tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc=progress_desc,
                unit="chunk",
            )
            # Progress bar for futures
            for future in pbar:
                try:
                    result = future.result()
                    if result is not None:
                        collected_results.append(result)
                    else:
                        print("Error: Received None result from ai.")
                    if usage is not None:
                        input_tokens = usage.get("input_tokens", 0)
                        output_tokens = usage.get("output_tokens", 0)
                        pbar.set_postfix(
                            {
                                "inTokens": human_format(input_tokens),
                                "outTokens": human_format(output_tokens),
                            }
                        )
                except Exception as exc:
                    # Log or handle exceptions from chunk processing
                    print(f"Chunk generated an exception: {exc}")
    else:
        pbar = tqdm(range(num_chunks), desc=progress_desc, unit="chunk")
        # Sequential execution
        for i in pbar:
            chunk = chunks[i]
            if chunk:  # Ensure chunk is not empty
                try:
                    result = chunk_processor_fn(chunk)
                    if result is not None:
                        collected_results.append(result)
                    else:
                        print("Error: Received None result from ai.")
                    if usage is not None:
                        input_tokens = usage.get("input_tokens", 0)
                        output_tokens = usage.get("output_tokens", 0)
                        pbar.set_postfix(
                            {
                                "inTokens": human_format(input_tokens),
                                "outTokens": human_format(output_tokens),
                            }
                        )
                except Exception as exc:
                    # Log or handle exceptions from chunk processing
                    print(f"Chunk generated an exception: {exc}")

    return collected_results


def add_counts_from_phrases(
    words_df,
    phrases_df,
    word_col="word",
    phrase_col="phrase",
    count_col="count",
    default_value=1,
):
    count_map = dict(zip(phrases_df[phrase_col], phrases_df[count_col]))
    result_df = words_df.copy()
    result_df[count_col] = (
        result_df[phrase_col].map(count_map).fillna(default_value).astype(int)
    )
    return result_df
