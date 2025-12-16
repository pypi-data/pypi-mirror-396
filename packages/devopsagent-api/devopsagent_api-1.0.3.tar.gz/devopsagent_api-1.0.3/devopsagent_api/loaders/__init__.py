"""
Custom service loaders for boto3 service integration.

This module contains custom loader implementations for registering
the Community DevOps Agent service with boto3.
"""

from .service_loader import ServiceLoader

__all__ = ["ServiceLoader"]
