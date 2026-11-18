from fastapi import FastAPI

from app.api.endpoints import health
from app.api.error_handlers import register_exception_handlers
from app.api.router import api_router

app = FastAPI(title="RPG Tabletop App API", version="0.1.0")

register_exception_handlers(app)

app.include_router(health.router)