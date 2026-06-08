from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routes import conversions, health, uploads


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="MD Converter API", version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(uploads.router, prefix="/api")
    app.include_router(conversions.router, prefix="/api")

    return app


app = create_app()

