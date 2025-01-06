from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

class TranslationResponse(BaseModel):
    source_text: str
    target_text: str
    source_lang: str
    target_lang: str
    quality_score: Optional[float] = None
    created_at: datetime
    from_cache: bool

    class Config:
        from_attributes = True

class QualityCheckRequest(BaseModel):
    translation_id: int
    reviewer_comments: Optional[str] = None 