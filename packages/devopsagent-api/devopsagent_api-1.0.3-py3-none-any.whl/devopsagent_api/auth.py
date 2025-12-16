"""
Authentication module for DevOps Agent API.

This module implements direct AWS SigV4 authentication for boto3 integration.
No JWT generation or credential exchange is needed - we use AWS credentials directly.
"""

import logging
import threading
from typing import Optional

from botocore.credentials import CredentialProvider, Credentials
from botocore.session import Session

logger = logging.getLogger(__name__)


class DevOpsAgentCredentialProvider(CredentialProvider):
    """
    Custom credential provider for the DevOps Agent API.

    This provider uses direct AWS SigV4 authentication, passing through
    the user's AWS credentials directly without JWT exchange.
    """

    def __init__(self):
        """Initialize the credential provider."""
        # Thread lock for credential operations
        self._lock = threading.Lock()

        logger.debug("Initialized DevOpsAgentCredentialProvider")

    def load(
        self, service_name: Optional[str] = None
    ) -> Optional[Credentials]:
        """
        Load credentials for the DevOps Agent service.

        This method is called by botocore when credentials are needed.
        It only provides credentials for the community-devops-agent service.

        Args:
            service_name: The service name requesting credentials

        Returns:
            Credentials object or None if unable to obtain credentials
        """
        # Only provide credentials for our specific service
        if service_name != "community-devops-agent":
            logger.debug(
                f"DevOpsAgentCredentialProvider: skipping for service {service_name}"
            )
            return None

        logger.info(
            "DevOpsAgentCredentialProvider.load() called for community-devops-agent service"
        )
        with self._lock:
            try:
                logger.info("Starting direct credential refresh process")
                credentials = self._refresh_credentials()
                logger.info("Successfully obtained direct AWS credentials")
                return credentials
            except Exception as e:
                logger.error(f"Failed to obtain credentials: {e}")
                import traceback

                logger.error(f"Traceback: {traceback.format_exc()}")
                return None

    def _refresh_credentials(self) -> Credentials:
        """
        Get AWS credentials directly from the boto3 credential chain.

        The DevOps Agent API uses direct AWS SigV4 signing instead of
        JWT exchange. We simply pass through the user's AWS credentials.

        Returns:
            AWS credentials for direct SigV4 authentication
        """
        # Get AWS credentials from boto3 credential chain
        aws_credentials = self._get_aws_credentials()
        if not aws_credentials:
            raise RuntimeError("No AWS credentials available")

        # For direct AWS SigV4 authentication, we use the credentials as-is
        # No JWT generation or exchange needed
        credentials = Credentials(
            access_key=aws_credentials.access_key,
            secret_key=aws_credentials.secret_key,
            token=aws_credentials.token,
            method="devops-agent-direct-sigv4",
        )

        logger.info(
            "Using direct AWS SigV4 authentication (no JWT exchange needed)"
        )
        return credentials

    def _get_aws_credentials(self) -> Optional[Credentials]:
        """
        Get AWS credentials from the boto3 credential chain.

        Returns:
            AWS credentials or None if not available
        """
        # Get the botocore session
        session = Session()

        # Get credentials from the chain
        creds = session.get_credentials()
        return creds
