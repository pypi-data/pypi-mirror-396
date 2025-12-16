# Flask OpenAPI Documentation Package

A powerful, reusable package for generating comprehensive OpenAPI documentation with Flask-Pydantic-Spec. Features custom metadata, security schemes, and flexible configuration options.

## ✨ Features

- **Flexible Configuration**: Easy-to-use configuration system for API metadata
- **Custom Security Schemes**: Support for multiple authentication types
- **Tag-based Organization**: Group endpoints by functionality
- **Route Format Control**: Choose between Flask (`<string:param>`) and OpenAPI (`{param}`) formats
- **Automatic Schema Registration**: Seamless Pydantic model integration
- **Backward Compatibility**: Drop-in replacement for existing setups
- **Base Response Schemas**: Automatic canonical response envelope wrapping with customizable base schemas

## 🚀 Quick Start

### Basic Usage

```python
from flask import Flask
from pydantic import BaseModel
from quas_docs import FlaskOpenAPISpec, DocsConfig, ContactInfo, SecurityScheme, endpoint

# Define your data models (these will be wrapped in base response schemas)
class UserData(BaseModel):
    id: int
    username: str
    email: str

class ErrorData(BaseModel):
    error_code: str
    error_message: str

# Create configuration
config = DocsConfig(
    title="My API",
    version="0.0.9",
    description="A sample API with comprehensive documentation",
    contact=ContactInfo(
        email="api@example.com",
        name="API Team"
    )
)

# Initialize the spec
spec = FlaskOpenAPISpec(config)

# Create Flask app
app = Flask(__name__)

# Add endpoints with metadata and response data models
# Note: By default, data models are automatically wrapped in base response schemas
@app.post("/users")
@endpoint(
    request_body=CreateUserRequest,
    responses={"200": UserData, "400": ErrorData},
    security=SecurityScheme.BEARER_AUTH,
    tags=["Users"],
    summary="Create New User",
    description="Creates a new user account with validation"
)
def create_user():
    return {"message": "User created"}

# Initialize documentation
spec.init_app(app)
```

### Dynamic Configuration Methods

```python
from quas_docs import FlaskOpenAPISpec, DocsConfig

# Method 1: From dictionary (recommended)
config = DocsConfig.from_dict({
    'title': 'My API',
    'version': '2.0.0',
    'description': 'API built with dynamic configuration',
    'contact': {
        'email': 'dev@mycompany.com',
        'name': 'Development Team',
        'url': 'https://mycompany.com'
    },
    'security_schemes': {
        'BearerAuth': {'description': 'JWT authentication'},
        'ApiKeyAuth': {
            'scheme_type': 'apiKey',
            'location': 'header',
            'parameter_name': 'X-API-Key',
            'description': 'API key authentication'
        }
    },
    'preserve_flask_routes': True
})

# Method 2: From environment variables
config = DocsConfig.from_env(prefix="MY_API_")

# Method 3: Create default and customize
config = DocsConfig.create_default()
config.title = "Custom API"
config.version = "2.0.0"

# Method 4: Manual construction
config = DocsConfig(
    title="Custom API",
    version="2.0.0",
    description="Custom API with specific requirements"
)
```

## 📋 Configuration Options

### DocsConfig Class

```python
@dataclass
class DocsConfig:
    # Basic API Information
    title: str = "Flask API"
    version: str = "0.0.9"
    description: Optional[str] = None
    terms_of_service: Optional[str] = None
    
    # Contact Information
    contact: Optional[ContactInfo] = None
    
    # License Information
    license_name: Optional[str] = None
    license_url: Optional[str] = None
    
    # Server Information
    servers: List[Dict[str, str]] = field(default_factory=list)
    
    # Security Schemes
    security_schemes: Dict[str, SecuritySchemeConfig] = field(default_factory=dict)
    
    # Customization Options
    preserve_flask_routes: bool = True  # Keep <string:param> format
    clear_auto_discovered: bool = True  # Remove auto-discovered duplicates
    add_default_responses: bool = True  # Add default response schemas
    
    # Response Schema Configuration
    custom_response_schemas: Dict[int, Type[BaseModel]] = field(default_factory=dict)  # Custom base response schemas
    use_response_wrapper: bool = True  # Enable automatic response wrapping (default: True)
    
    # External Documentation
    external_docs_url: Optional[str] = None
    external_docs_description: Optional[str] = None
```

### Security Schemes

```python
from quas_docs import SecuritySchemeConfig

# API Key Authentication
api_key_config = SecuritySchemeConfig(
    name="ApiKeyAuth",
    scheme_type="apiKey",
    location="header",
    parameter_name="X-API-Key",
    description="API key authentication"
)

# Bearer Token Authentication
bearer_config = SecuritySchemeConfig(
    name="BearerAuth",
    scheme_type="apiKey",
    location="header", 
    parameter_name="Authorization",
    description="JWT Bearer token authentication"
)

# Add to configuration
config.add_security_scheme("ApiKeyAuth", api_key_config)
config.add_security_scheme("BearerAuth", bearer_config)
```

