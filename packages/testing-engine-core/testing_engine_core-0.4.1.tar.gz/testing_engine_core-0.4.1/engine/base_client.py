"""
Base HTTP client for service communication
"""

import logging
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseServiceClient:
    """
    Base class for service HTTP clients.
    
    Features:
    - Automatic retries with backoff
    - Timeout configuration
    - Request/response logging
    - Error handling
    """
    
    def __init__(self, base_url: str, timeout: int = 30, retry_attempts: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Make HTTP request to service.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative to base_url)
            data: Request body data
            params: Query parameters
            headers: Additional headers
        
        Returns:
            Response object
        
        Raises:
            requests.RequestException: On request failure
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"🌐 {method} {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            logger.debug(f"✅ Response: {response.status_code}")
            return response
            
        except requests.RequestException as e:
            logger.error(f"❌ Request failed: {method} {url} - {e}")
            raise
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """Make GET request"""
        return self._make_request("GET", endpoint, params=params, headers=headers)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """Make POST request"""
        return self._make_request("POST", endpoint, data=data, headers=headers)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """Make PUT request"""
        return self._make_request("PUT", endpoint, data=data, headers=headers)
    
    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """Make DELETE request"""
        return self._make_request("DELETE", endpoint, headers=headers)
    
    def health_check(self) -> bool:
        """
        Check if service is healthy.
        
        Returns:
            True if service is healthy
        """
        try:
            response = self.get("/health")
            is_healthy = response.status_code == 200
            
            if is_healthy:
                logger.info(f"✅ Service healthy: {self.base_url}")
            else:
                logger.warning(f"⚠️ Service unhealthy: {self.base_url}")
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"❌ Service unreachable: {self.base_url} - {e}")
            return False
