"""
Service HTTP Clients - Universal clients for any REST API
"""

from .base import BaseServiceClient
from .generic import GenericServiceClient

__all__ = [
    "BaseServiceClient",
    "GenericServiceClient",
]
