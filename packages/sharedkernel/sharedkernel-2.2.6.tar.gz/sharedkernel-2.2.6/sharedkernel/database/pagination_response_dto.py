from typing import List, TypeVar, Generic

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class PaginationResponseDto(BaseModel, Generic[T]):
    data: List[T] | None = [] 
    total_items: int | None = 0
    page_size: int | None = 0
    current_page: int | None = 0
    total_pages: int | None = 0
    has_next: bool | None = False
    has_prev: bool | None = False

