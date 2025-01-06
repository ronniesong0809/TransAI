from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

class LanguagePairStats(BaseModel):
    source_lang: str
    target_lang: str
    count: int
    avg_quality: float
    human_modified_count: int

class TimeSeriesPoint(BaseModel):
    date: datetime
    count: int
    avg_quality: float

class QualityDistribution(BaseModel):
    range_0_20: int
    range_20_40: int
    range_40_60: int
    range_60_80: int
    range_80_100: int

class TranslationAnalytics(BaseModel):
    total_translations: int
    total_unique_texts: int
    avg_quality_score: float
    human_modified_percentage: float
    top_language_pairs: List[LanguagePairStats]
    quality_distribution: QualityDistribution
    daily_stats: List[TimeSeriesPoint]
    cache_hit_rate: float 