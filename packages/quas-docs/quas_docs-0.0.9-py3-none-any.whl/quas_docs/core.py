"""
Core functionality for Flask OpenAPI Documentation Package.

This module contains the main FlaskOpenAPISpec class and supporting utilities
for generating comprehensive OpenAPI documentation with custom metadata.
"""

from __future__ import annotations

import functools
import re
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Tuple

from flask import Flask
from flask_pydantic_spec import FlaskPydanticSpec
from pydantic import BaseModel

from .config import DocsConfig


class SecurityScheme(str, Enum):
    """Available security schemes for API endpoints."""
    PUBLIC_BEARER = "PublicBearerAuth"
    ADMIN_BEARER = "AdminBearerAuth"
    BEARER_AUTH = "BearerAuth"
    NONE = "none"


class QueryParameter:
    """Represents a query parameter definition."""
    def __init__(
        self,
        name: str,
        type_: str = "string",
        required: bool = False,
        description: Optional[str] = None,
        default: Any = None
    ):
        self.name = name
        self.type_ = type_
        self.required = required
        self.description = description or f"The {name} parameter"
        self.default = default


class EndpointMetadata:
    """Container for all endpoint metadata including request body, security, etc."""

    def __init__(
        self,
        request_body: Optional[Type[BaseModel]] = None,
        responses: Optional[Dict[Any, Any]] = None,
        security: Optional[SecurityScheme] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        deprecated: bool = False,
        query_params: Optional[List[QueryParameter]] = None,
        **extra_metadata: Any
    ):
        self.request_body = request_body
        self.responses = responses
        self.security = security
        self.tags = tags or []
        self.summary = summary
        self.description = description
        self.deprecated = deprecated
        self.query_params = query_params or []
        self.extra_metadata = extra_metadata


