from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class TranslationFeedback(Base):
    __tablename__ = "translation_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    translation_id = Column(Integer, ForeignKey("translations.id"))
    user_id = Column(String, index=True)
    rating = Column(Integer)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    translation = relationship("Translation", back_populates="feedbacks") 