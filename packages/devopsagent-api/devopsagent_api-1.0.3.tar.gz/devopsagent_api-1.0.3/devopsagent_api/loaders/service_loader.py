"""Service loader for registering community services with boto3."""

import json
from pathlib import Path
from typing import Dict, Any, List

from botocore.loaders import Loader


class ServiceLoader:
    """Loads service model files for community AWS services."""

    # Supported services and their configurations
    SERVICES = {
        "community-devops-agent": {
            "api_version": "2025-12-09",
            "service_name": "community-devops-agent"
        },
        "community-aidevops": {
            "api_version": "2018-05-10",
            "service_name": "community-aidevops"
        }
    }

    def __init__(self, service_name: str) -> None:
        """Initialize the service loader for a specific service."""
        if service_name not in self.SERVICES:
            raise ValueError(f"Unsupported service: {service_name}")

        self.service_name = service_name
        self.api_version = self.SERVICES[service_name]["api_version"]
        self.data_path = self._get_data_path()
        self._service_data = None

    def _get_data_path(self) -> Path:
        """Get the path to the service model data directory."""
        # Get the directory containing this file
        current_dir = Path(__file__).parent.parent
        data_dir = current_dir / "data" / self.service_name / self.api_version

        if not data_dir.exists():
            raise RuntimeError(
                f"Service model directory not found: {data_dir}. "
                "Ensure the package is properly installed."
            )

        return data_dir

    def load_service_model(
        self, type_name: str = "service-2"
    ) -> Dict[str, Any]:
        """
        Load a service model file.

        Args:
            type_name: The type of model to load (e.g., 'service-2', 'paginators-1')

        Returns:
            The loaded service model as a dictionary
        """
        file_path = self.data_path / f"{type_name}.json"

        if not file_path.exists():
            raise FileNotFoundError(
                f"Service model file not found: {file_path}"
            )

        with open(file_path, "r") as f:
            return json.load(f)

    def get_service_data(self) -> Dict[str, Any]:
        """
        Get the complete service data including all model files.

        Returns:
            Dictionary containing service model, paginators, waiters, etc.
        """
        if self._service_data is None:
            self._service_data = {
                "service": self.load_service_model("service-2"),
                "paginators": self.load_service_model("paginators-1"),
                "waiters": self.load_service_model("waiters-2"),
                "endpoint-rule-set": self.load_service_model(
                    "endpoint-rule-set-1"
                ),
            }

        return self._service_data

    @classmethod
    def get_supported_services(cls) -> List[str]:
        """Get list of supported service names."""
        return list(cls.SERVICES.keys())

    @classmethod
    def register_with_botocore(cls) -> None:
        """
        Register all supported services with botocore's loader.

        This modifies botocore's loader to include our custom service models.
        """
        # Create loaders for each service
        loaders = {}
        for service_name in cls.SERVICES:
            try:
                loaders[service_name] = ServiceLoader(service_name)
            except RuntimeError:
                # Skip services that don't have model files installed
                continue

        # Get the original methods
        original_load_data = Loader.load_data
        original_list_available_services = Loader.list_available_services
        original_list_api_versions = Loader.list_api_versions

        def custom_load_data(self, data_path):
            """Custom load_data that includes our services."""
            # Check if this is a request for one of our services
            parts = data_path.split("/")

            if len(parts) >= 2 and parts[0] in loaders:
                service_name = parts[0]
                loader = loaders[service_name]

                # This is a request for our service
                if len(parts) == 2:
                    # Request for API versions list
                    if parts[1] == "api-versions":
                        return [loader.api_version]
                elif len(parts) == 3:
                    # Request for a specific model file
                    api_version = parts[1]
                    model_type = parts[2]

                    if api_version == loader.api_version:
                        try:
                            return loader.load_service_model(model_type)
                        except FileNotFoundError:
                            pass

            # Fall back to original loader
            return original_load_data(self, data_path)

        def custom_list_available_services(self, type_name):
            """Custom list_available_services that includes our services."""
            # Get the original list
            services = original_list_available_services(self, type_name)

            # Add our services if not already present
            for service_name in loaders:
                if service_name not in services:
                    services.append(service_name)

            return services

        def custom_list_api_versions(self, service_name, type_name):
            """Custom list_api_versions that includes our services."""
            if service_name in loaders:
                loader = loaders[service_name]
                # Return our API version
                return [loader.api_version]

            # Fall back to original loader
            return original_list_api_versions(self, service_name, type_name)

        # Monkey-patch the Loader class
        Loader.load_data = custom_load_data
        Loader.list_available_services = custom_list_available_services
        Loader.list_api_versions = custom_list_api_versions
