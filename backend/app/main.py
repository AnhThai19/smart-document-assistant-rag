from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Smart Document Assistant RAG backend",
)

app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Smart Document Assistant RAG API is running",
        "environment": settings.app_env,
    }