import logging

import uvicorn
from fastapi import FastAPI

from semiconductor import __version__
from semiconductor.api import router
from semiconductor.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    application = FastAPI(
        title="Semiconductor AI Troubleshooting API",
        description="Phase 1 operational data and investigation API",
        version=__version__,
    )
    application.include_router(router)

    @application.get("/")
    def root() -> dict:
        return {
            "service": "semiconductor-ai-troubleshooting",
            "version": __version__,
            "docs": "/docs",
        }

    return application


app = create_app()


def run() -> None:
    uvicorn.run("semiconductor.main:app", host="0.0.0.0", port=8000)
