from fastapi import FastAPI
from app.api.documents import router as document_router

from app.api.health import router as health_router
from app.core.config import settings
from app.api.chat import router as chat_router


app = FastAPI(title=settings.app_name, version=settings.app_version)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(document_router)

@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Knowledge Agent API is running.",
        "docs": "/docs",
        "health": "/health",
    }

