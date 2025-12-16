# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Extended HTTP client for Docker Engine API.

Author: A M (am@bbdevs.com)
Created At: 08 Nov 2025
"""

from __future__ import annotations

import time

import httpx

from dockpycore.exceptions import APIError, ContainerError, NotFound
from dockpycore.logging import get_logger, log_context


__all__ = ["DockerHTTPClient"]

logger = get_logger(__name__)


class DockerHTTPClient(httpx.AsyncClient):
    """Extended HTTP client with Docker-specific features.

    Extends httpx.AsyncClient to add:
    - Automatic HTTP error → SDK exception conversion
    - Request/response logging with structlog
    - Request ID tracking
    - Duration measurement

    Usage:
        transport = UnixSocketTransport()
        async with DockerHTTPClient(transport=transport, base_url="http://localhost/v1.43") as client:
            response = await client.get("/containers/json")
    """

    def __init__(self, *args, **kwargs):
        """Initialize Docker HTTP client.

        Accepts all httpx.AsyncClient arguments plus Docker-specific config.
        """
        super().__init__(*args, **kwargs)
        self.logger = get_logger("dockpysdk.http")

    async def request(
        self,
        method: str,
        url: httpx.URL | str,
        **kwargs,
    ) -> httpx.Response:
        """Send HTTP request with logging and error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            HTTP response

        Raises:
            NotFound: If resource not found (404)
            ContainerError: If container operation fails (409)
            ImageError: If image operation fails
            APIError: If API returns error status
        """
        start_time = time.time()

        # Log request
        with log_context(
            operation="http_request",
            method=method,
            url=str(url),
        ):
            self.logger.debug(
                "request_start",
                method=method,
                url=str(url),
            )

            try:
                # Make request
                response = await super().request(method, url, **kwargs)

                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Log response
                self.logger.debug(
                    "request_complete",
                    method=method,
                    url=str(url),
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                )

                # Check for errors
                if response.status_code >= 400:
                    self._handle_error_response(response, method, url)

                return response

            except httpx.HTTPError as e:
                duration_ms = (time.time() - start_time) * 1000
                self.logger.error(
                    "request_failed",
                    method=method,
                    url=str(url),
                    duration_ms=duration_ms,
                    error=str(e),
                )
                raise

    def _handle_error_response(
        self,
        response: httpx.Response,
        method: str,
        url: httpx.URL | str,
    ) -> None:
        """Convert HTTP error response to SDK exception.

        Args:
            response: HTTP response with error status
            method: HTTP method
            url: Request URL

        Raises:
            NotFound: If 404
            ContainerError: If 409 (conflict)
            APIError: For other error statuses
        """
        status_code = response.status_code

        # Try to parse error message from response
        try:
            error_data = response.json()
            message = error_data.get("message", response.text)
        except Exception:
            message = response.text or f"HTTP {status_code}"

        # Log error
        self.logger.error(
            "api_error",
            method=method,
            url=str(url),
            status_code=status_code,
            message=message,
        )

        # Convert to appropriate exception
        if status_code == 404:
            raise NotFound(
                resource_type=self._extract_resource_type(url),
                resource_id=self._extract_resource_id(url),
            )

        if status_code == 409:
            # Conflict - usually container/image already exists or in use
            raise ContainerError(
                message,
                container_id=self._extract_resource_id(url),
            )

        # Generic API error
        raise APIError(
            message,
            status_code=status_code,
            response={"method": method, "url": str(url)},
        )

    def _extract_resource_type(self, url: httpx.URL | str) -> str:
        """Extract resource type from URL path.

        Args:
            url: Request URL

        Returns:
            Resource type (container, image, network, volume)
        """
        url_str = str(url)

        if "/containers/" in url_str:
            return "container"
        if "/images/" in url_str:
            return "image"
        if "/networks/" in url_str:
            return "network"
        if "/volumes/" in url_str:
            return "volume"
        return "resource"

    def _extract_resource_id(self, url: httpx.URL | str) -> str | None:
        """Extract resource ID from URL path.

        Args:
            url: Request URL

        Returns:
            Resource ID or None
        """
        url_str = str(url)
        parts = url_str.split("/")

        # Look for ID after resource type
        for i, part in enumerate(parts):
            if part in ("containers", "images", "networks", "volumes") and i + 1 < len(parts):
                return parts[i + 1]

        return None
