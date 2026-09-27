class DomainError(Exception):
    error_code = "DOMAIN_ERROR"
    status_code = 400

    def __init__(self, message: str, details=None):
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class ValidationError(DomainError):
    status_code = 422


class ForbiddenError(DomainError):
    error_code = "FORBIDDEN_RESOURCE"
    status_code = 403


class UnauthorizedError(DomainError):
    status_code = 401
