from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db.database import client
from app.api.router import api_router
from app.core.logger import setup_logging, logger
from app.core.middlewares import LoggingMiddleware
from app.core.exception_handlers import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle manager."""
    setup_logging()
    logger.info("Starting up application lifecycle...")
    # Verify MongoDB is reachable before accepting traffic
    await client.admin.command("ping")
    logger.info("✅  Connected to MongoDB.")
    yield
    # Clean up the motor client on shutdown
    client.close()
    logger.info("🔌  MongoDB connection closed.")


app = FastAPI(
    title="URL Shortening Service",
    description=(
        "A RESTful URL shortening service built with **FastAPI** and **MongoDB**.\n\n"
        "## Features\n"
        "- Create, read, update, and delete short URLs\n"
        "- List all stored short URLs\n"
        "- Track access counts per short URL\n"
        "- Redirect endpoint (`/r/{shortCode}`) for seamless browser redirects\n"
        "- Cryptographically random 6-character short codes\n"
    ),
    version="1.0.0",
    contact={"name": "URL Shortener API"},
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(api_router)


@app.get("/", tags=["Health"], summary="Health check")
async def root():
    """Simple health-check endpoint."""
    return {"status": "ok", "message": "URL Shortening Service is running 🚀"}
