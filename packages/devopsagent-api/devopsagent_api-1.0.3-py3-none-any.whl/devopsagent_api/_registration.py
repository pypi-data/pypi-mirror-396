"""
Service registration module for boto3 integration.

This module handles the registration of the community-devops-agent service
with botocore, enabling boto3.client('community-devops-agent') usage.
"""

import logging
from pathlib import Path

from botocore.session import get_session

from .loaders.service_loader import ServiceLoader

logger = logging.getLogger(__name__)

# Package data directory
PACKAGE_DIR = Path(__file__).parent


def _register_service_with_botocore() -> None:
    """
    Register all supported community services with botocore.

    This function uses the ServiceLoader to register all available services.
    """
    try:
        # Use the ServiceLoader to register all supported services
        ServiceLoader.register_with_botocore()

        # Set service model paths for each supported service
        import botocore.session
        session = botocore.session.Session()

        for service_name in ServiceLoader.get_supported_services():
            service_config = ServiceLoader.SERVICES[service_name]
            api_version = service_config["api_version"]
            session.set_config_variable(
                f"service_model_{service_name}",
                f"{service_name}/{api_version}/service-2",
            )

        logger.debug("Successfully registered community services with botocore")

    except Exception as e:
        logger.error(f"Failed to register community services: {e}")
        raise


def _register_credential_provider() -> None:
    """
    Register the custom DevOpsAgentCredentialProvider with botocore.

    This enables automatic authentication flow for the service.
    """
    try:
        from .auth import DevOpsAgentCredentialProvider

        # Get the botocore session
        session = get_session()

        # Create our credential provider
        provider = DevOpsAgentCredentialProvider()

        # Get the credential resolver
        resolver = session.get_component("credential_provider")

        # Insert our provider at the beginning of the chain so it gets priority
        # This ensures it's checked before environment variables
        if hasattr(resolver, "providers"):
            resolver.providers.insert(0, provider)
            logger.debug(
                "Successfully registered DevOpsAgentCredentialProvider at start of chain"
            )
        else:
            # Fallback to component registration
            session.register_component("credential_provider", provider)
            logger.debug(
                "Successfully registered DevOpsAgentCredentialProvider as component"
            )

    except ImportError:
        logger.warning(
            "DevOpsAgentCredentialProvider not available yet - auth.py not implemented"
        )
    except Exception as e:
        logger.error(f"Failed to register credential provider: {e}")
        raise


def register_service() -> None:
    """
    Main registration function called on package import.

    This function registers both the service loader and credential provider
    with botocore, enabling full boto3 integration.
    """
    supported_services = ServiceLoader.get_supported_services()
    logger.info(f"Registering community services with boto3: {supported_services}")

    # Register the service model loader
    _register_service_with_botocore()

    # Register the credential provider (if available)
    _register_credential_provider()

    logger.info("Community services successfully registered with boto3")


# Register the service when this module is imported
register_service()
