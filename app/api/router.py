from fastapi import APIRouter

from app.api.routes import urls

# This is the single router that main.py imports.
# Add new sub-routers here as the project grows.
api_router = APIRouter()
api_router.include_router(urls.router)
