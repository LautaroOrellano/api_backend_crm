from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items: List[T]
    total_items: int
    total_pages: int
    limit: int
    offset: int
