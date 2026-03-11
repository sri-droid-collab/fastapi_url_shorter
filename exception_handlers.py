import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from logger import logger

async def global_exception_handler(request: Request, exc: Exception):
    """Fallback exception handler for unhandled exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{request_id}] Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal Server Error",
            "request_id": request_id
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handler for FastAPI standard HTTPExceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Log 5xx errors as error, others as warning
    if exc.status_code >= 500:
        logger.error(f"[{request_id}] HTTP Exception {exc.status_code}: {exc.detail}")
    else:
        logger.warning(f"[{request_id}] HTTP Exception {exc.status_code}: {exc.detail}")
        
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": request_id
        },
        headers=getattr(exc, "headers", None)
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for Pydantic validation errors."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.warning(f"[{request_id}] Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation Error",
            "errors": exc.errors(),
            "request_id": request_id
        }
    )
