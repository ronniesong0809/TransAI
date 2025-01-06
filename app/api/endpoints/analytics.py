from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, distinct, case
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from app.core.database import get_db
from app.models.translation import Translation
from app.schemas.analytics import (
    TranslationAnalytics,
    LanguagePairStats,
    TimeSeriesPoint,
    QualityDistribution
)

router = APIRouter()

@router.get("/overview", response_model=TranslationAnalytics)
def get_translation_analytics(
    db: Session = Depends(get_db),
    days: Optional[int] = Query(30, ge=1, le=365)
):
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Base query for the time period
    base_query = db.query(Translation).filter(
        Translation.created_at >= start_date,
        Translation.created_at <= end_date
    )
    
    # Calculate basic stats
    total_translations = base_query.count()
    unique_texts = base_query.distinct(Translation.source_text).count()
    
    # Calculate average quality score
    quality_stats = db.query(
        func.avg(Translation.quality_score).label('avg_quality')
    ).filter(Translation.quality_score.isnot(None)).first()
    
    # Calculate human modification percentage
    human_modified = base_query.filter(Translation.human_modified == True).count()
    human_modified_pct = (human_modified / total_translations * 100) if total_translations > 0 else 0
    
    # Get top language pairs
    language_pairs = db.query(
        Translation.source_lang,
        Translation.target_lang,
        func.count().label('count'),
        func.avg(Translation.quality_score).label('avg_quality'),
        func.sum(case([(Translation.human_modified == True, 1)], else_=0)).label('human_modified_count')
    ).group_by(
        Translation.source_lang,
        Translation.target_lang
    ).order_by(func.count().desc()).limit(5).all()
    
    # Calculate quality distribution
    quality_dist = db.query(
        func.sum(case([(Translation.quality_score < 0.2, 1)], else_=0)).label('range_0_20'),
        func.sum(case([(Translation.quality_score >= 0.2, 1), (Translation.quality_score < 0.4, 1)], else_=0)).label('range_20_40'),
        func.sum(case([(Translation.quality_score >= 0.4, 1), (Translation.quality_score < 0.6, 1)], else_=0)).label('range_40_60'),
        func.sum(case([(Translation.quality_score >= 0.6, 1), (Translation.quality_score < 0.8, 1)], else_=0)).label('range_60_80'),
        func.sum(case([(Translation.quality_score >= 0.8, 1)], else_=0)).label('range_80_100')
    ).filter(Translation.quality_score.isnot(None)).first()
    
    # Calculate daily stats
    daily_stats = db.query(
        func.date_trunc('day', Translation.created_at).label('date'),
        func.count().label('count'),
        func.avg(Translation.quality_score).label('avg_quality')
    ).group_by(
        func.date_trunc('day', Translation.created_at)
    ).order_by('date').all()
    
    # Calculate cache hit rate
    total_requests = total_translations
    cache_hits = base_query.filter(Translation.human_modified == False).count()
    cache_hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0
    
    return TranslationAnalytics(
        total_translations=total_translations,
        total_unique_texts=unique_texts,
        avg_quality_score=quality_stats.avg_quality or 0.0,
        human_modified_percentage=human_modified_pct,
        top_language_pairs=[
            LanguagePairStats(
                source_lang=pair.source_lang,
                target_lang=pair.target_lang,
                count=pair.count,
                avg_quality=pair.avg_quality or 0.0,
                human_modified_count=pair.human_modified_count
            ) for pair in language_pairs
        ],
        quality_distribution=QualityDistribution(
            range_0_20=quality_dist.range_0_20 or 0,
            range_20_40=quality_dist.range_20_40 or 0,
            range_40_60=quality_dist.range_40_60 or 0,
            range_60_80=quality_dist.range_60_80 or 0,
            range_80_100=quality_dist.range_80_100 or 0
        ),
        daily_stats=[
            TimeSeriesPoint(
                date=stat.date,
                count=stat.count,
                avg_quality=stat.avg_quality or 0.0
            ) for stat in daily_stats
        ],
        cache_hit_rate=cache_hit_rate
    )

@router.get("/language-pairs", response_model=List[LanguagePairStats])
def get_language_pair_stats(
    db: Session = Depends(get_db),
    min_count: int = Query(1, ge=1)
):
    pairs = db.query(
        Translation.source_lang,
        Translation.target_lang,
        func.count().label('count'),
        func.avg(Translation.quality_score).label('avg_quality'),
        func.sum(case([(Translation.human_modified == True, 1)], else_=0)).label('human_modified_count')
    ).group_by(
        Translation.source_lang,
        Translation.target_lang
    ).having(
        func.count() >= min_count
    ).order_by(
        func.count().desc()
    ).all()
    
    return [
        LanguagePairStats(
            source_lang=pair.source_lang,
            target_lang=pair.target_lang,
            count=pair.count,
            avg_quality=pair.avg_quality or 0.0,
            human_modified_count=pair.human_modified_count
        ) for pair in pairs
    ] 