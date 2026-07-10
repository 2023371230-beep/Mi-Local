from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.infrastructure.logging.logger import setup_logging
from app.presentation.endpoints import agent, chat, health, ingest, logs, models, rag, web_search


def create_app() -> FastAPI:
    setup_logging(get_settings())
    app = FastAPI(
        title="Modelo IA Carrera Backend",
        version="0.1.0",
        description="Backend local modular para IA, RAG, skills y busqueda web.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(chat.router)
    app.include_router(health.router)
    app.include_router(models.router)
    app.include_router(ingest.router)
    app.include_router(rag.router)
    app.include_router(web_search.router)
    app.include_router(logs.router)
    app.include_router(agent.router)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "detail": str(exc)},
        )

    return app


app = create_app()
