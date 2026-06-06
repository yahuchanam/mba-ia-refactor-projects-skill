"""Application error hierarchy mapped to HTTP status codes by the central handler."""


class AppError(Exception):
    """Base class for expected, client-facing errors."""

    status = 400

    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status is not None:
            self.status = status


class ValidationError(AppError):
    status = 400


class NotFoundError(AppError):
    status = 404


class AuthError(AppError):
    status = 401

    def __init__(
        self, message: str = "Autenticação necessária", status: int = 401
    ) -> None:
        super().__init__(message, status)
