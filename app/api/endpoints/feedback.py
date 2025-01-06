from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.translation import Translation
from app.models.feedback import TranslationFeedback
from app.schemas.feedback import FeedbackRequest, FeedbackResponse, FeedbackStats

router = APIRouter()

@router.post("/{translation_id}", response_model=FeedbackResponse)
def create_feedback(
    translation_id: int,
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    feedback = TranslationFeedback(
        translation_id=translation_id,
        user_id=request.user_id,
        rating=request.rating,
        comment=request.comment
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return feedback

@router.get("/{translation_id}", response_model=List[FeedbackResponse])
def get_translation_feedback(
    translation_id: int,
    db: Session = Depends(get_db)
):
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    return translation.feedbacks

@router.get("/stats/overall", response_model=FeedbackStats)
def get_feedback_stats(db: Session = Depends(get_db)):
    feedbacks = db.query(TranslationFeedback).all()
    
    if not feedbacks:
        return FeedbackStats(
            total_feedbacks=0,
            average_rating=0.0,
            rating_distribution={str(i): 0 for i in range(1, 6)}
        )
    
    total = len(feedbacks)
    avg_rating = sum(f.rating for f in feedbacks) / total
    distribution = {str(i): 0 for i in range(1, 6)}
    
    for feedback in feedbacks:
        distribution[str(feedback.rating)] += 1
    
    return FeedbackStats(
        total_feedbacks=total,
        average_rating=round(avg_rating, 2),
        rating_distribution=distribution
    ) 