### Contact Information

```python
from quas_docs import ContactInfo

contact = ContactInfo(
    email="api@example.com",
    name="API Development Team",
    url="https://example.com/contact"
)

config.contact = contact
```

## 🎯 Endpoint Decoration

### The @endpoint Decorator

```python
@endpoint(
    request_body=Optional[Type[BaseModel]],      # Pydantic model for request body
    responses=Optional[Dict[str|int, Type[BaseModel]]],  # Response schemas by status code
    security=Optional[SecurityScheme],           # Security requirement
    tags=Optional[List[str]],                    # Organization tags
    summary=Optional[str],                       # Brief description
    description=Optional[str],                   # Detailed description
    query_params=Optional[List[QueryParameter]], # Query parameters for GET endpoints
    deprecated=bool,                             # Mark as deprecated
    **extra_metadata                             # Custom metadata
)
```

### Examples

```python
from pydantic import BaseModel

# Define your data models
class LoginData(BaseModel):
    access_token: str
    user_id: str

class ErrorData(BaseModel):
    error_code: str
    error_message: str

# Basic endpoint with request body and responses
# Data models are automatically wrapped in base response schemas
@app.post("/auth/login")
@endpoint(
    request_body=LoginRequest,
    responses={"200": LoginData, "400": ErrorData, "401": ErrorData},
    tags=["Authentication"],
    summary="User Login",
    description="Authenticate user with email and password"
)
def login():
    return AuthController.login()

# Secured endpoint with query parameters
@app.get("/users")
@endpoint(
    responses={"200": UsersListData},  # Preferred: use responses parameter
    security=SecurityScheme.BEARER_AUTH,
    tags=["Users"],
    summary="List Users",
    description="Get paginated list of users with filtering options",
    query_params=[
        QueryParameter("page", "integer", required=False, description="Page number", default=1),
        QueryParameter("per_page", "integer", required=False, description="Items per page", default=10),
        QueryParameter("search", "string", required=False, description="Search by name or email"),
        QueryParameter("active", "boolean", required=False, description="Filter by active status", default=True),
    ]
)
def list_users():
    return UserController.list()

# Note: @spec.validate is still supported for backward compatibility,
# but using the responses parameter in @endpoint is the recommended approach

# Public endpoint with custom metadata
@app.get("/health")
@endpoint(
    tags=["System"],
    summary="Health Check",
    description="Check API health status",
    custom_field="health-check"  # Custom metadata
)
def health_check():
    return {"status": "healthy"}
```

## 🔧 Advanced Configuration

### Base Response Schemas

The package provides a canonical response envelope system that automatically wraps your endpoint data models in consistent base response schemas. This ensures all API responses follow a standard format with `status`, `status_code`, `message`, and `data` fields.

#### Default Base Response Schemas

The package includes default base response schemas for common HTTP status codes:

- `SuccessResp` (200) - Standard success response
- `CreatedResp` (201) - Resource created
- `NoContentResp` (204) - No content
- `BadRequestResp` (400) - Bad request
- `UnauthorizedResp` (401) - Unauthorized
- `ForbiddenResp` (403) - Forbidden
- `NotFoundResp` (404) - Not found
- `ConflictResp` (409) - Conflict
- `InternalServerErrorResp` (500) - Server error

#### Using Default Base Response Schemas

**Important**: Response wrapping is enabled by default (`use_response_wrapper=True`). When you specify data models in the `responses` parameter, they are automatically wrapped in the appropriate base response schema based on the status code.

Simply specify your data models in the `responses` parameter:

```python
from quas_docs import FlaskOpenAPISpec, DocsConfig, endpoint
from pydantic import BaseModel

class LoginData(BaseModel):
    access_token: str
    user_id: str
    access_data: dict

class ErrorData(BaseModel):
    error_code: str
    error_message: str

config = DocsConfig(
    title="My API",
    version="0.0.9",
    use_response_wrapper=True  # Enabled by default
)

spec = FlaskOpenAPISpec(config)

@app.post("/login")
@endpoint(
    request_body=LoginRequest,
    responses={"200": LoginData, "400": ErrorData, "401": ErrorData},
    tags=["Authentication"]
)
def login():
    return {...}
```

This will generate response schemas where:
- `200` responses wrap `LoginData` in `SuccessResp` with `LoginData` as the `data` field
- `400` and `401` responses wrap `ErrorData` in `BadRequestResp` and `UnauthorizedResp` respectively

