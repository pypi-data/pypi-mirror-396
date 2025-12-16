# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Volume management operations.

Author: A M (am@bbdevs.com)
Created At: 08 Nov 2025
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dockpycore.exceptions import APIError, NotFound
from dockpycore.logging import get_logger, log_context


if TYPE_CHECKING:
    from .http_client import DockerHTTPClient

__all__ = ["VolumeManager"]


logger = get_logger(__name__)


class VolumeManager:
    """Manage Docker volumes.

    Provides methods for volume lifecycle management and inspection.

    Usage:
        async with AsyncDockerClient() as client:
            # Create volume
            volume = await client.volumes.create("my-volume", driver="local")

            # List volumes
            volumes = await client.volumes.list()

            # Remove volume
            await client.volumes.remove(volume.name)
    """

    def __init__(self, client: DockerHTTPClient):
        """Initialize volume manager.

        Args:
            client: HTTP client for API communication
        """
        self._client = client
        self.logger = get_logger("dockpysdk.volumes")

    async def create(
        self,
        name: str,
        *,
        driver: str = "local",
        driver_opts: dict[str, str] | None = None,
        labels: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new volume.

        Args:
            name: Volume name
            driver: Volume driver (default: local)
            driver_opts: Driver-specific options
            labels: Volume labels
            **kwargs: Additional volume config

        Returns:
            Volume creation response with volume name

        Example:
            volume = await manager.create(
                "my-volume",
                driver="local",
                labels={"com.example.project": "myapp"},
            )
        """
        with log_context(operation="volume_create", name=name):
            self.logger.info("volume_create_start", name=name, driver=driver)

            # Build volume config
            config: dict[str, Any] = {
                "Name": name,
                "Driver": driver,
            }

            if driver_opts:
                config["DriverOpts"] = driver_opts
            if labels:
                config["Labels"] = labels

            # Add any additional config
            config.update(kwargs)

            # Create volume
            response = await self._client.post("/volumes/create", json=config)
            data = response.json()

            volume_name = data.get("Name", "")
            if not volume_name:
                msg = "Volume creation response missing name"
                raise APIError(msg, response=response)

            self.logger.info(
                "volume_created",
                volume_name=volume_name,
                name=name,
            )

            return data

    async def list(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """List volumes.

        Args:
            filters: Filter options (e.g., {"name": ["my-volume"]})

        Returns:
            List of volume information dictionaries
        """
        with log_context(operation="volume_list"):
            self.logger.debug("volume_list_start", filters=filters)

            params: dict[str, Any] = {}
            if filters:
                params["filters"] = filters

            response = await self._client.get("/volumes", params=params)
            data = response.json()

            volumes = data.get("Volumes", [])

            self.logger.info("volume_list_success", count=len(volumes))

            return volumes

    async def inspect(self, volume_name: str) -> dict[str, Any]:
        """Inspect a volume.

        Args:
            volume_name: Volume name

        Returns:
            Volume details dictionary

        Raises:
            NotFound: If volume not found
        """
        with log_context(operation="volume_inspect", volume_name=volume_name):
            self.logger.debug("volume_inspect_start", volume_name=volume_name)

            try:
                response = await self._client.get(f"/volumes/{volume_name}")
                volume = response.json()

                self.logger.info("volume_inspect_success", volume_name=volume_name)

                return volume
            except APIError as e:
                if e.status_code == 404:
                    msg = f"Volume not found: {volume_name}"
                    raise NotFound(msg) from e
                raise

    async def remove(self, volume_name: str, force: bool = False) -> None:
        """Remove a volume.

        Args:
            volume_name: Volume name
            force: Force removal even if in use

        Raises:
            NotFound: If volume not found
            APIError: If volume is in use and force=False
        """
        with log_context(operation="volume_remove", volume_name=volume_name):
            self.logger.info("volume_remove_start", volume_name=volume_name, force=force)

            params: dict[str, Any] = {}
            if force:
                params["force"] = "1"

            try:
                await self._client.delete(f"/volumes/{volume_name}", params=params)

                self.logger.info("volume_removed", volume_name=volume_name)
            except APIError as e:
                if e.status_code == 404:
                    msg = f"Volume not found: {volume_name}"
                    raise NotFound(msg) from e
                raise

    async def prune(self, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """Prune unused volumes.

        Args:
            filters: Filter options

        Returns:
            Prune report with volumes deleted and space reclaimed
        """
        with log_context(operation="volume_prune"):
            self.logger.info("volume_prune_start", filters=filters)

            params: dict[str, Any] = {}
            if filters:
                params["filters"] = filters

            response = await self._client.post("/volumes/prune", params=params)
            report = response.json()

            volumes_deleted = report.get("VolumesDeleted", [])
            space_reclaimed = report.get("SpaceReclaimed", 0)

            self.logger.info(
                "volume_prune_success",
                volumes_deleted=len(volumes_deleted),
                space_reclaimed=space_reclaimed,
            )

            return report
