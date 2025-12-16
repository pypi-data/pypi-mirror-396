from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)

class BaseResponse(BaseModel, Generic[T]):
    """A reusable base response model that wraps a list of items."""
    values: List[T] = Field(..., description="A list of response items.")


class FormattedWord(BaseModel):
    phrase: str = Field(..., description="The user searched phrase.")
    keyword: str = Field(..., description="The correct keyword or product name identified.")


def make_response_model(model_cls):
    return BaseResponse[model_cls]

