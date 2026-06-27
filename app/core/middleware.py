"""Request ID middleware for correlating log entries."""
import uuid
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog.contextvars

logger = structlog.get_logger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add a unique request ID to every request and bind it to the logger."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        
        with structlog.contextvars.bound_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        ):
            logger.info("request_started")
            response = await call_next(request)
            logger.info(
                "request_completed",
                status_code=response.status_code,
            )
        
        response.headers["X-Request-ID"] = request_id
        return response