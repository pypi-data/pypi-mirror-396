"""Main client"""

import json
from typing import Any, Dict, Optional

import httpx

from .errors import ApiError
from .types import ClientOptions
from .utils import build_url


class OomolConnectClient:
    """Oomol Connect main client

    This is the main entry point of the SDK, providing access to all sub-clients.

    Example:
        >>> client = OomolConnectClient(
        ...     base_url="https://api.example.com/api",
        ...     api_token="your-token"
        ... )
        >>> blocks = await client.blocks.list()
    """

    def __init__(self, options: Optional[ClientOptions] = None) -> None:
        """Initialize client

        Args:
            options: Client configuration options
        """
        options = options or {}

        self._base_url = options.get("base_url", "/api")
        self._timeout = options.get("timeout", 30.0)
        self._default_headers: Dict[str, str] = {
            "Content-Type": "application/json",
        }

        # Add custom headers
        if options.get("default_headers"):
            self._default_headers.update(options["default_headers"])

        # Handle API Token
        api_token = options.get("api_token")
        if api_token:
            self._default_headers["Authorization"] = api_token

        # Create HTTP client
        self._http_client = httpx.AsyncClient(
            timeout=self._timeout,
            headers=self._default_headers
        )

        # Lazy import to avoid circular dependencies
        from .applets import AppletsClient
        from .blocks import BlocksClient
        from .packages import PackagesClient
        from .tasks import TasksClient

        # Initialize sub-clients
        self.blocks = BlocksClient(self)
        self.tasks = TasksClient(self)
        self.packages = PackagesClient(self)
        self.applets = AppletsClient(self)

    async def request(
        self,
        path: str,
        method: str = "GET",
        json_data: Optional[Any] = None,
        data: Optional[Any] = None,
        files: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Send HTTP request

        Args:
            path: Request path
            method: HTTP method
            json_data: JSON data
            data: Form data
            files: File data
            headers: Additional request headers

        Returns:
            Response data (automatically parsed as JSON)

        Raises:
            ApiError: Raised when API request fails
        """
        url = build_url(self._base_url, path)

        # Merge request headers
        request_headers = dict(self._default_headers)
        if headers:
            request_headers.update(headers)

        # If there's file upload, remove Content-Type (let httpx set it automatically)
        if files:
            request_headers.pop("Content-Type", None)

        try:
            response = await self._http_client.request(
                method=method,
                url=url,
                json=json_data,
                data=data,
                files=files,
                headers=request_headers,
            )

            # Check status code
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", response.text)
                except Exception:
                    error_message = response.text

                raise ApiError(
                    message=error_message,
                    status=response.status_code,
                    response=response.text
                )

            # Try to parse JSON
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return response.text

        except httpx.HTTPError as e:
            raise ApiError(
                message=str(e),
                status=0,
                response=None
            )

    async def request_to_server(
        self,
        server_url: str,
        path: str,
        method: str = "GET",
        json_data: Optional[Any] = None,
        data: Optional[Any] = None,
        files: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Send HTTP request to specified server

        Used to send requests to a server different from base_url (e.g., Applets query server).

        Args:
            server_url: Target server URL
            path: Request path
            method: HTTP method
            json_data: JSON data
            data: Form data
            files: File data
            headers: Additional request headers

        Returns:
            Response data (automatically parsed as JSON)

        Raises:
            ApiError: Raised when API request fails
        """
        url = build_url(server_url, path)

        # Merge request headers
        request_headers = dict(self._default_headers)
        if headers:
            request_headers.update(headers)

        # If there's file upload, remove Content-Type (let httpx set it automatically)
        if files:
            request_headers.pop("Content-Type", None)

        try:
            response = await self._http_client.request(
                method=method,
                url=url,
                json=json_data,
                data=data,
                files=files,
                headers=request_headers,
            )

            # Check status code
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", response.text)
                except Exception:
                    error_message = response.text

                raise ApiError(
                    message=error_message,
                    status=response.status_code,
                    response=response.text
                )

            # Try to parse JSON
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return response.text

        except httpx.HTTPError as e:
            raise ApiError(
                message=str(e),
                status=0,
                response=None
            )

    def get_base_url(self) -> str:
        """Get base URL"""
        return self._base_url

    def get_default_headers(self) -> Dict[str, str]:
        """Get default request headers"""
        return dict(self._default_headers)

    async def close(self) -> None:
        """Close client and release resources"""
        await self._http_client.aclose()

    async def __aenter__(self) -> "OomolConnectClient":
        """Support async context manager"""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Support async context manager"""
        await self.close()
