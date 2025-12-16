# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Network management operations.

Author: A M (am@bbdevs.com)
Created At: 08 Nov 2025
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dockpycore.exceptions import APIError, NotFound
from dockpycore.logging import get_logger, log_context


if TYPE_CHECKING:
    from .http_client import DockerHTTPClient

__all__ = ["NetworkManager"]


logger = get_logger(__name__)


class NetworkManager:
    """Manage Docker networks.

    Provides methods for network lifecycle management and inspection.

    Usage:
        async with AsyncDockerClient() as client:
            # Create network
            network = await client.networks.create("my-network", driver="bridge")

            # List networks
            networks = await client.networks.list()

            # Remove network
            await client.networks.remove(network.id)
    """

    def __init__(self, client: DockerHTTPClient):
        """Initialize network manager.

        Args:
            client: HTTP client for API communication
        """
        self._client = client
        self.logger = get_logger("dockpysdk.networks")

    async def create(
        self,
        name: str,
        *,
        driver: str = "bridge",
        driver_opts: dict[str, str] | None = None,
        ipam: dict[str, Any] | None = None,
        labels: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new network.

        Args:
            name: Network name
            driver: Network driver (default: bridge)
            driver_opts: Driver-specific options
            ipam: IPAM configuration
            labels: Network labels
            **kwargs: Additional network config

        Returns:
            Network creation response with network ID

        Example:
            network = await manager.create(
                "my-network",
                driver="bridge",
                labels={"com.example.project": "myapp"},
            )
        """
        with log_context(operation="network_create", name=name):
            self.logger.info("network_create_start", name=name, driver=driver)

            # Build network config
            config: dict[str, Any] = {
                "Name": name,
                "Driver": driver,
            }

            if driver_opts:
                config["Options"] = driver_opts
            if ipam:
                config["IPAM"] = ipam
            if labels:
                config["Labels"] = labels

            # Add any additional config
            config.update(kwargs)

            # Create network
            response = await self._client.post("/networks/create", json=config)
            data = response.json()

            network_id = data.get("Id", "")
            if not network_id:
                msg = "Network creation response missing ID"
                raise APIError(msg, response=response)

            self.logger.info(
                "network_created",
                network_id=network_id,
                name=name,
            )

            return data

    async def list(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """List networks.

        Args:
            filters: Filter options (e.g., {"name": ["my-network"]})

        Returns:
            List of network information dictionaries
        """
        with log_context(operation="network_list"):
            self.logger.debug("network_list_start", filters=filters)

            params: dict[str, Any] = {}
            if filters:
                params["filters"] = filters

            response = await self._client.get("/networks", params=params)
            networks = response.json()

            self.logger.info("network_list_success", count=len(networks))

            return networks

    async def inspect(self, network_id: str) -> dict[str, Any]:
        """Inspect a network.

        Args:
            network_id: Network ID or name

        Returns:
            Network details dictionary

        Raises:
            NotFound: If network not found
        """
        with log_context(operation="network_inspect", network_id=network_id):
            self.logger.debug("network_inspect_start", network_id=network_id)

            try:
                response = await self._client.get(f"/networks/{network_id}")
                network = response.json()

                self.logger.info("network_inspect_success", network_id=network_id)

                return network
            except APIError as e:
                if e.status_code == 404:
                    msg = f"Network not found: {network_id}"
                    raise NotFound(msg) from e
                raise

    async def remove(self, network_id: str, force: bool = False) -> None:
        """Remove a network.

        Args:
            network_id: Network ID or name
            force: Force removal even if in use

        Raises:
            NotFound: If network not found
            APIError: If network is in use and force=False
        """
        with log_context(operation="network_remove", network_id=network_id):
            self.logger.info("network_remove_start", network_id=network_id, force=force)

            params: dict[str, Any] = {}
            if force:
                params["force"] = "1"

            try:
                await self._client.delete(f"/networks/{network_id}", params=params)

                self.logger.info("network_removed", network_id=network_id)
            except APIError as e:
                if e.status_code == 404:
                    msg = f"Network not found: {network_id}"
                    raise NotFound(msg) from e
                raise

    async def prune(self, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """Prune unused networks.

        Args:
            filters: Filter options

        Returns:
            Prune report with networks deleted and space reclaimed
        """
        with log_context(operation="network_prune"):
            self.logger.info("network_prune_start", filters=filters)

            params: dict[str, Any] = {}
            if filters:
                params["filters"] = filters

            response = await self._client.post("/networks/prune", params=params)
            report = response.json()

            networks_deleted = report.get("NetworksDeleted", [])
            self.logger.info(
                "network_prune_success",
                networks_deleted=len(networks_deleted),
            )

            return report
