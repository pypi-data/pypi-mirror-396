# TroveSuite Packages

TroveSuite package providing authentication, authorization, notifications, and other enterprise services for TroveSuite applications.

## Features

- **Authentication Services**: JWT token validation and user authentication
- **Authorization Services**: Multi-level authorization with tenant verification
- **Notification Services**: Send and manage notifications for users
- **Permission Checking**: Hierarchical permission system (organization > business > app > location > resource)
- **Database Integration**: PostgreSQL support with connection pooling
- **Logging**: Comprehensive logging with multiple output formats
- **Azure Integration**: Support for Azure Storage Queues and Managed Identity
- **FastAPI Ready**: Built for FastAPI applications
- **Extensible**: Easy to add new services and functionality

## Installation

### From Azure DevOps Artifacts

#### Using pip
```bash
pip install trovesuite --index-url https://pypi.org/simple/ --extra-index-url https://pkgs.dev.azure.com/brightgclt/trovesuite/_packaging/packages/pypi/simple/
```

#### Using Poetry
```bash
# Add Azure DevOps Artifacts as a source
poetry source add --priority=supplemental azure https://pkgs.dev.azure.com/brightgclt/trovesuite/_packaging/packages/pypi/simple/

# Install the package
poetry add trovesuite
```

### From Source

#### Using pip
```bash
git clone https://brightgclt@dev.azure.com/brightgclt/trovesuite/_git/packages
cd packages
pip install -e .
```

#### Using Poetry
```bash
git clone https://brightgclt@dev.azure.com/brightgclt/trovesuite/_git/packages
cd packages
poetry install
```

### Development Installation

#### Using pip
```bash
git clone https://brightgclt@dev.azure.com/brightgclt/trovesuite/_git/packages
cd packages
pip install -e ".[dev]"
```

#### Using Poetry
```bash
git clone https://brightgclt@dev.azure.com/brightgclt/trovesuite/_git/packages
cd packages
poetry install --with dev
```

## Quick Start

> **✅ Package Status**: All import issues have been resolved in version 1.0.5. The package now works correctly when installed from PyPI or wheel files.

### Import Patterns

The package provides clean, simplified import patterns:

```python
# Import services and DTOs from main package
from trovesuite import AuthService, NotificationService
from trovesuite.auth import AuthServiceWriteDto
from trovesuite.notification import NotificationEmailServiceWriteDto, NotificationSMSServiceWriteDto

# Or import everything you need in one line
from trovesuite import AuthService, NotificationService
from trovesuite.auth import AuthServiceWriteDto
from trovesuite.notification import NotificationEmailServiceWriteDto
```

### Basic Usage

```python
from trovesuite import AuthService, NotificationService
from trovesuite.configs.settings import db_settings

# Configure your database settings
db_settings.DB_HOST = "localhost"
db_settings.DB_PORT = 5432
db_settings.DB_NAME = "your_database"
db_settings.DB_USER = "your_user"
db_settings.DB_PASSWORD = "your_password"
db_settings.SECRET_KEY = "your-secret-key"

# Initialize the auth service
auth_service = AuthService()

# Authorize a user
from trovesuite.auth import AuthServiceWriteDto
auth_data = AuthServiceWriteDto(user_id="user123", tenant="tenant456")
result = AuthService.authorize(auth_data)

if result.success:
    print("User authorized successfully")
    for role in result.data:
        print(f"Role: {role.role_id}, Permissions: {role.permissions}")
else:
    print(f"Authorization failed: {result.detail}")
```

### Notification Service Usage

```python
from trovesuite import NotificationService
from trovesuite.notification import NotificationEmailServiceWriteDto

# Send an email notification
email_data = NotificationEmailServiceWriteDto(
    sender_email="your-email@gmail.com",
    receiver_email=["recipient1@example.com", "recipient2@example.com"],
    password="your-app-password",  # Gmail app password
    subject="Test Notification",
    text_message="This is a plain text message",
    html_message="<h1>This is an HTML message</h1><p>With rich formatting!</p>"
)

result = NotificationService.send_email(email_data)

if result.success:
    print(f"Email sent successfully: {result.detail}")
else:
    print(f"Email failed: {result.error}")
```

### JWT Token Decoding

