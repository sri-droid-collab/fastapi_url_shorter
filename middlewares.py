import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        # Attach request_id to request state so it can be used in exception handlers or routes
        request.state.request_id = request_id
        
        start_time = time.time()
        
        client_ip = request.client.host if request.client else "Unknown"
        logger.info(f"[{request_id}] Started {request.method} {request.url.path} from {client_ip}")
        
        try:
            response: Response = await call_next(request)
            
            process_time = time.time() - start_time
            # Safely get response phrase if available
            phrase = hasattr(response, 'phrase') and response.phrase or ""
            logger.info(
                f"[{request_id}] Completed {response.status_code} {phrase} "
                f"in {process_time:.4f}s"
            )
            
            # Add custom internal headers to response
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] Failed with exception {e.__class__.__name__} "
                f"in {process_time:.4f}s"
            )
            raise e
