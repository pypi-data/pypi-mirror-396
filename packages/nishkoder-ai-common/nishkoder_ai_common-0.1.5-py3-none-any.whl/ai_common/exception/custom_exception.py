from typing import Any, Dict, Optional

from ai_common.logger.custom_logger import logger
from ai_common.logger.logger_utils import add_context


class AppException(Exception):
    """Base exception for the Application."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize exception to dictionary."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }

    def log_error(self, custom_logger=None):
        """Log the exception details with context."""
        log = custom_logger or logger
        context_data = {
            "error_code": self.code,
            "status_code": self.status_code,
            "error_details": self.details,
        }
        ctx_logger = add_context(log, **context_data)
        ctx_logger.error(self.message)


class ResourceNotFoundException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, code="RESOURCE_NOT_FOUND", status_code=404, details=details
        )


class ValidationException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, code="VALIDATION_ERROR", status_code=400, details=details
        )


class AuthenticationException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=401,
            details=details,
        )


class PermissionDeniedException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, code="PERMISSION_DENIED", status_code=403, details=details
        )


class DatabaseException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, code="DATABASE_ERROR", status_code=500, details=details
        )


class ConfigException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
            details=details,
        )


class ModelException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, code="MODEL_ERROR", status_code=500, details=details
        )
