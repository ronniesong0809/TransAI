from fastapi import FastAPI
from apis import translation, feedback, analytics
from core.database import engine
from models import translation as translation_model
from models import feedback as feedback_model
import logging

# Create database tables
translation_model.Base.metadata.create_all(bind=engine)
feedback_model.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Translation API")

# Include routers
app.include_router(translation.router, prefix="/api/v1/translations", tags=["translations"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["feedback"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__) 