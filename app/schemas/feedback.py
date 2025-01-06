from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class FeedbackRequest(BaseModel):
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    translation_id: int
    user_id: str
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackStats(BaseModel):
    total_feedbacks: int
    average_rating: float
    rating_distribution: Dict[str, int] 