```python
from trovesuite import AuthService
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    # Decode and validate token
    user_data = AuthService.decode_token(token)
    user_id = user_data["user_id"]
    tenant_id = user_data["tenant_id"]
    
    # Authorize user
    from trovesuite.auth import AuthServiceWriteDto
    auth_data = AuthServiceWriteDto(user_id=user_id, tenant=tenant_id)
    auth_result = AuthService.authorize(auth_data)
    return auth_result
```

### Convenience Methods

```python
from trovesuite import AuthService

# Get user info directly from token
user_info = AuthService.get_user_info_from_token(token)
print(f"User: {user_info['user_id']}, Tenant: {user_info['tenant_id']}")

# Authorize user directly from token (combines decode + authorize)
auth_result = AuthService.authorize_user_from_token(token)

if auth_result.success:
    # Get all user permissions
    all_permissions = AuthService.get_user_permissions(auth_result.data)
    print(f"User has permissions: {all_permissions}")
    
    # Check if user has any of the required permissions
    has_any = AuthService.has_any_permission(
        auth_result.data, 
        ["read", "write", "admin"]
    )
    
    # Check if user has all required permissions
    has_all = AuthService.has_all_permissions(
        auth_result.data, 
        ["read", "write"]
    )
```

### Permission Checking

```python
from trovesuite import AuthService

# After getting user roles from authorization
user_roles = auth_result.data

# Check specific permission
has_permission = AuthService.check_permission(
    user_roles=user_roles,
    action="read",
    org_id="org123",
    bus_id="bus456",
    app_id="app789"
)

if has_permission:
    print("User has permission to read from this resource")
```


## Configuration

### Quick Configuration Check

```python
from trovesuite.configs.settings import db_settings

# Check your configuration
config_summary = db_settings.get_configuration_summary()
print("Current configuration:")
for key, value in config_summary.items():
    print(f"  {key}: {value}")

# The service will automatically validate configuration on import
# and show warnings for potential issues
```

### Environment Variables

The service uses environment variables for configuration. Set these in your environment or `.env` file:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
DATABASE_URL=postgresql://user:password@localhost:5432/database

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application
APP_NAME=Auth Service
ENVIRONMENT=production
DEBUG=false

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=detailed
LOG_TO_FILE=true

# Table Names (customize as needed)
MAIN_TENANTS_TABLE=tenants
TENANT_LOGIN_SETTINGS_TABLE=login_settings
USER_GROUPS_TABLE=user_groups
ASSIGN_ROLES_TABLE=assign_roles
ROLE_PERMISSIONS_TABLE=role_permissions

