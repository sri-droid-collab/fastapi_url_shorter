from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import client
from routes import router
from logger import setup_logging, logger
from middlewares import LoggingMiddleware
from exception_handlers import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle manager."""
    setup_logging()
    logger.info("Starting up application lifecycle...")
    # Startup: verify MongoDB connectivity
    await client.admin.command("ping")
    logger.info("✅  Connected to MongoDB.")
    yield
    # Shutdown: close the motor client
    client.close()
    logger.info("🔌  MongoDB connection closed.")


app = FastAPI(
    title="URL Shortening Service",
    description=(
        "A RESTful URL shortening service built with **FastAPI** and **MongoDB**.\n\n"
        "## Features\n"
        "- Create, read, update, and delete short URLs\n"
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

app.include_router(router)


@app.get("/", tags=["Health"], summary="Health check")
async def root():
    """Simple health-check endpoint."""
    return {"status": "ok", "message": "URL Shortening Service is running 🚀"}
