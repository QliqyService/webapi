from typing import Any

from fastapi.exceptions import HTTPException
from starlette import status


class BaseHTTPException(HTTPException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Internal server error."

    def __init__(self, message: str | None = None, meta: Any | None = None):
        meta = f": {meta}" if meta is not None else ""
        super().__init__(
            status_code=self.status_code,
            detail=f"{message or self.message}{meta}",
        )


class InternalServerErrorException(BaseHTTPException):
    pass


class ObjectAlreadyExistsException(BaseHTTPException):
    status_code: int = status.HTTP_409_CONFLICT
    message: str = "Object already exists."


class RequestedDataNotFoundException(BaseHTTPException):
    status_code: int = status.HTTP_404_NOT_FOUND
    message: str = "Requested data was not found."


class InvalidCredentialsException(BaseHTTPException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Make sure that the input data are correct."


class UnauthorizedUserException(BaseHTTPException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Unauthorized user."


class PermissionDeniedException(BaseHTTPException):
    status_code: int = status.HTTP_403_FORBIDDEN
    message: str = "Permission denied."


class FileWorkflowException(BaseHTTPException):
    status_code: int = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    message: str = "File workflow error."


class UnprocessableEntityException(BaseHTTPException):
    status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    message: str = "Unprocessable entity."


class ValidationException(BaseHTTPException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    message: str = "Validation error."
