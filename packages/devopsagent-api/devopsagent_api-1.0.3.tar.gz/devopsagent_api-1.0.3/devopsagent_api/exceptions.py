"""
Exception classes for the DevOps Agent API.

This module provides a comprehensive exception hierarchy that extends botocore's
exception system while adding DevOps Agent specific error handling.
"""

from typing import Any, Dict, Optional
from botocore.exceptions import ClientError, BotoCoreError


class DevOpsAgentError(ClientError):
    """
    Base exception class for DevOps Agent API errors.

    This extends botocore's ClientError to provide a common base for all
    DevOps Agent specific exceptions while maintaining compatibility with
    boto3's exception handling patterns.
    """

    def __init__(
        self,
        error_response: Dict[str, Any],
        operation_name: str,
        service_name: str = "community-devops-agent",
        **kwargs,
    ):
        """
        Initialize the DevOps Agent error.

        Args:
            error_response: Error response dictionary
            operation_name: Name of the operation that failed
            service_name: Service name (defaults to community-devops-agent)
            **kwargs: Additional arguments passed to ClientError
        """
        super().__init__(error_response, operation_name, **kwargs)
        self.service_name = service_name

    @property
    def error_code(self) -> Optional[str]:
        """Get the error code from the response."""
        return self.response.get("Error", {}).get("Code")

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the response."""
        return self.response.get("Error", {}).get("Message")

    @property
    def http_status_code(self) -> Optional[int]:
        """Get the HTTP status code."""
        return self.response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    @property
    def request_id(self) -> Optional[str]:
        """Get the AWS request ID."""
        return self.response.get("ResponseMetadata", {}).get("RequestId")

    def __str__(self) -> str:
        """String representation of the error."""
        code = self.error_code or "Unknown"
        message = self.error_message or "Unknown error"
        request_id = self.request_id
        if request_id:
            return f"{code}: {message} (Request ID: {request_id})"
        return f"{code}: {message}"


# =============================================================================
# Authentication & Credential Errors
# =============================================================================


class AuthenticationError(DevOpsAgentError):
    """
    Authentication-related errors.

    Raised when there are issues with AWS credentials, JWT generation,
    or credential exchange authentication flow.
    """

    pass


class CredentialRefreshError(AuthenticationError):
    """
    Credential refresh errors.

    Raised when automatic credential refresh fails, typically due to:
    - Expired AWS credentials
    - Network connectivity issues
    - Invalid agent space configuration
    - API service unavailability
    """

    pass


class JWTGenerationError(AuthenticationError):
    """
    JWT token generation errors.

    Raised when JWT token generation fails, typically due to:
    - Invalid AWS credentials
    - Insufficient IAM permissions
    - Network connectivity issues
    - Control plane API unavailability
    """

    pass


class CredentialExchangeError(AuthenticationError):
    """
    Credential exchange errors.

    Raised when JWT to temporary credential exchange fails, typically due to:
    - Expired or invalid JWT token
    - Authorizer service unavailability
    - Invalid agent space ID
    - Cookie/session issues
    """

    pass


# =============================================================================
# Configuration & Setup Errors
# =============================================================================


class ConfigurationError(DevOpsAgentError):
    """
    Configuration and setup errors.

    Raised when there are issues with library configuration, typically due to:
    - Missing or invalid service model files
    - Incorrect boto3 integration
    - Invalid region or endpoint configuration
    - Package installation issues
    """

    pass


class ServiceRegistrationError(ConfigurationError):
    """
    Service registration errors.

    Raised when the boto3 service registration fails, typically due to:
    - Missing service model files
    - Botocore integration issues
    - Import or initialization failures
    """

    pass


class ModelValidationError(ConfigurationError):
    """
    Model validation errors.

    Raised when Pydantic model validation fails, typically due to:
    - Invalid data types
    - Missing required fields
    - Constraint violations
    - Schema mismatches
    """

    pass


# =============================================================================
# API Operation Errors
# =============================================================================


class ValidationException(DevOpsAgentError):
    """
    Request validation errors.

    Corresponds to HTTP 400 errors from the API, raised when:
    - Required parameters are missing
    - Parameter values are invalid
    - Request format is incorrect
    - Business rule violations
    """

    pass


class UnauthorizedException(DevOpsAgentError):
    """
    Authentication and authorization errors.

    Corresponds to HTTP 401/403 errors from the API, raised when:
    - Invalid or missing credentials
    - Insufficient permissions
    - Expired authentication
    - Invalid agent space access
    """

    pass


class ResourceNotFoundException(DevOpsAgentError):
    """
    Resource not found errors.

    Corresponds to HTTP 404 errors from the API, raised when:
    - Task ID does not exist
    - Agent space ID is invalid
    - Recommendation ID not found
    - Execution ID is missing
    """

    pass


class ConflictException(DevOpsAgentError):
    """
    Resource conflict errors.

    Corresponds to HTTP 409 errors from the API, raised when:
    - Resource already exists
    - Version conflicts in updates
    - Concurrent modification issues
    """

    pass


class ThrottlingException(DevOpsAgentError):
    """
    Rate limiting errors.

    Corresponds to HTTP 429 errors from the API, raised when:
    - Request rate exceeds limits
    - Burst limits exceeded
    - Backoff required
    """

    pass


class InternalServerException(DevOpsAgentError):
    """
    Internal server errors.

    Corresponds to HTTP 500 errors from the API, raised when:
    - Unexpected server errors
    - Service unavailability
    - Database or backend issues
    """

    pass


class ServiceUnavailableException(DevOpsAgentError):
    """
    Service unavailable errors.

    Corresponds to HTTP 503 errors from the API, raised when:
    - Service maintenance
    - Temporary outages
    - Capacity issues
    """

    pass


# =============================================================================
# Network & Connectivity Errors
# =============================================================================


class NetworkError(BotoCoreError):
    """
    Network and connectivity errors.

    Extends BotoCoreError for network-related issues that occur
    before reaching the API service.
    """

    pass


class ConnectionError(NetworkError):
    """
    Connection establishment errors.

    Raised when unable to establish connection to API endpoints, typically due to:
    - DNS resolution failures
    - Network connectivity issues
    - Firewall or proxy problems
    - SSL/TLS handshake failures
    """

    pass


class TimeoutError(NetworkError):
    """
    Request timeout errors.

    Raised when requests exceed configured timeouts, typically due to:
    - Slow network connections
    - API service overload
    - Large response payloads
    - Network congestion
    """

    pass


# =============================================================================
# Error Factory & Utilities
# =============================================================================


def _create_error_from_response(
    error_response: Dict[str, Any],
    operation_name: str,
    service_name: str = "community-devops-agent",
) -> DevOpsAgentError:
    """
    Create appropriate exception from error response.

    This factory function examines the error response and creates the
    most appropriate exception type based on error codes and HTTP status.

    Args:
        error_response: Error response from API
        operation_name: Name of the operation that failed
        service_name: Service name

    Returns:
        Appropriate DevOpsAgentError subclass
    """
    error = error_response.get("Error", {})
    error_code = error.get("Code", "")
    http_status = error_response.get("ResponseMetadata", {}).get(
        "HTTPStatusCode"
    )

    # Map error codes to exception classes
    error_code_map = {
        "ValidationException": ValidationException,
        "UnauthorizedException": UnauthorizedException,
        "ResourceNotFoundException": ResourceNotFoundException,
        "ConflictException": ConflictException,
        "ThrottlingException": ThrottlingException,
        "InternalServerException": InternalServerException,
        "ServiceUnavailableException": ServiceUnavailableException,
    }

    # Map HTTP status codes to exception classes
    status_code_map = {
        400: ValidationException,
        401: UnauthorizedException,
        403: UnauthorizedException,
        404: ResourceNotFoundException,
        409: ConflictException,
        429: ThrottlingException,
        500: InternalServerException,
        503: ServiceUnavailableException,
    }

    # Try error code first, then HTTP status
    exception_class = error_code_map.get(error_code)
    if not exception_class:
        exception_class = status_code_map.get(http_status, DevOpsAgentError)

    return exception_class(error_response, operation_name, service_name)


def handle_client_error(error: ClientError) -> DevOpsAgentError:
    """
    Convert botocore ClientError to DevOpsAgentError.

    This utility function takes a standard botocore ClientError and
    converts it to the appropriate DevOpsAgentError subclass.

    Args:
        error: Original ClientError from botocore

    Returns:
        Appropriate DevOpsAgentError subclass

    Raises:
        DevOpsAgentError: Converted exception
    """
    if hasattr(error, "operation_name"):
        operation_name = error.operation_name
    else:
        operation_name = "UnknownOperation"

    return _create_error_from_response(
        error.response, operation_name, "community-devops-agent"
    )


# =============================================================================
# Exception Hierarchy Documentation
# =============================================================================

"""
Exception Hierarchy:

