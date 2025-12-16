"""HTTP client wrapper with retry logic and error handling."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from alpacafarmer.auth import AlpacaAuth
from alpacafarmer.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)


class BaseHTTPClient:
    """Async HTTP client wrapper around httpx with retry and error handling.
    
    This client provides:
    - Automatic retry logic with exponential backoff
    - Error response parsing and exception raising
    - Async context manager support for proper resource cleanup
    
    Examples:
        >>> auth = AlpacaAuth(api_key="key", secret_key="secret")
        >>> async with BaseHTTPClient(base_url="https://api.alpaca.markets", auth=auth) as client:
        ...     response = await client._get("/v2/account")
    """

    def __init__(
        self,
        base_url: str,
        auth: AlpacaAuth,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
    ) -> None:
        """Initialize the HTTP client.
        
        Args:
            base_url: Base URL for all API requests.
            auth: AlpacaAuth instance for generating auth headers.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
            retry_base_delay: Base delay in seconds for exponential backoff.
        """
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "BaseHTTPClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.auth.get_headers(),
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager and close the client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the underlying httpx client.
        
        Raises:
            RuntimeError: If client is not initialized (not in async context).
        """
        if self._client is None:
            raise RuntimeError(
                "HTTP client not initialized. Use 'async with' context manager."
            )
        return self._client

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute HTTP request with automatic retry and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            endpoint: API endpoint (will be appended to base_url).
            params: Query parameters.
            json: JSON body for POST/PUT/PATCH requests.
            
        Returns:
            Parsed JSON response as dictionary.
            
        Raises:
            AuthenticationError: For 401/403 responses.
            RateLimitError: For 429 responses.
            ValidationError: For 422 responses.
            APIError: For other HTTP errors.
        """
        last_exception: Exception | None = None
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(
                    method=method,
                    url=endpoint,
                    params=params,
                    json=json,
                )
                
                # Check for errors
                if response.status_code >= 400:
                    await self._handle_error_response(response)
                
                # Return empty dict for 204 No Content
                if response.status_code == 204:
                    return {}
                
                return response.json()
                
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                continue
            except (AuthenticationError, ValidationError):
                # Don't retry auth or validation errors
                raise
            except RateLimitError as e:
                # Retry rate limit errors with specified delay
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = e.retry_after if e.retry_after else self.retry_base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                continue
        
        # All retries exhausted
        if last_exception:
            raise APIError(
                message=f"Request failed after {self.max_retries} attempts: {last_exception}",
                status_code=0,
            )
        raise APIError(message="Request failed", status_code=0)

    async def _handle_error_response(self, response: httpx.Response) -> None:
        """Parse error response and raise appropriate exception.
        
        Args:
            response: The HTTP response object.
            
        Raises:
            AuthenticationError: For 401/403 responses.
            RateLimitError: For 429 responses.
            ValidationError: For 422 responses.
            APIError: For other HTTP errors.
        """
        try:
            body = response.json()
        except Exception:
            body = {"message": response.text}
        
        message = body.get("message", body.get("error", str(body)))
        status_code = response.status_code
        
        if status_code in (401, 403):
            raise AuthenticationError(message=message)
        
        if status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message=message,
                retry_after=int(retry_after) if retry_after else None,
            )
        
        if status_code == 422:
            errors = body.get("errors", [])
            raise ValidationError(message=message, errors=errors)
        
        raise APIError(
            message=message,
            status_code=status_code,
            response_body=body,
        )

    async def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute GET request.
        
        Args:
            endpoint: API endpoint.
            params: Query parameters.
            
        Returns:
            Parsed JSON response.
        """
        return await self._request("GET", endpoint, params=params)

    async def _post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute POST request.
        
        Args:
            endpoint: API endpoint.
            json: JSON body.
            params: Query parameters.
            
        Returns:
            Parsed JSON response.
        """
        return await self._request("POST", endpoint, params=params, json=json)

    async def _put(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute PUT request.
        
        Args:
            endpoint: API endpoint.
            json: JSON body.
            params: Query parameters.
            
        Returns:
            Parsed JSON response.
        """
        return await self._request("PUT", endpoint, params=params, json=json)

    async def _patch(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute PATCH request.
        
        Args:
            endpoint: API endpoint.
            json: JSON body.
            params: Query parameters.
            
        Returns:
            Parsed JSON response.
        """
        return await self._request("PATCH", endpoint, params=params, json=json)

    async def _delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute DELETE request.
        
        Args:
            endpoint: API endpoint.
            params: Query parameters.
            
        Returns:
            Parsed JSON response.
        """
        return await self._request("DELETE", endpoint, params=params)

    async def _get_bytes(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> bytes:
        """Execute GET request and return raw bytes.
        
        Args:
            endpoint: API endpoint.
            params: Query parameters.
            
        Returns:
            Raw response bytes.
            
        Raises:
            AuthenticationError: For 401/403 responses.
            RateLimitError: For 429 responses.
            ValidationError: For 422 responses.
            APIError: For other HTTP errors.
        """
        last_exception: Exception | None = None
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(
                    method="GET",
                    url=endpoint,
                    params=params,
                )
                
                # Check for errors
                if response.status_code >= 400:
                    await self._handle_error_response(response)
                
                return response.content
                
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                continue
            except (AuthenticationError, ValidationError):
                # Don't retry auth or validation errors
                raise
            except RateLimitError as e:
                # Retry rate limit errors with specified delay
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = e.retry_after if e.retry_after else self.retry_base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                continue
        
        # All retries exhausted
        if last_exception:
            raise APIError(
                message=f"Request failed after {self.max_retries} attempts: {last_exception}",
                status_code=0,
            )
        raise APIError(message="Request failed", status_code=0)