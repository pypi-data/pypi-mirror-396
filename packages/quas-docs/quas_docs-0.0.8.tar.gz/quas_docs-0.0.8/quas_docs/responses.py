"""
Base response schemas for API documentation.

Provides canonical response envelope schemas that wrap all API responses
in a consistent format with status, status_code, message, and data fields.
"""

from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel


class ApiResp(BaseModel):
    """Canonical API response envelope."""
    status: Literal['success', 'failed']
    status_code: int
    message: str
    data: Optional[Dict[str, Any]] = {}


class SuccessResp(ApiResp):
    """Success response schema."""
    status: Literal['success'] = 'success'
    status_code: int = 200


class CreatedResp(SuccessResp):
    """Created response schema."""
    status_code: int = 201


class NoContentResp(SuccessResp):
    """No content response schema."""
    status_code: int = 204


class ErrorResp(ApiResp):
    """Error response schema."""
    status: Literal['failed'] = 'failed'
    errors: Optional[List[str]] = None
    status_code: int = 400


class BadRequestResp(ErrorResp):
    """Bad request response schema."""
    status_code: int = 400


class UnauthorizedResp(ErrorResp):
    """Unauthorized response schema."""
    status_code: int = 401


class ForbiddenResp(ErrorResp):
    """Forbidden response schema."""
    status_code: int = 403


class NotFoundResp(ErrorResp):
    """Not found response schema."""
    status_code: int = 404


class ConflictResp(ErrorResp):
    """Conflict response schema."""
    status_code: int = 409


class InternalServerErrorResp(ErrorResp):
    """Internal server error response schema."""
    status_code: int = 500


# Default mapping of status codes to base response types
DEFAULT_STATUS_CODE_MAP: Dict[int, type] = {
    200: SuccessResp,
    201: CreatedResp,
    204: NoContentResp,
    400: BadRequestResp,
    401: UnauthorizedResp,
    403: ForbiddenResp,
    404: NotFoundResp,
    409: ConflictResp,
    500: InternalServerErrorResp,
}

