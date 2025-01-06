from fastapi import FastAPI
from app.api.endpoints import translation
from app.core.database import engine
from app.models.translation import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Translation API")

# Include routers
app.include_router(translation.router, prefix="/api/v1", tags=["translation"]) 