import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log every incoming request and its final response."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        # Attach request_id to request state so exception handlers can read it
        request.state.request_id = request_id

        start_time = time.time()
        client_ip = request.client.host if request.client else "Unknown"
        logger.info(
            f"[{request_id}] Started {request.method} {request.url.path} from {client_ip}"
        )

        try:
            response: Response = await call_next(request)

            process_time = time.time() - start_time
            logger.info(
                f"[{request_id}] Completed {response.status_code} in {process_time:.4f}s"
            )

            # Attach timing and trace headers to every response
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] Failed with {exc.__class__.__name__} in {process_time:.4f}s"
            )
            raise exc