The resulting response structure:
```json
{
  "status": "success",
  "status_code": 200,
  "message": "string",
  "data": {
    "access_token": "",
    "user_id": "",
    "access_data": {}
  }
}
```

#### Custom Base Response Schemas

You can define your own base response schemas that override the defaults for specific status codes. **Important**: Custom schemas must have a `data` field in their schema definition, but they don't need to inherit from the default schemas - they can be completely independent Pydantic models.

```python
from pydantic import BaseModel
from quas_docs import DocsConfig

# Define custom base response schema
class MyCustomSuccessResp(BaseModel):
    status: str = "success"
    status_code: int = 200
    message: str
    data: dict  # Required field

class MyCustomErrorResp(BaseModel):
    status: str = "error"
    code: int = 400
    message: str
    errors: list = []
    data: dict  # Required field

# Register custom schemas
config = DocsConfig(title="My API", version="0.0.9")
config.add_custom_response_schema(200, MyCustomSuccessResp)
config.add_custom_response_schema(400, MyCustomErrorResp)

# Use in endpoints - custom schema used for 200/400, default for 401
@app.post("/login")
@endpoint(
    responses={"200": LoginData, "400": ErrorData, "401": ErrorData}
)
def login():
    ...
```

**Mixed Usage**: If you define custom schemas for some status codes but not others, the package automatically falls back to defaults for undefined status codes. For example, if you define custom schemas for `200` and `400`, but an endpoint uses `401`, the default `UnauthorizedResp` will be used.

#### Disabling Response Wrapping

To disable response wrapping globally:

```python
config = DocsConfig(
    title="My API",
    version="0.0.9",
    use_response_wrapper=False  # Disable wrapping
)
```

When disabled, data models are used directly without base response envelopes.

### Modeling nested responses (avoiding `additionalProp1`)
- `additionalProp1` (or `additionalProperties`) shows up when a field is a free-form `dict`/`Dict[str, Any]`. Swagger can't infer keys, so it renders placeholders.
- Prefer typed nested models for clearer docs. Example:
```python
class Product(BaseModel):
    id: int
    name: str
    price: float
    currency: str

class ProductListData(BaseModel):
    products: list[Product]
    total: int
    page: int
    per_page: int
    total_pages: int
```
- If you truly need arbitrary dicts, add examples to make the docs usable:
```python
class CheckoutData(BaseModel):
    order: dict[str, Any] = Field(
        ...,
        examples=[{"id": 123, "status": "paid", "meta": {"channel": "web"}}],
        description="Free-form order data",
    )
```
- Example with nested models and examples:
```python
class OrderItem(BaseModel):
    sku: str
    quantity: int
    price: float

class Order(BaseModel):
    id: int
    total: float
    currency: str
    items: list[OrderItem]

class CheckoutData(BaseModel):
    order: Order = Field(..., examples=[{
        "id": 123,
        "total": 199.99,
        "currency": "NGN",
        "items": [{"sku": "ABC123", "quantity": 2, "price": 99.99}],
    }])
```


### Using @spec.validate (Legacy/Backward Compatibility)

The `@spec.validate` decorator from `flask-pydantic-spec` is still supported for backward compatibility, but using the `responses` parameter in `@endpoint` is the recommended approach:

```python
# Recommended: Use responses parameter in @endpoint
@app.post("/users")
@endpoint(
    tags=["Users"],
    responses={"201": UserData, "400": ErrorData, "409": ErrorData}
)
def create_user():
    return UserController.create()

# Legacy: Using @spec.validate (still works but not recommended)
@app.post("/users")
@endpoint(tags=["Users"])
@spec.validate(resp=Response(
    HTTP_201=CreateUserResponse,
    HTTP_400=ErrorResponse,
    HTTP_409=ConflictResponse
))
def create_user():
    return UserController.create()

# Note: You can disable automatic default response schemas if needed:
config.add_default_responses = False
```

### Route Format Control

```python
# Keep Flask format: /users/<string:user_id>
config.preserve_flask_routes = True

# Use OpenAPI format: /users/{user_id}  
config.preserve_flask_routes = False
```

### Servers Configuration

```python
# Add multiple servers
config.add_server("https://api.example.com", "Production")
config.add_server("https://staging-api.example.com", "Staging")
config.add_server("http://localhost:5000", "Development")
```

### External Documentation

```python
config.external_docs_url = "https://docs.example.com"
config.external_docs_description = "Complete API Documentation"
```

### Environment Variable Configuration

Set environment variables and load them automatically:

```bash
# .env file or environment
export API_TITLE="My Project API"
export API_VERSION="1.2.0"
export API_DESCRIPTION="API for my awesome project"
export API_CONTACT_EMAIL="api@myproject.com"
export API_CONTACT_NAME="API Team"
export API_CONTACT_URL="https://myproject.com/contact"
export API_LICENSE_NAME="MIT"
export API_PRESERVE_FLASK_ROUTES="true"
```