class FlaskOpenAPISpec:
    """
    Main class for Flask OpenAPI documentation generation.
    
    Provides a clean, configurable interface for generating comprehensive
    OpenAPI documentation with custom metadata, security schemes, and
    flexible configuration options.
    """
    
    def __init__(self, config: Optional[DocsConfig] = None):
        """
        Initialize the OpenAPI spec generator.
        
        Args:
            config: Configuration object. If None, creates default config.
        """
        self.config = config or DocsConfig.create_default()
        self.spec = FlaskPydanticSpec(
            'flask', 
            title=self.config.title, 
            version=self.config.version
        )
        self._registered_endpoints: List[Tuple[str, str, EndpointMetadata]] = []
    
    def init_app(self, app: Flask) -> None:
        """
        Initialize the OpenAPI documentation for a Flask application.
        
        Args:
            app: The Flask application instance to configure
        """
        # Extract our custom endpoints before registering the spec
        self._extract_decorated_endpoints(app)
        
        # Register the spec with the app
        self.spec.register(app)
        
        # Access the underlying OpenAPI spec object
        inner: Any = getattr(self.spec, 'spec', None)
        if inner is None:
            return
        
        # Clear auto-discovered paths to prevent duplicates if configured
        if self.config.clear_auto_discovered and isinstance(inner, dict) and 'paths' in inner:
            inner['paths'] = {}
        
        # Apply our customizations after spec registration
        self._setup_security_schemes(inner)
        self._setup_info_metadata(inner)
        self._setup_servers(inner)
        self._setup_external_docs(inner)
        
        # Apply our custom endpoint metadata
        self._apply_registered_endpoints(inner)
    
    def endpoint(
        self,
        request_body: Optional[Type[BaseModel]] = None,
        responses: Optional[Dict[Any, Any]] = None,
        security: Optional[SecurityScheme] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        deprecated: bool = False,
        query_params: Optional[List[QueryParameter]] = None,
        **extra_metadata: Any
    ) -> Callable:
        """
        Unified decorator for comprehensive endpoint documentation.
        
        Args:
            request_body: Pydantic model class for request body validation/documentation
            responses: Mapping of status codes to Pydantic models or {"model": ..., "description": ...}
            security: Security scheme required for this endpoint
            tags: List of tags for grouping endpoints in documentation
            summary: Brief summary of the endpoint functionality
            description: Detailed description of the endpoint
            deprecated: Whether this endpoint is deprecated
            **extra_metadata: Additional metadata for future extensibility
            
        Returns:
            Decorator function that preserves the original view function behavior
        """
        def decorator(func: Callable) -> Callable:
            # Create metadata object
            metadata = EndpointMetadata(
                request_body=request_body,
                responses=responses,
                security=security,
                tags=tags,
                summary=summary,
                description=description,
                deprecated=deprecated,
                query_params=query_params,
                **extra_metadata
            )
            
            # Attach metadata to function for later discovery
            func._endpoint_metadata = metadata  # type: ignore
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            # Ensure metadata is also attached to the wrapper
            wrapper._endpoint_metadata = metadata  # type: ignore
            return wrapper
        return decorator
    

    
    def _extract_decorated_endpoints(self, app: Flask) -> None:
        """Extract endpoint metadata from decorated view functions."""
        try:
            for rule in app.url_map.iter_rules():
                endpoint = rule.endpoint
                view_func = app.view_functions.get(endpoint)
                
                if not view_func:
                    continue
                
                metadata = None
                
                # Check for endpoint metadata
                if hasattr(view_func, '_endpoint_metadata'):
                    metadata = view_func._endpoint_metadata
                
                if metadata:
                    # Extract valid HTTP methods (exclude HEAD, OPTIONS)
                    methods = [m.lower() for m in rule.methods or set() 
                              if m.lower() not in ('head', 'options')]
                    
                    if not methods:
                        continue
                    
                    # Use the first valid method for documentation
                    method = methods[0]
                    
                    # Handle path format based on configuration
                    path = rule.rule
                    if not self.config.preserve_flask_routes:
                        # Convert Flask route format to OpenAPI format
                        # <string:param> -> {param}, <int:param> -> {param}, etc.
                        path = re.sub(r'<(?:\w+:)?(\w+)>', r'{\1}', path)
                    
                    # Try to extract response schemas from @spec.validate decorator
                    try:
                        if hasattr(view_func, '_spec_responses'):
                            responses = getattr(view_func, '_spec_responses', {})
                            if responses:
                                metadata.responses = responses
                    except Exception:
                        pass
                    
                    self._registered_endpoints.append((path, method, metadata))
        except Exception:
            # Silently continue - documentation generation should never break the app
            pass
    
    def _setup_security_schemes(self, inner: Any) -> None:
        """Configure security schemes from config."""
        security_schemes = self.config.to_openapi_security_schemes()
        
        if not security_schemes:
            return
        
        try:
            # Try flask-pydantic-spec's component interface first
            comps: Any = getattr(inner, 'components', None)
            if comps is not None and hasattr(comps, 'security_scheme'):
                for scheme_name, scheme_config in security_schemes.items():
                    getattr(comps, 'security_scheme')(scheme_name, scheme_config)
            # Fallback to direct dictionary manipulation
            elif isinstance(inner, dict):
                comp_dict = inner.setdefault('components', {})
                schemes = comp_dict.setdefault('securitySchemes', {})
                schemes.update(security_schemes)
        except Exception:
            # Silently fail to avoid breaking app initialization
            pass
    
    def _setup_info_metadata(self, inner: Any) -> None:
        """Configure API metadata from config."""
        info_data = self.config.to_openapi_info()
        
        try:
            # Attempt to access info object directly
            info_dict = getattr(inner, '_info', None)
            target = (info_dict if isinstance(info_dict, dict) 
                     else inner.setdefault('info', {}) if isinstance(inner, dict) 
                     else None)
            
            if target is not None:
                target.update(info_data)
        except Exception:
            # Silently fail to avoid breaking app initialization
            pass
    
    def _setup_servers(self, inner: Any) -> None:
        """Configure servers from config."""
        if not self.config.servers:
            return
        
        try:
            if isinstance(inner, dict):
                inner['servers'] = self.config.servers
        except Exception:
            pass
    
    def _setup_external_docs(self, inner: Any) -> None:
        """Configure external documentation from config."""
        external_docs = self.config.to_openapi_external_docs()
        if not external_docs:
            return
        
        try:
            if isinstance(inner, dict):
                inner['externalDocs'] = external_docs
        except Exception:
            pass
    
    def _apply_registered_endpoints(self, inner: Any) -> None:
        """Apply all endpoint metadata to OpenAPI spec."""
        if not self._registered_endpoints:
            return

        # Initialize wrapped schemas dict before building responses
        if not hasattr(self, '_wrapped_schemas'):
            self._wrapped_schemas: Dict[str, Dict[str, Any]] = {}

        # Collect unique models for schema registration and build responses
        models_to_register = set()
        normalized_responses_cache: Dict[Tuple[str, str], Dict[str, Any]] = {}
        
        # First pass: build all responses to create wrapped schemas and collect models
        for path, method, metadata in self._registered_endpoints:
            if metadata.request_body:
                models_to_register.add(metadata.request_body)
            if metadata.responses:
                models_to_register.update(self._extract_models_from_responses(metadata.responses))
                # Build responses spec which creates wrapped schemas
                raw_responses = metadata.responses or metadata.extra_metadata.get('responses', None)
                if raw_responses:
                    normalized_responses = self._build_responses_spec(raw_responses)
                    normalized_responses_cache[(path, method)] = normalized_responses

        # Register Pydantic model schemas in components/schemas section
        if models_to_register:
            try:
                comps: Any = getattr(inner, 'components', None)
                if comps is not None and hasattr(comps, 'schema'):
                    # Use flask-pydantic-spec's schema registration method
                    for model in models_to_register:
                        comps.schema(model.__name__, model.model_json_schema())
                elif isinstance(inner, dict):
                    # Direct dictionary manipulation fallback
                    schemas = inner.setdefault('components', {}).setdefault('schemas', {})
                    for model in models_to_register:
                        schemas[model.__name__] = model.model_json_schema()
            except Exception:
                # Continue even if schema registration fails
                pass
        
        # Register wrapped response schemas (now they exist after building responses)
        if hasattr(self, '_wrapped_schemas') and self._wrapped_schemas:
            try:
                comps: Any = getattr(inner, 'components', None)
                if comps is not None and hasattr(comps, 'schema'):
                    # Use flask-pydantic-spec's schema registration method
                    for name, schema in self._wrapped_schemas.items():
                        comps.schema(name, schema)
                elif isinstance(inner, dict):
                    # Direct dictionary manipulation fallback
                    schemas = inner.setdefault('components', {}).setdefault('schemas', {})
                    schemas.update(self._wrapped_schemas)
            except Exception:
                # Continue even if schema registration fails
                pass

        # Apply all metadata to each registered endpoint
        for path, method, metadata in self._registered_endpoints:
            operation_spec = {}
            # Use cached normalized responses if available, otherwise build them
            normalized_responses = normalized_responses_cache.get(
                (path, method),
                self._build_responses_spec(metadata.responses or metadata.extra_metadata.pop('responses', None))
            )
            
            # Initialize parameters list
            operation_spec['parameters'] = []

            # Extract path parameters and add them to the spec
            import re
            path_params = re.findall(r'\{(\w+)\}', path)
            for param_name in path_params:
                operation_spec['parameters'].append({
                    'name': param_name,
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'string'},
                    'description': f'The {param_name} parameter'
                })

            # Add query parameters from metadata
            for query_param in metadata.query_params:
                operation_spec['parameters'].append({
                    'name': query_param.name,
                    'in': 'query',
                    'required': query_param.required,
                    'schema': {'type': query_param.type_},
                    'description': query_param.description,
                    **({'default': query_param.default} if query_param.default is not None else {})
                })
            
            # Add request body if specified
            if metadata.request_body:
                operation_spec['requestBody'] = {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {'$ref': f"#/components/schemas/{metadata.request_body.__name__}"}
                        }
                    }
                }
            
            # Add security requirements if specified
            if metadata.security and metadata.security != SecurityScheme.NONE:
                operation_spec['security'] = [{metadata.security.value: []}]

            # Add normalized responses if present
            if normalized_responses:
                operation_spec['responses'] = normalized_responses
            
            # Add tags, summary, description, etc.
            if metadata.tags:
                operation_spec['tags'] = metadata.tags
            if metadata.summary:
                operation_spec['summary'] = metadata.summary
            if metadata.description:
                operation_spec['description'] = metadata.description
            if metadata.deprecated:
                operation_spec['deprecated'] = True
            
            # Add any extra metadata
            operation_spec.update(metadata.extra_metadata)
            
            # Apply the operation spec to the OpenAPI spec
            if operation_spec:
                # Direct dictionary manipulation for reliable metadata application
                if isinstance(inner, dict):
                    # Get or create the path and method
                    if path not in inner.setdefault('paths', {}):
                        inner['paths'][path] = {}
                    if method not in inner['paths'][path]:
                        inner['paths'][path][method] = {}
                    
                    ops = inner['paths'][path][method]
                    
                    # Apply our custom metadata (this will override defaults)
                    for key, value in operation_spec.items():
                        if key == 'responses' and 'responses' in ops:
                            # Merge responses instead of overwriting
                            ops['responses'].update(value)
                        else:
                            ops[key] = value
                    
                    # Add default response schemas if configured and not already present
                    if self.config.add_default_responses:
                        if 'responses' not in ops:
                            ops['responses'] = {}
                        
                        if '200' not in ops['responses']:
                            ops['responses']['200'] = {
                                'description': 'Success',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'status': {'type': 'string', 'enum': ['success']},
                                                'status_code': {'type': 'integer'},
                                                'message': {'type': 'string'},
                                                'data': {'type': 'object'}
                                            }
                                        }
                                    }
                                }
                            }
                        if '400' not in ops['responses']:
                            ops['responses']['400'] = {
                                'description': 'Bad Request',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'status': {'type': 'string', 'enum': ['failed']},
                                                'status_code': {'type': 'integer'},
                                                'message': {'type': 'string'},
                                                'data': {'type': 'object'}
                                            }
                                        }
                                    }
                                }
                            }

    def _extract_models_from_responses(self, responses: Dict[Any, Any]) -> List[Type[BaseModel]]:
        """Collect Pydantic models from response definitions for schema registration."""
        models: List[Type[BaseModel]] = []
        if not responses:
            return models
        for resp in responses.values():
            model = None
            if isinstance(resp, dict):
                model = resp.get('model') or resp.get('schema')
            elif isinstance(resp, (list, tuple)) and resp:
                model = resp[0]
            else:
                model = resp

            if isinstance(model, type) and issubclass(model, BaseModel):
                models.append(model)
        return models

    def _build_responses_spec(self, responses: Optional[Dict[Any, Any]]) -> Dict[str, Any]:
        """
        Normalize responses into OpenAPI response objects.
        
        If use_response_wrapper is enabled, wraps user data models in base response schemas.
        
        Accepts either:
        - Dict[str|int, BaseModel or {model, description}] 
        - Output of flask-pydantic-spec's @spec.validate (HTTP_200 keys)
        """
        if not responses:
            return {}

        result: Dict[str, Any] = {}
        
        # Initialize wrapped schemas dict if not exists
        if not hasattr(self, '_wrapped_schemas'):
            self._wrapped_schemas: Dict[str, Dict[str, Any]] = {}

        def coerce_status(key: Any) -> Optional[str]:
            if isinstance(key, int):
                return str(key)
            if isinstance(key, str):
                import re
                m = re.match(r"HTTP_(\d{3})", key)
                if m:
                    return m.group(1)
                if key.isdigit():
                    return key
            return None

        def build_response(
            model: Optional[Type[BaseModel]], 
            description: Optional[str],
            status_code: int
        ) -> Dict[str, Any]:
            resp: Dict[str, Any] = {
                "description": description or "",
            }
            
            if model and isinstance(model, type) and issubclass(model, BaseModel):
                if self.config.use_response_wrapper:
                    # Wrap the data model in base response schema
                    wrapped_schema = self._build_wrapped_response_schema(status_code, model)
                    wrapped_name = f"{model.__name__}Response"
                    
                    # Store wrapped schema for later registration
                    self._wrapped_schemas[wrapped_name] = wrapped_schema
                    
                    resp["content"] = {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{wrapped_name}"}
                        }
                    }
                else:
                    # Direct model reference (no wrapping)
                    resp["content"] = {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{model.__name__}"}
                        }
                    }
            
            return resp

        for key, value in responses.items():
            status = coerce_status(key)
            if not status:
                continue

            status_code = int(status)
            model: Optional[Type[BaseModel]] = None
            description: Optional[str] = None

            if isinstance(value, dict):
                model = value.get("model") or value.get("schema")
                description = value.get("description")
            elif isinstance(value, (list, tuple)):
                if value:
                    model = value[0] if isinstance(value[0], type) else None
                if len(value) > 1 and isinstance(value[1], str):
                    description = value[1]
            else:
                model = value if isinstance(value, type) else None

            result[status] = build_response(model, description, status_code)

        return result
    
    def _build_wrapped_response_schema(
        self, 
        status_code: int, 
        data_model: Type[BaseModel]
    ) -> Dict[str, Any]:
        """
        Build a wrapped response schema combining base response with data model.
        
        Args:
            status_code: HTTP status code
            data_model: User's data model to wrap
            
        Returns:
            Combined schema JSON structure
        """
        # Get the base response schema for this status code
        base_schema_class = self.config._get_response_schema_for_status(status_code)
        
        # Get the base response schema JSON
        base_schema = base_schema_class.model_json_schema()
        
        # Create a deep copy to modify (use dict() constructor for shallow copy, but we need to modify nested dicts)
        import copy
        wrapped_schema = copy.deepcopy(base_schema)
        
        # Replace the 'data' field with a reference to the data model
        if 'properties' in wrapped_schema and 'data' in wrapped_schema['properties']:
            # Completely replace the data field definition with a reference
            wrapped_schema['properties']['data'] = {
                '$ref': f"#/components/schemas/{data_model.__name__}"
            }
            
            # Ensure data is required
            if 'required' not in wrapped_schema:
                wrapped_schema['required'] = []
            if 'data' not in wrapped_schema['required']:
                wrapped_schema['required'].append('data')
        else:
            # If data field doesn't exist, add it
            if 'properties' not in wrapped_schema:
                wrapped_schema['properties'] = {}
            wrapped_schema['properties']['data'] = {
                '$ref': f"#/components/schemas/{data_model.__name__}"
            }
            if 'required' not in wrapped_schema:
                wrapped_schema['required'] = []
            wrapped_schema['required'].append('data')
        
        return wrapped_schema