# Azure (optional - for queue functionality)
STORAGE_ACCOUNT_NAME=your-storage-account
USER_ASSIGNED_MANAGED_IDENTITY=your-managed-identity
```

### Database Schema

The service expects the following database tables:

#### Main Schema Tables
- `tenants` - Tenant information and verification status
- `role_permissions` - Role-permission mappings

#### Tenant Schema Tables (per tenant)
- `login_settings` - User login configurations (working days, suspension status, etc.)
- `user_groups` - User-group memberships
- `assign_roles` - Role assignments to users/groups with resource hierarchy

## API Reference

### AuthService

#### `authorize(user_id: str, tenant_id: str) -> Respons[AuthServiceReadDto]`

Authorizes a user and returns their roles and permissions.

**Parameters:**
- `user_id`: The user identifier (must be a non-empty string)
- `tenant_id`: The tenant identifier (must be a non-empty string)

**Returns:**
- `Respons[AuthServiceReadDto]`: Authorization result with user roles and permissions

**Error Codes:**
- `INVALID_USER_ID`: Invalid or empty user_id
- `INVALID_TENANT_ID`: Invalid or empty tenant_id
- `TENANT_NOT_FOUND`: Tenant doesn't exist or is deleted
- `TENANT_NOT_VERIFIED`: Tenant exists but is not verified
- `USER_NOT_FOUND`: User doesn't exist in tenant or is inactive
- `USER_SUSPENDED`: User account is suspended
- `LOGIN_TIME_RESTRICTED`: Login not allowed at current time

#### `decode_token(token: str) -> dict`

Decodes and validates a JWT token.

**Parameters:**
- `token`: The JWT token to decode

**Returns:**
- `dict`: Token payload with user_id and tenant_id

**Raises:**
- `HTTPException`: If token is invalid

#### `check_permission(user_roles: list, action: str, **kwargs) -> bool`

Checks if a user has a specific permission for a resource.

**Parameters:**
- `user_roles`: List of user roles from authorization
- `action`: The permission action to check
- `org_id`, `bus_id`, `app_id`, `resource_id`, `shared_resource_id`: Resource identifiers

**Returns:**
- `bool`: True if user has permission, False otherwise

#### `get_user_info_from_token(token: str) -> dict`

Convenience method to get user information from a JWT token.

**Parameters:**
- `token`: JWT token string

**Returns:**
- `dict`: User information including user_id and tenant_id

#### `authorize_user_from_token(token: str) -> Respons[AuthServiceReadDto]`

Convenience method to authorize a user directly from a JWT token.

**Parameters:**
- `token`: JWT token string

**Returns:**
- `Respons[AuthServiceReadDto]`: Authorization result with user roles and permissions

#### `get_user_permissions(user_roles: list) -> list`

Get all unique permissions for a user across all their roles.

**Parameters:**
- `user_roles`: List of user roles from authorization

**Returns:**
- `list`: Unique list of permissions

#### `has_any_permission(user_roles: list, required_permissions: list) -> bool`

Check if user has any of the required permissions.

**Parameters:**
- `user_roles`: List of user roles from authorization
- `required_permissions`: List of permissions to check for

**Returns:**
- `bool`: True if user has any of the required permissions

#### `has_all_permissions(user_roles: list, required_permissions: list) -> bool`

Check if user has all of the required permissions.

**Parameters:**
- `user_roles`: List of user roles from authorization
- `required_permissions`: List of permissions to check for

**Returns:**
- `bool`: True if user has all of the required permissions

### NotificationService

#### `send_email(data: NotificationEmailServiceWriteDto) -> Respons[NotificationEmailServiceReadDto]`

Sends an email notification via Gmail SMTP. Supports both plain text and HTML email bodies.

**Parameters:**
- `data`: Email notification data including sender, recipients, subject, and message content

**Returns:**
- `Respons[NotificationEmailServiceReadDto]`: Email sending result with success status and details

**Example:**
```python
from trovesuite import NotificationService
from trovesuite.notification import NotificationEmailServiceWriteDto

email_data = NotificationEmailServiceWriteDto(
    sender_email="sender@gmail.com",
    receiver_email=["user1@example.com", "user2@example.com"],
    password="your-gmail-app-password",
    subject="Welcome to TroveSuite",
    text_message="Welcome! This is a plain text message.",
    html_message="<h1>Welcome!</h1><p>This is an <strong>HTML</strong> message.</p>"
)

result = NotificationService.send_email(email_data)
if result.success:
    print("Email sent successfully!")
else:
    print(f"Failed to send email: {result.error}")
```

#### `send_sms(data: NotificationSMSServiceWriteDto) -> Respons[NotificationSMSServiceReadDto]`

Sends an SMS notification (currently not implemented).

**Parameters:**
- `data`: SMS notification data

**Returns:**
- `Respons[NotificationSMSServiceReadDto]`: SMS sending result

### Data Models

#### `NotificationEmailServiceWriteDto`

```python
class NotificationEmailServiceWriteDto(BaseModel):
    sender_email: str
    receiver_email: Union[str, List[str]]  # Single email or list of emails
    password: str  # Gmail app password
    subject: str
    text_message: str
    html_message: Optional[str] = None  # Optional HTML content
```

#### `NotificationEmailServiceReadDto`

```python
class NotificationEmailServiceReadDto(BaseModel):
    pass  # Empty response model for email service
```

#### `NotificationSMSServiceWriteDto`

```python
class NotificationSMSServiceWriteDto(BaseModel):
    pass  # To be implemented for SMS functionality
```

#### `NotificationSMSServiceReadDto`

```python
class NotificationSMSServiceReadDto(BaseModel):
    pass  # To be implemented for SMS functionality
```

#### `AuthServiceReadDto`

```python
class AuthServiceReadDto(BaseModel):
    org_id: Optional[str] = None
    bus_id: Optional[str] = None 
    app_id: Optional[str] = None 
    shared_resource_id: Optional[str] = None
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    role_id: Optional[str] = None
    tenant_id: Optional[str] = None
    permissions: Optional[List[str]] = None
    resource_id: Optional[str] = None
```

#### `Respons[T]`

```python
class Respons[T](BaseModel):
    detail: Optional[str] = None
    error: Optional[str] = None
    data: Optional[List[T]] = None
    status_code: int = 200
    success: bool = True
    pagination: Optional[PaginationMeta] = None
