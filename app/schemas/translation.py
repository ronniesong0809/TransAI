from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

class BatchTranslationRequest(BaseModel):
    texts: List[str]
    source_lang: str
    target_lang: str

class TranslationResponse(BaseModel):
    source_text: str
    target_text: str
    source_lang: str
    target_lang: str
    quality_score: Optional[float] = None
    created_at: datetime
    modified_at: datetime
    from_cache: bool
    is_confirmed: bool
    last_modified_by: Optional[str] = None
    reviewer_comments: Optional[str] = None
    human_modified: bool
    machine_translation: str

    class Config:
        from_attributes = True

class BatchTranslationResponse(BaseModel):
    translations: List[TranslationResponse]
    total_count: int
    cache_hits: int

class QualityCheckRequest(BaseModel):
    translation_id: int
    reviewer_comments: Optional[str] = None

class ReviewRequest(BaseModel):
    translation_id: int
    reviewer: str
    is_confirmed: bool
    comments: Optional[str] = None
    modified_text: Optional[str] = None