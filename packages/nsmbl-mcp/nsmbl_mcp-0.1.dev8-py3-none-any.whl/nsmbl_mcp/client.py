"""
HTTP client for NSMBL API with authentication, retry logic, and error handling.
"""

import asyncio
from typing import Any, Optional
import httpx
from .config import get_config


class NSMBLAPIError(Exception):
    """Base exception for NSMBL API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, error_type: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type


class NSMBLClient:
    """
    Async HTTP client for NSMBL API.
    
    Handles authentication, retries, and error translation.
    """
    
    def __init__(self) -> None:
        """Initialize client with configuration."""
        self.config = get_config()
        self.base_url = self.config.api_base_url.rstrip("/")
        self.timeout = self.config.request_timeout
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (e.g., "/assets")
            json_data: JSON body for POST/PUT requests
            params: Query parameters
            max_retries: Maximum number of retry attempts
            
        Returns:
            dict: JSON response from API
            
        Raises:
            NSMBLAPIError: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"
        headers = self.config.get_auth_header()
        headers["Content-Type"] = "application/json"
        
        last_error: Optional[Exception] = None
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        json=json_data,
                        params=params,
                        headers=headers,
                    )
                    
                    # Handle successful responses
                    if response.status_code in (200, 201):
                        return response.json()
                    
                    # Handle error responses
                    await self._handle_error_response(response)
                    
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise NSMBLAPIError(
                    f"Request timed out after {self.timeout} seconds. "
                    f"The operation may still be processing on the server.",
                    status_code=None,
                    error_type="timeout"
                )
            
            except httpx.NetworkError as e:
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise NSMBLAPIError(
                    f"Network error: Could not connect to NSMBL API. "
                    f"Please check your internet connection.",
                    status_code=None,
                    error_type="network_error"
                )
            
            except Exception as e:
                # Don't retry on unexpected errors
                raise NSMBLAPIError(
                    f"Unexpected error: {str(e)}",
                    status_code=None,
                    error_type="unexpected_error"
                )
        
        # Should not reach here, but handle it just in case
        if last_error:
            raise NSMBLAPIError(
                f"Request failed after {max_retries} attempts: {str(last_error)}",
                status_code=None,
                error_type="max_retries_exceeded"
            )
        
        raise NSMBLAPIError(
            "Request failed for unknown reason",
            status_code=None,
            error_type="unknown_error"
        )
    
    async def _handle_error_response(self, response: httpx.Response) -> None:
        """
        Handle error responses from API.
        
        Args:
            response: HTTP response object
            
        Raises:
            NSMBLAPIError: With appropriate message based on status code
        """
        status_code = response.status_code
        
        # Try to parse error details from response
        try:
            error_data = response.json()
            if isinstance(error_data, dict) and "detail" in error_data:
                detail = error_data["detail"]
                if isinstance(detail, dict):
                    error_type = detail.get("error", "unknown_error")
                    error_message = detail.get("message", "An error occurred")
                else:
                    error_type = "unknown_error"
                    error_message = str(detail)
            else:
                error_type = "unknown_error"
                error_message = "An error occurred"
        except Exception:
            error_type = "unknown_error"
            error_message = f"HTTP {status_code}: {response.text[:200]}"
        
        # Map status codes to user-friendly messages
        if status_code == 401:
            raise NSMBLAPIError(
                f"Authentication failed: {error_message}\n"
                f"Please check your NSMBL_API_KEY in .env file.",
                status_code=401,
                error_type=error_type
            )
        
        elif status_code == 402:
            raise NSMBLAPIError(
                f"Insufficient funds: {error_message}\n"
                f"Please add credits to your NSMBL account at https://app.nsmbl.ai",
                status_code=402,
                error_type=error_type
            )
        
        elif status_code == 404:
            raise NSMBLAPIError(
                f"Not found: {error_message}",
                status_code=404,
                error_type=error_type
            )
        
        elif status_code == 422:
            raise NSMBLAPIError(
                f"Validation error: {error_message}",
                status_code=422,
                error_type=error_type
            )
        
        elif status_code == 429:
            raise NSMBLAPIError(
                f"Rate limit exceeded: {error_message}\n"
                f"Please wait a moment before trying again.",
                status_code=429,
                error_type=error_type
            )
        
        elif status_code >= 500:
            raise NSMBLAPIError(
                f"Server error: {error_message}\n"
                f"The NSMBL API is experiencing issues. Please try again later.",
                status_code=status_code,
                error_type=error_type
            )
        
        else:
            raise NSMBLAPIError(
                f"API error: {error_message}",
                status_code=status_code,
                error_type=error_type
            )
    
    async def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Make GET request to API.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            dict: JSON response
        """
        return await self._make_request("GET", endpoint, params=params)
    
    async def post(
        self,
        endpoint: str,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Make POST request to API.
        
        Args:
            endpoint: API endpoint path
            data: JSON body
            
        Returns:
            dict: JSON response
        """
        return await self._make_request("POST", endpoint, json_data=data)
    
    async def put(
        self,
        endpoint: str,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Make PUT request to API.
        
        Args:
            endpoint: API endpoint path
            data: JSON body
            
        Returns:
            dict: JSON response
        """
        return await self._make_request("PUT", endpoint, json_data=data)
    
    async def delete(
        self,
        endpoint: str
    ) -> dict[str, Any]:
        """
        Make DELETE request to API.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            dict: JSON response
        """
        return await self._make_request("DELETE", endpoint)

