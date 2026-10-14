from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.core.logging import get_logger
import time
import uuid
import structlog
from fastapi.encoders import jsonable_encoder

logger = get_logger(__name__)


class WorkshopUploadLimitMiddleware:
    """Bound streamed multipart input before the parser can spool large files."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("method") != "POST" or not (scope.get("path", "").rstrip("/").endswith("/workshop/documents") or scope.get("path", "").startswith("/assistant/")):
            return await self.app(scope, receive, send)
        received, messages = 0, []
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            received += len(message.get("body", b""))
            if received > 8 * 1024 * 1024 + 64 * 1024:
                response = JSONResponse(status_code=413, content={"detail": "Workshop upload request exceeds 8 MiB plus form overhead"})
                return await response(scope, receive, send)
            messages.append(message)
            if not message.get("more_body", False):
                break
        iterator = iter(messages)
        async def replay_receive():
            return next(iterator, None) or await receive()
        await self.app(scope, replay_receive, send)


async def error_handling_middleware(request: Request, call_next):
    """Global error handling middleware"""
    start_time = time.time()
    request_id = uuid.uuid4().hex
    structlog.contextvars.bind_contextvars(request_id=request_id)

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log request
        logger.info(
            "request_processed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=f"{process_time:.3f}s",
        )

        response.headers["X-Request-ID"] = request_id
        return response

    except Exception as exc:
        process_time = time.time() - start_time

        logger.error(
            "request_error",
            method=request.method,
            path=request.url.path,
            error_type=type(exc).__name__,
            process_time=f"{process_time:.3f}s",
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"X-Request-ID": request_id, "Cache-Control": "no-store"},
            content={
                "success": False,
                "error": "Internal server error",
                "detail": "An unexpected error occurred",
            },
        )

    finally:
        structlog.contextvars.clear_contextvars()


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(
        "validation_error",
        method=request.method,
        path=request.url.path,
        error_count=len(exc.errors()),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "detail": jsonable_encoder(exc.errors()),
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(
        "http_exception",
        method=request.method,
        path=request.url.path,
        status_code=exc.status_code,
        detail=exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "detail": exc.detail,
        },
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(
        "database_error",
        method=request.method,
        path=request.url.path,
        error_type=type(exc).__name__,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Database error",
            "detail": "An error occurred while accessing the database",
        },
    )
