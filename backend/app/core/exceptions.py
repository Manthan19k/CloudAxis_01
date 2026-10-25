"""Application-level exceptions and FastAPI error handlers."""
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, status_code: int, detail: str, code: str = "error"):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.code = code


class UnauthorizedError(AppException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, "unauthorized")


class ForbiddenError(AppException):
    def __init__(self, detail: str = "Not permitted"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail, "forbidden")


class NotFoundError(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail, "not_found")


class ConflictError(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status.HTTP_409_CONFLICT, detail, "conflict")


class ValidationError(AppException):
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail, "validation_error")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": True, "code": exc.code, "detail": exc.detail, "path": request.url.path},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError):
        errors = []
        for err in exc.errors():
            loc = ".".join(str(p) for p in err["loc"] if p != "body")
            errors.append({"field": loc, "message": err["msg"]})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "code": "validation_error",
                "detail": "Validation failed",
                "errors": errors,
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "code": "internal_error", "detail": "Internal server error", "path": request.url.path},
        )