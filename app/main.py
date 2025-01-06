from fastapi import FastAPI
from app.api.endpoints import translation, feedback
from app.core.database import engine
from app.models import translation as translation_model
from app.models import feedback as feedback_model

# Create database tables
translation_model.Base.metadata.create_all(bind=engine)
feedback_model.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Translation API")

# Include routers
app.include_router(translation.router, prefix="/api/v1/translations", tags=["translations"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["feedback"]) 