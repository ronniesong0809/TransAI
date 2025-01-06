from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Translation(Base):
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True, index=True)
    source_text = Column(String, index=True)
    target_text = Column(String)
    source_lang = Column(String)
    target_lang = Column(String)
    quality_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_confirmed = Column(Boolean, default=False)
    last_modified_by = Column(String, nullable=True)
    reviewer_comments = Column(String, nullable=True)
    human_modified = Column(Boolean, default=False)
    machine_translation = Column(String)
    
    feedbacks = relationship("TranslationFeedback", back_populates="translation")