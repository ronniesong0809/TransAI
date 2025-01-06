from fastapi import FastAPI
from app.api.endpoints import translation
from app.core.database import engine
from app.models.translation import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Translation API")

app.include_router(translation.router, prefix="/api/v1", tags=["translation"]) 