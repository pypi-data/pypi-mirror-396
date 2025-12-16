# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Unix socket transport for Docker Engine API communication.

Author: A M (am@bbdevs.com)
Created At: 08 Nov 2025
"""

from __future__ import annotations

import os
from pathlib import Path

import httpx

from dockpycore.exceptions import DockerSDKError
from dockpycore.logging import get_logger


__all__ = ["UnixSocketTransport"]

logger = get_logger(__name__)


class UnixSocketTransport(httpx.AsyncHTTPTransport):
    """Extended HTTP transport for Unix socket communication.

    Extends httpx.AsyncHTTPTransport to add:
    - Socket path validation
    - Better error messages
    - Connection health monitoring
    - Docker-specific logging

    Usage:
        transport = UnixSocketTransport("/var/run/docker.sock")
        async with httpx.AsyncClient(transport=transport) as client:
            response = await client.get("http://localhost/version")
    """

    def __init__(
        self,
        socket_path: str = "/var/run/docker.sock",
        *,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 5.0,
    ):
        """Initialize Unix socket transport.

        Args:
            socket_path: Path to Docker Unix socket
            max_connections: Maximum number of connections in pool
            max_keepalive_connections: Maximum number of idle connections
            keepalive_expiry: Time to keep idle connections alive (seconds)

        Raises:
            DockerSDKError: If socket doesn't exist or is not accessible
        """
        self.socket_path = socket_path

        # Validate socket before initializing
        self._validate_socket()

        logger.info(
            "transport_init",
            socket_path=socket_path,
            max_connections=max_connections,
        )

        # Create limits object for connection pool
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        )

        # Initialize parent with Unix socket
        super().__init__(
            uds=socket_path,
            limits=limits,
        )

    def _validate_socket(self) -> None:
        """Validate that socket exists and is accessible.

        Raises:
            DockerSDKError: If socket validation fails
        """
        socket_file = Path(self.socket_path)

        # Check if socket exists
        if not socket_file.exists():
            logger.error(
                "socket_not_found",
                socket_path=self.socket_path,
            )
            raise DockerSDKError(
                f"Docker socket not found at {self.socket_path}. Is Docker daemon running?",
                operation="socket_validation",
                context={"socket_path": self.socket_path},
            )

        # Check if it's a socket
        if not socket_file.is_socket():
            logger.error(
                "not_a_socket",
                socket_path=self.socket_path,
            )
            raise DockerSDKError(
                f"Path {self.socket_path} exists but is not a socket",
                operation="socket_validation",
                context={"socket_path": self.socket_path},
            )

        # Check if socket is readable/writable
        if not os.access(self.socket_path, os.R_OK | os.W_OK):
            logger.error(
                "socket_permission_denied",
                socket_path=self.socket_path,
            )
            raise DockerSDKError(
                f"Permission denied accessing {self.socket_path}. Try running with sudo or add user to docker group.",
                operation="socket_validation",
                context={"socket_path": self.socket_path},
            )

        logger.debug(
            "socket_validated",
            socket_path=self.socket_path,
        )

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Handle async request with enhanced error handling.

        Args:
            request: HTTP request to send

        Returns:
            HTTP response

        Raises:
            DockerSDKError: If connection fails
        """
        try:
            logger.debug(
                "transport_request",
                method=request.method,
                url=str(request.url),
            )

            response = await super().handle_async_request(request)

            logger.debug(
                "transport_response",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
            )

            return response

        except httpx.ConnectError as e:
            logger.error(
                "transport_connect_error",
                method=request.method,
                url=str(request.url),
                error=str(e),
            )
            raise DockerSDKError(
                f"Failed to connect to Docker daemon at {self.socket_path}. Is Docker daemon running?",
                operation="socket_connect",
                context={
                    "socket_path": self.socket_path,
                    "method": request.method,
                    "url": str(request.url),
                },
            ) from e

        except httpx.TimeoutException as e:
            logger.error(
                "transport_timeout",
                method=request.method,
                url=str(request.url),
                error=str(e),
            )
            raise DockerSDKError(
                f"Request to Docker daemon timed out: {request.method} {request.url}",
                operation="socket_request",
                context={
                    "socket_path": self.socket_path,
                    "method": request.method,
                    "url": str(request.url),
                },
            ) from e
