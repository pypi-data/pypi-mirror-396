"""
Memory Box SDK - Main Client
The primary interface for interacting with Memory Box API
"""

import requests
from typing import Optional, Dict, Any, List
from .exceptions import (
    MemoryBoxError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
    PermissionError,
)
from .models import Memory, PaginatedResponse, Pagination, SearchResult, Stats
from .resources import MemoriesResource


class MemoryBox:
    """
    Memory Box SDK Client.
    
    The main entry point for interacting with the Memory Box API.
    
    Usage:
        from memorybox import MemoryBox
        
        mb = MemoryBox(api_key="mb_live_...")
        
        # Access memories
        memories = mb.memories.list()
        
        # Create a memory
        memory = mb.memories.create(content="...", platform="custom")
        
        # Search
        results = mb.memories.search("machine learning")
    
    Args:
        api_key: Your Memory Box API key (starts with 'mb_live_' or 'mb_test_')
        base_url: API base URL (default: production)
        timeout: Request timeout in seconds (default: 30)
    """
    
    DEFAULT_BASE_URL = "https://memory-box-website.onrender.com"
    DEV_BASE_URL = "http://localhost:5000"
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        if not api_key:
            raise ValueError("API key is required")
        
        if not api_key.startswith("mb_"):
            raise ValueError("Invalid API key format. Key should start with 'mb_live_' or 'mb_test_'")
        
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        
        # Set up session with auth headers
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "MemoryBox-Python-SDK/1.0.0",
        })
        
        # Initialize resources
        self.memories = MemoriesResource(self)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Memory Box API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint (e.g., '/api/v1/memories')
            params: URL query parameters
            json: JSON request body
        
        Returns:
            Parsed JSON response
        
        Raises:
            MemoryBoxError: On API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            raise MemoryBoxError("Request timed out", status_code=408)
        except requests.exceptions.ConnectionError:
            raise MemoryBoxError("Failed to connect to Memory Box API")
        except requests.exceptions.RequestException as e:
            raise MemoryBoxError(f"Request failed: {str(e)}")
        
        return self._handle_response(response)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: requests Response object
        
        Returns:
            Parsed JSON response
        
        Raises:
            Various MemoryBoxError subclasses based on status code
        """
        try:
            data = response.json()
        except ValueError:
            data = {"error": response.text}
        
        if response.status_code == 200 or response.status_code == 201:
            return data
        
        error_message = data.get("error") or data.get("message") or "Unknown error"
        
        if response.status_code == 401:
            raise AuthenticationError(
                error_message,
                status_code=response.status_code,
                response=data,
            )
        
        if response.status_code == 403:
            raise PermissionError(
                error_message,
                status_code=response.status_code,
                response=data,
            )
        
        if response.status_code == 404:
            raise NotFoundError(
                error_message,
                status_code=response.status_code,
                response=data,
            )
        
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                error_message,
                status_code=response.status_code,
                response=data,
                retry_after=int(retry_after) if retry_after else None,
            )
        
        if response.status_code == 400:
            raise ValidationError(
                error_message,
                status_code=response.status_code,
                response=data,
            )
        
        if response.status_code >= 500:
            raise ServerError(
                error_message,
                status_code=response.status_code,
                response=data,
            )
        
        raise MemoryBoxError(
            error_message,
            status_code=response.status_code,
            response=data,
        )
    
    def get_stats(self) -> Stats:
        """
        Get memory statistics for your account.
        
        Returns:
            Stats object with total memories, platform breakdown, etc.
        """
        response = self._request("GET", "/api/v1/stats")
        return Stats.from_dict(response.get("data", {}))
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the Memory Box API is healthy.
        
        Returns:
            Dict with status, version, and timestamp
        """
        return self._request("GET", "/api/v1/health")
    
    def __repr__(self) -> str:
        return f"MemoryBox(base_url='{self.base_url}')"

