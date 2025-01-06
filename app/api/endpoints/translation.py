from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.openai_client import translate_text, evaluate_translation_quality
from app.models.translation import Translation
from app.schemas.translation import (
    TranslationRequest, 
    TranslationResponse, 
    QualityCheckRequest,
    BatchTranslationRequest,
    BatchTranslationResponse,
    ReviewRequest,
    FeedbackRequest,
    FeedbackResponse,
    TranslationWithFeedback
)
from datetime import datetime

router = APIRouter()

@router.post("/translate/", response_model=TranslationResponse)
def translate(request: TranslationRequest, db: Session = Depends(get_db)):
    cached_translation = db.query(Translation).filter(
        Translation.source_text == request.text,
        Translation.source_lang == request.source_lang,
        Translation.target_lang == request.target_lang
    ).first()
    
    if cached_translation:
        return TranslationResponse(
            source_text=cached_translation.source_text,
            target_text=cached_translation.target_text,
            source_lang=cached_translation.source_lang,
            target_lang=cached_translation.target_lang,
            quality_score=cached_translation.quality_score,
            created_at=cached_translation.created_at,
            modified_at=cached_translation.modified_at,
            from_cache=True,
            is_confirmed=cached_translation.is_confirmed,
            last_modified_by=cached_translation.last_modified_by,
            reviewer_comments=cached_translation.reviewer_comments,
            human_modified=cached_translation.human_modified,
            machine_translation=cached_translation.machine_translation or cached_translation.target_text
        )
    
    translated_text = translate_text(
        request.text,
        request.source_lang,
        request.target_lang
    )
    
    quality_score = evaluate_translation_quality(
        request.text,
        translated_text,
        request.source_lang,
        request.target_lang
    )
    
    now = datetime.utcnow()
    db_translation = Translation(
        source_text=request.text,
        target_text=translated_text,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
        quality_score=quality_score,
        created_at=now,
        modified_at=now,
        machine_translation=translated_text
    )
    db.add(db_translation)
    db.commit()
    db.refresh(db_translation)
    
    return TranslationResponse(
        source_text=db_translation.source_text,
        target_text=db_translation.target_text,
        source_lang=db_translation.source_lang,
        target_lang=db_translation.target_lang,
        quality_score=db_translation.quality_score,
        created_at=db_translation.created_at,
        modified_at=db_translation.modified_at,
        from_cache=False,
        is_confirmed=db_translation.is_confirmed,
        last_modified_by=db_translation.last_modified_by,
        reviewer_comments=db_translation.reviewer_comments,
        human_modified=db_translation.human_modified,
        machine_translation=db_translation.machine_translation
    )

@router.post("/translate/batch/", response_model=BatchTranslationResponse)
async def batch_translate(request: BatchTranslationRequest, db: Session = Depends(get_db)):
    results = []
    cache_hits = 0
    
    for text in request.texts:
        cached_translation = db.query(Translation).filter(
            Translation.source_text == text,
            Translation.source_lang == request.source_lang,
            Translation.target_lang == request.target_lang
        ).first()
        
        if cached_translation:
            cache_hits += 1
            results.append(TranslationResponse(
                source_text=cached_translation.source_text,
                target_text=cached_translation.target_text,
                source_lang=cached_translation.source_lang,
                target_lang=cached_translation.target_lang,
                quality_score=cached_translation.quality_score,
                created_at=cached_translation.created_at,
                modified_at=cached_translation.modified_at,
                from_cache=True
            ))
            continue
        
        translated_text = translate_text(
            text,
            request.source_lang,
            request.target_lang
        )
        
        quality_score = evaluate_translation_quality(
            text,
            translated_text,
            request.source_lang,
            request.target_lang
        )
        
        now = datetime.utcnow()
        db_translation = Translation(
            source_text=text,
            target_text=translated_text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            quality_score=quality_score,
            created_at=now,
            modified_at=now
        )
        db.add(db_translation)
        db.commit()
        db.refresh(db_translation)
        
        results.append(TranslationResponse(
            source_text=db_translation.source_text,
            target_text=db_translation.target_text,
            source_lang=db_translation.source_lang,
            target_lang=db_translation.target_lang,
            quality_score=db_translation.quality_score,
            created_at=db_translation.created_at,
            modified_at=db_translation.modified_at,
            from_cache=False
        ))
    
    return BatchTranslationResponse(
        translations=results,
        total_count=len(request.texts),
        cache_hits=cache_hits
    )

@router.post("/translations/{translation_id}/review", response_model=TranslationResponse)
def review_translation(
    translation_id: int,
    request: ReviewRequest,
    db: Session = Depends(get_db)
):
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    translation.is_confirmed = request.is_confirmed
    translation.last_modified_by = request.reviewer
    translation.reviewer_comments = request.comments
    
    if request.modified_text:
        translation.human_modified = True
        if not translation.machine_translation:
            translation.machine_translation = translation.target_text
        translation.target_text = request.modified_text
        
        quality_score = evaluate_translation_quality(
            translation.source_text,
            request.modified_text,
            translation.source_lang,
            translation.target_lang
        )
        translation.quality_score = quality_score
    
    translation.modified_at = datetime.utcnow()
    db.commit()
    db.refresh(translation)
    
    return TranslationResponse(
        source_text=translation.source_text,
        target_text=translation.target_text,
        source_lang=translation.source_lang,
        target_lang=translation.target_lang,
        quality_score=translation.quality_score,
        created_at=translation.created_at,
        modified_at=translation.modified_at,
        from_cache=True,
        is_confirmed=translation.is_confirmed,
        last_modified_by=translation.last_modified_by,
        reviewer_comments=translation.reviewer_comments,
        human_modified=translation.human_modified,
        machine_translation=translation.machine_translation or translation.target_text
    ) 

@router.post("/translations/{translation_id}/feedback", response_model=FeedbackResponse)
def create_feedback(
    translation_id: int,
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    if not 1 <= request.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
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

@router.get("/translations/{translation_id}/feedback", response_model=List[FeedbackResponse])
def get_translation_feedback(
    translation_id: int,
    db: Session = Depends(get_db)
):
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    return translation.feedbacks

@router.get("/translations/{translation_id}/with-feedback", response_model=TranslationWithFeedback)
def get_translation_with_feedback(
    translation_id: int,
    db: Session = Depends(get_db)
):
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    return TranslationWithFeedback(
        source_text=translation.source_text,
        target_text=translation.target_text,
        source_lang=translation.source_lang,
        target_lang=translation.target_lang,
        quality_score=translation.quality_score,
        created_at=translation.created_at,
        modified_at=translation.modified_at,
        from_cache=True,
        is_confirmed=translation.is_confirmed,
        last_modified_by=translation.last_modified_by,
        reviewer_comments=translation.reviewer_comments,
        human_modified=translation.human_modified,
        machine_translation=translation.machine_translation,
        feedbacks=translation.feedbacks
    )

@router.get("/translations/feedback/stats")
def get_feedback_stats(db: Session = Depends(get_db)):
    feedbacks = db.query(TranslationFeedback).all()
    
    if not feedbacks:
        return {
            "total_feedbacks": 0,
            "average_rating": 0,
            "rating_distribution": {str(i): 0 for i in range(1, 6)}
        }
    
    total = len(feedbacks)
    avg_rating = sum(f.rating for f in feedbacks) / total
    distribution = {str(i): 0 for i in range(1, 6)}
    
    for feedback in feedbacks:
        distribution[str(feedback.rating)] += 1
    
    return {
        "total_feedbacks": total,
        "average_rating": round(avg_rating, 2),
        "rating_distribution": distribution
    } 