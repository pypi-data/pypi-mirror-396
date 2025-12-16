"""
Flask OpenAPI Documentation Package

A reusable package for generating comprehensive OpenAPI documentation 
with Flask-Pydantic-Spec, featuring custom metadata, security schemes,
and flexible configuration.

Author: Emmanuel Olowu
License: MIT
"""

from .core import FlaskOpenAPISpec, SecurityScheme, QueryParameter
from .config import DocsConfig, ContactInfo, SecuritySchemeConfig
from .responses import (
    ApiResp,
    SuccessResp,
    ErrorResp,
    CreatedResp,
    NoContentResp,
    BadRequestResp,
    UnauthorizedResp,
    ForbiddenResp,
    NotFoundResp,
    ConflictResp,
    InternalServerErrorResp,
)

__version__ = "0.0.9"
__author__ = "Emmanuel Olowu"

# Create a default instance for endpoint decorator export
_default_spec = FlaskOpenAPISpec(DocsConfig.create_default())
endpoint = _default_spec.endpoint

# Public API
__all__ = [
    "FlaskOpenAPISpec",
    "SecurityScheme",
    "QueryParameter",
    "endpoint",
    "DocsConfig",
    "ContactInfo",
    "SecuritySchemeConfig",
    # Base Response Schemas
    "ApiResp",
    "SuccessResp",
    "ErrorResp",
    "CreatedResp",
    "NoContentResp",
    "BadRequestResp",
    "UnauthorizedResp",
    "ForbiddenResp",
    "NotFoundResp",
    "ConflictResp",
    "InternalServerErrorResp",
]