```python
# Load configuration from environment
config = DocsConfig.from_env()  # Uses API_ prefix by default

# Or use custom prefix
config = DocsConfig.from_env(prefix="MYAPI_")
```

## 📦 Integration Examples

### Replace Existing Setup

If you have an existing Flask app with manual OpenAPI setup:

```python
# OLD WAY
from flask_pydantic_spec import FlaskPydanticSpec
spec = FlaskPydanticSpec('flask', title='My API', version='0.0.9')

# NEW WAY
from quas_docs import FlaskOpenAPISpec, DocsConfig
config = DocsConfig(title='My API', version='0.0.9')
spec_instance = FlaskOpenAPISpec(config)
spec = spec_instance.spec  # For backward compatibility with @spec.validate
```

### Multiple APIs

```python
# API 1: Public API
public_config = DocsConfig(
    title="Public API",
    version="0.0.9",
    preserve_flask_routes=True
)
public_spec = FlaskOpenAPISpec(public_config)

# API 2: Admin API  
admin_config = DocsConfig(
    title="Admin API",
    version="0.0.9",
    preserve_flask_routes=False
)
admin_spec = FlaskOpenAPISpec(admin_config)
```

### Custom Project Setup

```python
# projects/my_project/docs_config.py
from quas_docs import DocsConfig, ContactInfo, SecuritySchemeConfig

def create_my_project_config():
    config = DocsConfig(
        title="My Project API",
        version="2.1.0",
        description="Custom project with specific requirements",
        contact=ContactInfo(
            email="dev@myproject.com",
            name="Development Team",
            url="https://myproject.com"
        )
    )
    
    # Add custom security schemes
    config.add_security_scheme("ApiKey", SecuritySchemeConfig(
        name="ApiKey",
        parameter_name="X-API-Key",
        description="Project-specific API key"
    ))
    
    config.add_server("https://api.myproject.com", "Production")
    config.add_server("http://localhost:8000", "Development")
    
    return config

# projects/my_project/app.py
from quas_docs import FlaskOpenAPISpec
from .docs_config import create_my_project_config

config = create_my_project_config()
spec = FlaskOpenAPISpec(config)
```

## 🔄 Migration Guide

### From Manual Setup

1. **Copy the docs/ folder** to your project
2. **Replace your existing docs setup**:
   ```python
   # Replace your old setup with:
   from quas_docs import FlaskOpenAPISpec, DocsConfig, endpoint, SecurityScheme
   
   config = DocsConfig.from_dict({
       'title': 'Your API Name',
       'version': '0.0.9',
       # ... your settings
   })
   spec_instance = FlaskOpenAPISpec(config)
   spec = spec_instance.spec  # For @spec.validate decorators
   ```
3. **Use the @endpoint decorator**:
   ```python
   @endpoint(
       request_body=YourModel,
       security=SecurityScheme.BEARER_AUTH,
       tags=["Your Tag"],
       summary="Your Summary"
   )
   ```
4. **Initialize documentation**:
   ```python
   spec_instance.init_app(app)
   ```

### Clean v1.0 Design

The package follows a clean, modern approach:

- Single `@endpoint` decorator for all metadata
- Configuration-driven setup
- No legacy compatibility code
- Streamlined API surface

## 📝 Best Practices

1. **Use meaningful tags** to organize endpoints logically
2. **Provide clear summaries and descriptions** for better developer experience
3. **Configure contact information** for API support
4. **Use appropriate security schemes** for different endpoint types
5. **Test documentation** in both Swagger UI and Redoc
6. **Version your APIs** properly using semantic versioning

## 🐛 Troubleshooting

### Common Issues

**Issue**: Endpoints appear in "default" category
**Solution**: Ensure `clear_auto_discovered = True` in config

**Issue**: Route parameters show wrong format
**Solution**: Set `preserve_flask_routes` in config

**Issue**: Security schemes not working
**Solution**: Verify security scheme names match those in config

**Issue**: Missing response schemas
**Solution**: Check `add_default_responses` setting. Use the `responses` parameter in `@endpoint` decorator to specify response data models.

**Issue**: Response wrapping not working
**Solution**: Ensure `use_response_wrapper=True` in config (enabled by default). Data models specified in `responses` are automatically wrapped in base response schemas.

**Issue**: Custom base response schema validation error
**Solution**: Ensure your custom schema has a `data` field. Use `config.add_custom_response_schema(status_code, schema)` to register custom schemas.

## 📄 License

MIT License - feel free to use in your projects!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Submit a pull request

---

**Created by Emmanuel Olowu** | [GitHub](https://github.com/zeddyemy) | [Website](https://eshomonu.com/)
