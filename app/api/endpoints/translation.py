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
    BatchTranslationResponse
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
            from_cache=True
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
        modified_at=now
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
        from_cache=False
    )

@router.post("/translate/batch/", response_model=BatchTranslationResponse)
async def batch_translate(request: BatchTranslationRequest, db: Session = Depends(get_db)):
    results = []
    cache_hits = 0
    
    for text in request.texts:
        # Check cache first
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
        
        # Translate new text
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

@router.get("/translations/", response_model=List[TranslationResponse])
def list_translations(db: Session = Depends(get_db)):
    translations = db.query(Translation).all()
    return [
        TranslationResponse(
            source_text=t.source_text,
            target_text=t.target_text,
            source_lang=t.source_lang,
            target_lang=t.target_lang,
            quality_score=t.quality_score,
            created_at=t.created_at,
            modified_at=t.modified_at,
            from_cache=True
        ) for t in translations
    ]

@router.post("/quality-check/{translation_id}")
def check_translation_quality(
    translation_id: int,
    request: QualityCheckRequest,
    db: Session = Depends(get_db)
):
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    quality_score = evaluate_translation_quality(
        translation.source_text,
        translation.target_text,
        translation.source_lang,
        translation.target_lang
    )
    
    translation.quality_score = quality_score
    translation.modified_at = datetime.utcnow()
    db.commit()
    
    return {"translation_id": translation_id, "quality_score": quality_score} 