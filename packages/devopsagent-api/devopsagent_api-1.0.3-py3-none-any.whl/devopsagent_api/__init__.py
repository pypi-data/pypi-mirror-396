"""
Community DevOps Agent API - boto3 Service Integration

A Python client library that provides native boto3 integration for the AWS DevOps Agent API.
This library registers 'community-devops-agent' as a custom boto3 service, enabling
familiar AWS SDK patterns for DevOps Agent operations.

Usage:
    import devopsagent_api  # Registers the service
    import boto3

    client = boto3.client('community-devops-agent', region_name='us-east-1')
    tasks = client.list_tasks(agentSpaceId='your-agent-space-uuid')
"""

import logging

__version__ = "1.0.0"
__author__ = "Stefan Saftic"
__email__ = "stefan.saftic@gmail.com"
__license__ = "Apache-2.0"

logger = logging.getLogger(__name__)

# Service registration happens on import
try:
    # Import the registration module to trigger service registration
    from .loaders import ServiceLoader

    ServiceLoader.register_with_botocore()
    _SERVICE_REGISTERED = True
    logger.debug("Community DevOps Agent service registered successfully")
except Exception as e:
    _SERVICE_REGISTERED = False
    logger.warning(f"Failed to register Community DevOps Agent service: {e}")
    logger.warning("Some functionality may not be available")

# Re-export commonly used items
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]


def is_service_registered() -> bool:
    """
    Check if the service was successfully registered with boto3.

    Returns:
        True if the service is registered, False otherwise
    """
    return _SERVICE_REGISTERED