BotoCoreError (botocore)
├── NetworkError (custom)
│   ├── ConnectionError
│   └── TimeoutError
└── ClientError (botocore)
    └── DevOpsAgentError (custom base)
        ├── AuthenticationError
        │   ├── CredentialRefreshError
        │   ├── JWTGenerationError
        │   └── CredentialExchangeError
        ├── ConfigurationError
        │   ├── ServiceRegistrationError
        │   └── ModelValidationError
        ├── ValidationException (HTTP 400)
        ├── UnauthorizedException (HTTP 401/403)
        ├── ResourceNotFoundException (HTTP 404)
        ├── ConflictException (HTTP 409)
        ├── ThrottlingException (HTTP 429)
        ├── InternalServerException (HTTP 500)
        └── ServiceUnavailableException (HTTP 503)
"""

# Export all exception classes
__all__ = [
    # Base exceptions
    "DevOpsAgentError",
    # Authentication errors
    "AuthenticationError",
    "CredentialRefreshError",
    "JWTGenerationError",
    "CredentialExchangeError",
    # Configuration errors
    "ConfigurationError",
    "ServiceRegistrationError",
    "ModelValidationError",
    # API operation errors
    "ValidationException",
    "UnauthorizedException",
    "ResourceNotFoundException",
    "ConflictException",
    "ThrottlingException",
    "InternalServerException",
    "ServiceUnavailableException",
    # Network errors
    "NetworkError",
    "ConnectionError",
    "TimeoutError",
    # Utilities
    "handle_client_error",
    "_create_error_from_response",
]