```

## Error Handling

The service provides comprehensive error handling with specific error codes and user-friendly messages:

### Common Error Scenarios

```python
from trovesuite import AuthService

# Example: Handle authorization errors
result = AuthService.authorize("user123", "tenant456")

if not result.success:
    if result.error == "TENANT_NOT_FOUND":
        print("Tenant doesn't exist")
    elif result.error == "USER_SUSPENDED":
        print("User account is suspended")
    elif result.error == "LOGIN_TIME_RESTRICTED":
        print("Login not allowed at this time")
    else:
        print(f"Authorization failed: {result.detail}")
else:
    print("Authorization successful!")
```

### Best Practices

1. **Always check the `success` field** before accessing `data`
2. **Use specific error codes** for programmatic error handling
3. **Display user-friendly messages** from the `detail` field
4. **Log errors** for debugging purposes
5. **Validate input parameters** before calling service methods

### Configuration Validation

The service automatically validates configuration on import and shows warnings for potential issues:

```python
# Configuration validation happens automatically
from trovesuite_auth_service.configs.settings import db_settings

# Check configuration summary
config = db_settings.get_configuration_summary()
print("Configuration loaded successfully")

# Common warnings you might see:
# - Default SECRET_KEY in production
# - Missing database configuration
# - Inconsistent environment settings
```

## Development

### Running Tests

#### Using pip
```bash
pytest
```

#### Using Poetry
```bash
poetry run pytest
```

### Code Formatting

#### Using pip
```bash
black trovesuite/
```

#### Using Poetry
```bash
poetry run black trovesuite/
```

### Type Checking

#### Using pip
```bash
mypy trovesuite/
```

#### Using Poetry
```bash
poetry run mypy trovesuite/
```

### Linting

#### Using pip
```bash
flake8 trovesuite/
```

#### Using Poetry
```bash
poetry run flake8 trovesuite/
```

### Poetry Configuration

If you're using Poetry in your project, you can add this package to your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
trovesuite = "^1.0.0"

[[tool.poetry.source]]
name = "azure"
url = "https://pkgs.dev.azure.com/brightgclt/trovesuite/_packaging/packages/pypi/simple/"
priority = "supplemental"
```

Then run:
```bash
poetry install
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Import Issues

If you encounter import errors, make sure you're using the correct import patterns:

```python
# ✅ Correct imports
from trovesuite import AuthService, NotificationService
from trovesuite.auth import AuthServiceWriteDto
from trovesuite.notification import NotificationEmailServiceWriteDto

# ❌ Incorrect imports (will fail)
from trovesuite.auth.auth_write_dto import AuthServiceWriteDto  # Too specific
from trovesuite.notification.notification_write_dto import NotificationEmailServiceWriteDto  # Too specific
```

### Package Installation

If you're having issues with the package installation:

1. **Make sure you have the latest version**:
   ```bash
   pip install --upgrade trovesuite
   ```

2. **Force reinstall if needed**:
   ```bash
   pip install --force-reinstall trovesuite
   ```

3. **Check your Python environment**:
   ```bash
   python -c "import trovesuite; print('Package installed successfully')"
   ```

### Common Issues

- **ImportError: No module named 'src'**: This was fixed in version 1.0.5. Update to the latest version.
- **AttributeError: module has no attribute 'AuthServiceWriteDto'**: Use `from trovesuite.auth import AuthServiceWriteDto` instead of importing from the main package.

## Support

For support, email brightgclt@gmail.com or create a work item in the [Azure DevOps repository](https://dev.azure.com/brightgclt/trovesuite/_workitems/create).

## Changelog

### 1.0.5
- Fixed all import issues across auth, notification, and entities modules
- Changed absolute imports (`from src.trovesuite.`) to relative imports (`from .` and `from ..`)
- Ensured package works correctly when installed from PyPI or wheel
- Added service write DTOs to module exports for easier usage
- Updated documentation with simplified import patterns
- All services and DTOs now import correctly in clean environments
- Package builds and installs without import errors

### 1.0.8
- Restructured package for direct service imports
- Added comprehensive notification services with email support
- Excluded controllers from package build
- Updated import paths for better usability
- JWT token validation
- User authorization with tenant verification
- Hierarchical permission checking
- PostgreSQL database integration
- Comprehensive logging
- Azure integration support
- Email notification service with Gmail SMTP support
- Support for both plain text and HTML email content
- Multiple recipient support for email notifications
