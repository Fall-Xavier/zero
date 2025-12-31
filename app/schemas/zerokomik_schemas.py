from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Union, Optional
    
class KomikSchema(BaseModel):
    komik_id: str  # primary key, wajib
    title: str  # wajib
    alternative_title: Optional[str] = None
    release_year: Optional[str] = None
    release_day: Optional[str] = None
    status: str  # wajib
    cover: Optional[str] = None
    type: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[float] = None
    readers: Optional[int] = 0
    bookmark: Optional[int] = 0
    genres: List[str] = []  # di DB text[], gunakan List[str]
    author: Optional[str] = None
    description: Optional[str] = None
    chapters: List[Any] = []  # ini bisa kosong atau diisi list chapter
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    
class ChapterSchema(BaseModel):
    komik_id: str
    chapter_id: str
    chapter_number: str
    chapter_readers: int
    chapter_update_at: Optional[str] = None
    chapter_images: List[Any] = []
    
class Pagination(BaseModel):
    page: int
    total_items: int
    total_pages: int
    prev_page: bool
    next_page: bool
    
class KomikListResponse(BaseModel):
    list: List[KomikSchema]
    pagination: Pagination