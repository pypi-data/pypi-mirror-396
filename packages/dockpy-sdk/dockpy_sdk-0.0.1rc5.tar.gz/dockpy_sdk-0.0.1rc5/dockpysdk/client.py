# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Main Docker SDK client.

Author: A M (am@bbdevs.com)
Created At: 08 Nov 2025
"""

from __future__ import annotations

from dockpycore.logging import get_logger

from .containers import ContainerManager
from .http_client import DockerHTTPClient
from .images import ImageManager
from .networks import NetworkManager
from .transport import UnixSocketTransport
from .volumes import VolumeManager


__all__ = ["AsyncDockerClient"]

logger = get_logger(__name__)


class AsyncDockerClient:
    """Async Docker SDK client - main entry point.

    Provides async interface to Docker Engine API via Unix socket.

    Usage:
        async with AsyncDockerClient() as client:
            # Check daemon is accessible
            if await client.ping():
                print("Docker daemon is running")

            # Get version info
            version = await client.version()
            print(f"Docker version: {version['Version']}")

            # Container operations
            container = await client.containers.create("nginx", name="web")
            await client.containers.start(container.id)
            containers = await client.containers.list()

            # Image operations
            image = await client.images.pull("nginx:latest")
            images = await client.images.list()

            # Network operations
            network = await client.networks.create("my-network")
            networks = await client.networks.list()

            # Volume operations
            volume = await client.volumes.create("my-volume")
            volumes = await client.volumes.list()

    Args:
        base_url: Base URL for API (default: http://localhost)
        socket_path: Path to Docker Unix socket
        api_version: Docker API version (default: v1.43)
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        base_url: str = "http://localhost",
        socket_path: str = "/var/run/docker.sock",
        api_version: str = "v1.43",
        timeout: float = 60.0,
    ):
        """Initialize Docker client.

        Args:
            base_url: Base URL for API
            socket_path: Path to Docker Unix socket
            api_version: Docker API version
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.socket_path = socket_path
        self.api_version = api_version
        self.timeout = timeout

        logger.info(
            "client_init",
            socket_path=socket_path,
            api_version=api_version,
            timeout=timeout,
        )

        # Create transport
        transport = UnixSocketTransport(socket_path)

        # Create HTTP client
        self._http_client = DockerHTTPClient(
            transport=transport,
            base_url=f"{base_url}/{api_version}",
            timeout=timeout,
        )

        # Initialize resource managers
        self.containers = ContainerManager(self._http_client)
        self.images = ImageManager(self._http_client)
        self.networks = NetworkManager(self._http_client)
        self.volumes = VolumeManager(self._http_client)

    async def __aenter__(self):
        """Enter async context manager."""
        logger.debug("client_enter")
        await self._http_client.__aenter__()
        return self

    async def __aexit__(self, *args):
        """Exit async context manager."""
        logger.debug("client_exit")
        await self._http_client.__aexit__(*args)

    async def ping(self) -> bool:
        """Check if Docker daemon is accessible.

        Returns:
            True if daemon is accessible, False otherwise

        Example:
            async with AsyncDockerClient() as client:
                if await client.ping():
                    print("Docker is running!")
        """
        try:
            response = await self._http_client.get("/_ping")
            success = response.status_code == 200

            logger.info(
                "ping_result",
                success=success,
                status_code=response.status_code,
            )

            return success

        except Exception as e:
            logger.error(
                "ping_failed",
                error=str(e),
            )
            return False

    async def version(self) -> dict:
        """Get Docker daemon version information.

        Returns:
            Dictionary with version information

        Example:
            async with AsyncDockerClient() as client:
                version = await client.version()
                print(f"Docker version: {version['Version']}")
                print(f"API version: {version['ApiVersion']}")
        """
        response = await self._http_client.get("/version")
        version_data = response.json()

        logger.info(
            "version_retrieved",
            version=version_data.get("Version"),
            api_version=version_data.get("ApiVersion"),
        )

        return version_data

    async def info(self) -> dict:
        """Get Docker daemon system information.

        Returns:
            Dictionary with system information

        Example:
            async with AsyncDockerClient() as client:
                info = await client.info()
                print(f"Containers: {info['Containers']}")
                print(f"Images: {info['Images']}")
        """
        response = await self._http_client.get("/info")
        info_data = response.json()

        logger.info(
            "info_retrieved",
            containers=info_data.get("Containers"),
            images=info_data.get("Images"),
        )

        return info_data

    async def df(self) -> dict:
        """Get Docker disk usage information.

        Returns:
            Dictionary with disk usage information for images, containers, volumes, and build cache

        Example:
            async with AsyncDockerClient() as client:
                df_data = await client.df()
                print(f"Images: {df_data['Images']}")
                print(f"Containers: {df_data['Containers']}")
        """
        response = await self._http_client.get("/system/df")
        df_data = response.json()

        logger.info(
            "df_retrieved",
            images_count=len(df_data.get("Images", [])),
            containers_count=len(df_data.get("Containers", [])),
            volumes_count=len(df_data.get("Volumes", [])),
        )

        return df_data
