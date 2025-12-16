"""
Generic HTTP client for any service
"""

import logging
from typing import Any, Dict, Optional

from .base import BaseServiceClient

logger = logging.getLogger(__name__)


class GenericServiceClient(BaseServiceClient):
    """
    Generic HTTP client for any service.
    
    Extends BaseServiceClient with convenience methods and custom header support.
    Use this for services that don't need specialized client implementations.
    
    Example:
        # Basic usage
        client = GenericServiceClient("http://localhost:8080")
        data = client.get_json("/api/items")
        
        # With custom headers
        client = GenericServiceClient(
            "http://localhost:8080",
            default_headers={"X-API-Key": "secret"}
        )
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        retry_attempts: int = 3,
        default_headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize generic service client.
        
        Args:
            base_url: Service base URL
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts
            default_headers: Additional default headers to include in all requests
        """
        super().__init__(base_url, timeout, retry_attempts)
        
        # Merge additional default headers
        if default_headers:
            self.session.headers.update(default_headers)
            logger.debug(f"Added default headers: {list(default_headers.keys())}")
    
    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request and return JSON response.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            headers: Additional headers (merged with defaults)
        
        Returns:
            JSON response as dictionary
        
        Raises:
            requests.HTTPError: On non-2xx status code
        """
        response = self._make_request(method, endpoint, data, params, headers)
        response.raise_for_status()
        
        try:
            return response.json()
        except ValueError:
            # Response is not JSON
            return {"status": "success", "status_code": response.status_code}
    
    def get_json(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make GET request and return JSON response.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
        
        Returns:
            JSON response as dictionary
        """
        return self.request("GET", endpoint, params=params, headers=headers)
    
    def post_json(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make POST request and return JSON response.
        
        Args:
            endpoint: API endpoint
            data: Request body data
            headers: Additional headers
        
        Returns:
            JSON response as dictionary
        """
        return self.request("POST", endpoint, data=data, headers=headers)
    
    def put_json(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make PUT request and return JSON response.
        
        Args:
            endpoint: API endpoint
            data: Request body data
            headers: Additional headers
        
        Returns:
            JSON response as dictionary
        """
        return self.request("PUT", endpoint, data=data, headers=headers)
    
    def delete_json(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make DELETE request and return JSON response.
        
        Args:
            endpoint: API endpoint
            headers: Additional headers
        
        Returns:
            JSON response as dictionary
        """
        return self.request("DELETE", endpoint, headers=headers)
    
    def patch_json(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make PATCH request and return JSON response.
        
        Args:
            endpoint: API endpoint
            data: Request body data
            headers: Additional headers
        
        Returns:
            JSON response as dictionary
        """
        return self.request("PATCH", endpoint, data=data, headers=headers)
