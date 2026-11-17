from typing import Optional


class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationException(AppException):
    def __init__(self, message: str = "Invalid request parameters."):
        super().__init__(code="VALIDATION_ERROR", message=message, status_code=400)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Invalid or expired authentication token."):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(code="FORBIDDEN", message=message, status_code=403)


class NotFoundException(AppException):
    def __init__(self, message: str = "Requested resource not found."):
        super().__init__(code="NOT_FOUND", message=message, status_code=404)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource was modified by another request."):
        super().__init__(code="CONFLICT", message=message, status_code=409)


class InternalServerErrorException(AppException):
    def __init__(self, message: str = "An unexpected server error occurred."):
        super().__init__(code="INTERNAL_SERVER_ERROR", message=message, status_code=500)
