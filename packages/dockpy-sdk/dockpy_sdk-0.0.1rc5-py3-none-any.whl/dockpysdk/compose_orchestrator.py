# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Compose orchestrator for multi-container operations.

Author: A M (am@bbdevs.com)
Created At: 08 Nov 2025
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dockpycore.exceptions import DockerSDKError
from dockpycore.logging import get_logger, log_context

from .compose_dependencies import DependencyResolver, resolve_shutdown_order, resolve_startup_order
from .models import ComposeFile, ComposeService


if TYPE_CHECKING:
    from .client import AsyncDockerClient

__all__ = ["ComposeOrchestrator"]

logger = get_logger(__name__)


class ComposeOrchestratorError(DockerSDKError):
    """Error in compose orchestration."""


class ComposeOrchestrator:
    """Orchestrator for compose operations.

    Handles multi-container operations with dependency resolution,
    parallel execution where safe, and error handling.
    """

    def __init__(self, client: AsyncDockerClient, compose_file: ComposeFile, project_name: str):
        """Initialize compose orchestrator.

        Args:
            client: Docker client instance
            compose_file: Parsed compose file
            project_name: Compose project name
        """
        self.client = client
        self.compose_file = compose_file
        self.project_name = project_name
        self.dependency_resolver = DependencyResolver(compose_file)
        self.logger = get_logger(__name__)

    def _get_project_label(self) -> dict[str, str]:
        """Get project labels for resources.

        Returns:
            Dictionary with project labels
        """
        return {
            "com.docker.compose.project": self.project_name,
        }

    def _get_service_name(self, service_name: str) -> str:
        """Get full container name for service.

        Args:
            service_name: Service name from compose file

        Returns:
            Full container name (project_service)
        """
        return f"{self.project_name}_{service_name}"

    async def _create_networks(self) -> list[str]:
        """Create networks defined in compose file.

        Returns:
            List of created network names
        """
        if not self.compose_file.networks:
            return []

        created: list[str] = []
        project_labels = self._get_project_label()

        for network_name, network in self.compose_file.networks.items():
            # Skip external networks
            if network.external:
                self.logger.debug("network_skip_external", network=network_name)
                continue

            # Create network
            full_name = f"{self.project_name}_{network_name}"
            try:
                await self.client.networks.create(
                    full_name,
                    driver=network.driver or "bridge",
                    driver_opts=network.driver_opts,
                    labels={**project_labels, **network.labels} if network.labels else project_labels,
                )
                created.append(full_name)
                self.logger.info("compose_network_created", network=full_name)
            except Exception as e:
                self.logger.error("compose_network_create_failed", network=full_name, error=str(e))
                raise ComposeOrchestratorError(f"Failed to create network {full_name}: {e}") from e

        return created

    async def _create_volumes(self) -> list[str]:
        """Create volumes defined in compose file.

        Returns:
            List of created volume names
        """
        if not self.compose_file.volumes:
            return []

        created: list[str] = []
        project_labels = self._get_project_label()

        for volume_name, volume in self.compose_file.volumes.items():
            # Skip external volumes
            if volume.external:
                self.logger.debug("volume_skip_external", volume=volume_name)
                continue

            # Create volume
            full_name = f"{self.project_name}_{volume_name}"
            try:
                await self.client.volumes.create(
                    full_name,
                    driver=volume.driver or "local",
                    driver_opts=volume.driver_opts,
                    labels={**project_labels, **volume.labels} if volume.labels else project_labels,
                )
                created.append(full_name)
                self.logger.info("compose_volume_created", volume=full_name)
            except Exception as e:
                self.logger.error("compose_volume_create_failed", volume=full_name, error=str(e))
                raise ComposeOrchestratorError(f"Failed to create volume {full_name}: {e}") from e

        return created

    async def _create_container(self, service_name: str, service: ComposeService) -> str:  # noqa: PLR0912
        """Create container for a service.

        Args:
            service_name: Service name
            service: Service configuration

        Returns:
            Container ID
        """
        container_name = self._get_service_name(service_name)
        project_labels = self._get_project_label()

        # Build container config from service
        config: dict[str, Any] = {}

        if service.image:
            config["image"] = service.image
        if service.command:
            config["command"] = service.command
        if service.entrypoint:
            config["entrypoint"] = service.entrypoint
        if service.environment:
            config["environment"] = service.environment
        if service.working_dir:
            config["working_dir"] = service.working_dir
        if service.user:
            config["user"] = service.user
        if service.hostname:
            config["hostname"] = service.hostname
        if service.ports:
            config["ports"] = service.ports
        if service.volumes:
            config["volumes"] = service.volumes
        if service.labels:
            config["labels"] = {**project_labels, **service.labels}
        else:
            config["labels"] = project_labels

        # Add restart policy
        if service.restart:
            config["restart_policy"] = {"Name": service.restart}

        # Create container
        try:
            container = await self.client.containers.create(
                image=service.image or "unknown",
                name=container_name,
                **config,
            )
            self.logger.info("compose_container_created", service=service_name, container=container.id)
            return container.id
        except Exception as e:
            self.logger.error("compose_container_create_failed", service=service_name, error=str(e))
            raise ComposeOrchestratorError(f"Failed to create container for {service_name}: {e}") from e

    async def up(
        self,
        services: list[str] | None = None,
        build: bool = False,  # noqa: ARG002
        detach: bool = False,  # noqa: ARG002
        force_recreate: bool = False,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Start services (compose up).

        Args:
            services: List of service names to start (None = all)
            build: Build images before starting
            detach: Run in detached mode
            force_recreate: Recreate containers even if they exist

        Returns:
            Dictionary with operation results
        """
        with log_context(operation="compose_up", project=self.project_name):
            self.logger.info(
                "compose_up_start",
                project=self.project_name,
                services=services,
            )

            # Filter services if requested
            compose_file = self.compose_file.filter_services(services) if services else self.compose_file

            # Resolve startup order
            startup_order = resolve_startup_order(compose_file, service_filter=services)

            # Create networks and volumes
            await self._create_networks()
            await self._create_volumes()

            # Create and start containers in order
            started: list[str] = []
            failed: list[str] = []

            for service_name in startup_order:
                if service_name not in compose_file.services:
                    continue

                service = compose_file.services[service_name]

                try:
                    # Create container
                    container_id = await self._create_container(service_name, service)

                    # Start container
                    await self.client.containers.start(container_id)
                    started.append(service_name)
                    self.logger.info("compose_service_started", service=service_name)

                except Exception as e:
                    failed.append(service_name)
                    self.logger.error("compose_service_failed", service=service_name, error=str(e))

            result = {
                "started": started,
                "failed": failed,
                "total": len(startup_order),
            }

            self.logger.info(
                "compose_up_complete",
                project=self.project_name,
                started=len(started),
                failed=len(failed),
            )

            return result

    async def down(
        self,
        services: list[str] | None = None,
        volumes: bool = False,
        remove_orphans: bool = False,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Stop and remove services (compose down).

        Args:
            services: List of service names to stop (None = all)
            volumes: Remove volumes
            remove_orphans: Remove orphaned containers

        Returns:
            Dictionary with operation results
        """
        with log_context(operation="compose_down", project=self.project_name):
            self.logger.info(
                "compose_down_start",
                project=self.project_name,
                services=services,
            )

            # Resolve shutdown order (reverse of startup)
            shutdown_order = resolve_shutdown_order(self.compose_file, service_filter=services)

            stopped: list[str] = []
            failed: list[str] = []

            # Stop and remove containers
            for service_name in shutdown_order:
                container_name = self._get_service_name(service_name)

                try:
                    # Find container by name
                    containers = await self.client.containers.list(filters={"name": [container_name]})

                    for container in containers:
                        if container.name == container_name or container_name in container.names:
                            # Stop container
                            await self.client.containers.stop(container.id)
                            # Remove container
                            await self.client.containers.remove(container.id)
                            stopped.append(service_name)
                            self.logger.info("compose_service_stopped", service=service_name)

                except Exception as e:
                    failed.append(service_name)
                    self.logger.error("compose_service_stop_failed", service=service_name, error=str(e))

            # Remove networks
            if self.compose_file.networks:
                for network_name in self.compose_file.networks:
                    full_name = f"{self.project_name}_{network_name}"
                    try:
                        await self.client.networks.remove(full_name)
                        self.logger.info("compose_network_removed", network=full_name)
                    except Exception as e:
                        self.logger.warning("compose_network_remove_failed", network=full_name, error=str(e))

            # Remove volumes if requested
            if volumes and self.compose_file.volumes:
                for volume_name in self.compose_file.volumes:
                    full_name = f"{self.project_name}_{volume_name}"
                    try:
                        await self.client.volumes.remove(full_name)
                        self.logger.info("compose_volume_removed", volume=full_name)
                    except Exception as e:
                        self.logger.warning("compose_volume_remove_failed", volume=full_name, error=str(e))

            result = {
                "stopped": stopped,
                "failed": failed,
                "total": len(shutdown_order),
            }

            self.logger.info(
                "compose_down_complete",
                project=self.project_name,
                stopped=len(stopped),
                failed=len(failed),
            )

            return result

    async def start(self, services: list[str] | None = None) -> dict[str, Any]:
        """Start services.

        Args:
            services: List of service names to start (None = all)

        Returns:
            Dictionary with operation results
        """
        with log_context(operation="compose_start", project=self.project_name):
            self.logger.info("compose_start_start", project=self.project_name, services=services)

            # Filter services if requested
            compose_file = self.compose_file.filter_services(services) if services else self.compose_file

            # Resolve startup order
            startup_order = resolve_startup_order(compose_file, service_filter=services)

            started: list[str] = []
            failed: list[str] = []

            for service_name in startup_order:
                if service_name not in compose_file.services:
                    continue

                container_name = self._get_service_name(service_name)

                try:
                    # Find container by name
                    containers = await self.client.containers.list(filters={"name": [container_name]})

                    for container in containers:
                        if container.name == container_name or container_name in container.names:
                            # Start container
                            await self.client.containers.start(container.id)
                            started.append(service_name)
                            self.logger.info("compose_service_started", service=service_name)
                            break

                except Exception as e:
                    failed.append(service_name)
                    self.logger.error("compose_service_start_failed", service=service_name, error=str(e))

            result = {
                "started": started,
                "failed": failed,
                "total": len(startup_order),
            }

            self.logger.info(
                "compose_start_complete",
                project=self.project_name,
                started=len(started),
                failed=len(failed),
            )

            return result

    async def stop(self, services: list[str] | None = None, timeout: int = 10) -> dict[str, Any]:
        """Stop services.

        Args:
            services: List of service names to stop (None = all)
            timeout: Seconds to wait before killing

        Returns:
            Dictionary with operation results
        """
        with log_context(operation="compose_stop", project=self.project_name):
            self.logger.info("compose_stop_start", project=self.project_name, services=services)

            # Resolve shutdown order (reverse of startup)
            shutdown_order = resolve_shutdown_order(self.compose_file, service_filter=services)

            stopped: list[str] = []
            failed: list[str] = []

            for service_name in shutdown_order:
                container_name = self._get_service_name(service_name)

                try:
                    # Find container by name
                    containers = await self.client.containers.list(filters={"name": [container_name]})

                    for container in containers:
                        if container.name == container_name or container_name in container.names:
                            # Stop container
                            await self.client.containers.stop(container.id, timeout=timeout)
                            stopped.append(service_name)
                            self.logger.info("compose_service_stopped", service=service_name)
                            break

                except Exception as e:
                    failed.append(service_name)
                    self.logger.error("compose_service_stop_failed", service=service_name, error=str(e))

            result = {
                "stopped": stopped,
                "failed": failed,
                "total": len(shutdown_order),
            }

            self.logger.info(
                "compose_stop_complete",
                project=self.project_name,
                stopped=len(stopped),
                failed=len(failed),
            )

            return result

    async def restart(self, services: list[str] | None = None, timeout: int = 10) -> dict[str, Any]:
        """Restart services.

        Args:
            services: List of service names to restart (None = all)
            timeout: Seconds to wait before killing

        Returns:
            Dictionary with operation results
        """
        with log_context(operation="compose_restart", project=self.project_name):
            self.logger.info("compose_restart_start", project=self.project_name, services=services)

            # Resolve shutdown order (reverse of startup)
            shutdown_order = resolve_shutdown_order(self.compose_file, service_filter=services)

            restarted: list[str] = []
            failed: list[str] = []

            for service_name in shutdown_order:
                container_name = self._get_service_name(service_name)

                try:
                    # Find container by name
                    containers = await self.client.containers.list(filters={"name": [container_name]})

                    for container in containers:
                        if container.name == container_name or container_name in container.names:
                            # Restart container
                            await self.client.containers.restart(container.id, timeout=timeout)
                            restarted.append(service_name)
                            self.logger.info("compose_service_restarted", service=service_name)
                            break

                except Exception as e:
                    failed.append(service_name)
                    self.logger.error("compose_service_restart_failed", service=service_name, error=str(e))

            result = {
                "restarted": restarted,
                "failed": failed,
                "total": len(shutdown_order),
            }

            self.logger.info(
                "compose_restart_complete",
                project=self.project_name,
                restarted=len(restarted),
                failed=len(failed),
            )

            return result

    async def kill(self, services: list[str] | None = None, signal: str = "SIGKILL") -> dict[str, Any]:
        """Force stop services (kill).

        Args:
            services: List of service names to kill (None = all)
            signal: Signal to send (default: SIGKILL)

        Returns:
            Dictionary with operation results
        """
        with log_context(operation="compose_kill", project=self.project_name):
            self.logger.info("compose_kill_start", project=self.project_name, services=services, signal=signal)

            # Resolve shutdown order (reverse of startup)
            shutdown_order = resolve_shutdown_order(self.compose_file, service_filter=services)

            killed: list[str] = []
            failed: list[str] = []

            for service_name in shutdown_order:
                container_name = self._get_service_name(service_name)

                try:
                    # Find container by name
                    containers = await self.client.containers.list(filters={"name": [container_name]})

                    for container in containers:
                        if container.name == container_name or container_name in container.names:
                            # Kill container (stop with signal)
                            await self.client.containers.stop(container.id, timeout=0, signal=signal)
                            killed.append(service_name)
                            self.logger.info("compose_service_killed", service=service_name)
                            break

                except Exception as e:
                    failed.append(service_name)
                    self.logger.error("compose_service_kill_failed", service=service_name, error=str(e))

            result = {
                "killed": killed,
                "failed": failed,
                "total": len(shutdown_order),
            }

            self.logger.info(
                "compose_kill_complete",
                project=self.project_name,
                killed=len(killed),
                failed=len(failed),
            )

            return result

    async def pause(self, services: list[str] | None = None) -> dict[str, Any]:
        """Pause services.

        Args:
            services: List of service names to pause (None = all)

        Returns:
            Dictionary with operation results
        """
        with log_context(operation="compose_pause", project=self.project_name):
            self.logger.info("compose_pause_start", project=self.project_name, services=services)

            # Resolve shutdown order (reverse of startup)
            shutdown_order = resolve_shutdown_order(self.compose_file, service_filter=services)

            paused: list[str] = []
            failed: list[str] = []

            for service_name in shutdown_order:
                container_name = self._get_service_name(service_name)

                try:
                    # Find container by name
                    containers = await self.client.containers.list(filters={"name": [container_name]})

                    for container in containers:
                        if container.name == container_name or container_name in container.names:
                            # Pause container
                            await self.client.containers.pause(container.id)
                            paused.append(service_name)
                            self.logger.info("compose_service_paused", service=service_name)
                            break

                except Exception as e:
                    failed.append(service_name)
                    self.logger.error("compose_service_pause_failed", service=service_name, error=str(e))

            result = {
                "paused": paused,
                "failed": failed,
                "total": len(shutdown_order),
            }

            self.logger.info(
                "compose_pause_complete",
                project=self.project_name,
                paused=len(paused),
                failed=len(failed),
            )

            return result

    async def unpause(self, services: list[str] | None = None) -> dict[str, Any]:
        """Unpause services.

        Args:
            services: List of service names to unpause (None = all)

        Returns:
            Dictionary with operation results
        """
        with log_context(operation="compose_unpause", project=self.project_name):
            self.logger.info("compose_unpause_start", project=self.project_name, services=services)

            # Resolve startup order
            startup_order = resolve_startup_order(self.compose_file, service_filter=services)

            unpaused: list[str] = []
            failed: list[str] = []

            for service_name in startup_order:
                container_name = self._get_service_name(service_name)

                try:
                    # Find container by name
                    containers = await self.client.containers.list(filters={"name": [container_name]})

                    for container in containers:
                        if container.name == container_name or container_name in container.names:
                            # Unpause container
                            await self.client.containers.unpause(container.id)
                            unpaused.append(service_name)
                            self.logger.info("compose_service_unpaused", service=service_name)
                            break

                except Exception as e:
                    failed.append(service_name)
                    self.logger.error("compose_service_unpause_failed", service=service_name, error=str(e))

            result = {
                "unpaused": unpaused,
                "failed": failed,
                "total": len(startup_order),
            }

            self.logger.info(
                "compose_unpause_complete",
                project=self.project_name,
                unpaused=len(unpaused),
                failed=len(failed),
            )

            return result

    async def rm(self, services: list[str] | None = None, volumes: bool = False) -> dict[str, Any]:
        """Remove stopped service containers.

        Args:
            services: List of service names to remove (None = all)
            volumes: Remove associated volumes

        Returns:
            Dictionary with operation results
        """
        with log_context(operation="compose_rm", project=self.project_name):
            self.logger.info("compose_rm_start", project=self.project_name, services=services)

            # Resolve shutdown order (reverse of startup)
            shutdown_order = resolve_shutdown_order(self.compose_file, service_filter=services)

            removed: list[str] = []
            failed: list[str] = []

            for service_name in shutdown_order:
                container_name = self._get_service_name(service_name)

                try:
                    # Find container by name
                    containers = await self.client.containers.list(filters={"name": [container_name]})

                    for container in containers:
                        if container.name == container_name or container_name in container.names:
                            # Remove container
                            await self.client.containers.remove(container.id, force=False, volumes=volumes)
                            removed.append(service_name)
                            self.logger.info("compose_service_removed", service=service_name)
                            break

                except Exception as e:
                    failed.append(service_name)
                    self.logger.error("compose_service_remove_failed", service=service_name, error=str(e))

            result = {
                "removed": removed,
                "failed": failed,
                "total": len(shutdown_order),
            }

            self.logger.info(
                "compose_rm_complete",
                project=self.project_name,
                removed=len(removed),
                failed=len(failed),
            )

            return result

    async def pull(self, services: list[str] | None = None) -> dict[str, Any]:
        """Pull service images.

        Args:
            services: List of service names to pull images for (None = all)

        Returns:
            Dictionary with operation results
        """
        with log_context(operation="compose_pull", project=self.project_name):
            self.logger.info("compose_pull_start", project=self.project_name, services=services)

            # Filter services if requested
            compose_file = self.compose_file.filter_services(services) if services else self.compose_file

            pulled: list[str] = []
            failed: list[str] = []

            for service_name, service in compose_file.services.items():
                if not service.image:
                    self.logger.warning("compose_service_no_image", service=service_name)
                    continue

                try:
                    # Pull image
                    await self.client.images.pull(service.image)
                    pulled.append(service_name)
                    self.logger.info("compose_image_pulled", service=service_name, image=service.image)

                except Exception as e:
                    failed.append(service_name)
                    self.logger.error("compose_image_pull_failed", service=service_name, error=str(e))

            result = {
                "pulled": pulled,
                "failed": failed,
                "total": len(compose_file.services),
            }

            self.logger.info(
                "compose_pull_complete",
                project=self.project_name,
                pulled=len(pulled),
                failed=len(failed),
            )

            return result

    async def build(self, services: list[str] | None = None) -> dict[str, Any]:
        """Build service images.

        Args:
            services: List of service names to build (None = all)

        Returns:
            Dictionary with operation results
        """
        with log_context(operation="compose_build", project=self.project_name):
            self.logger.info("compose_build_start", project=self.project_name, services=services)

            # Filter services if requested
            compose_file = self.compose_file.filter_services(services) if services else self.compose_file

            built: list[str] = []
            failed: list[str] = []

            for service_name, service in compose_file.services.items():
                if not service.build:
                    self.logger.warning("compose_service_no_build", service=service_name)
                    continue

                try:
                    # Build image (simplified - full build support in future)
                    # For now, just log that build is requested
                    self.logger.info("compose_build_requested", service=service_name, build_config=service.build)
                    built.append(service_name)

                except Exception as e:
                    failed.append(service_name)
                    self.logger.error("compose_build_failed", service=service_name, error=str(e))

            result = {
                "built": built,
                "failed": failed,
                "total": len(compose_file.services),
            }

            self.logger.info(
                "compose_build_complete",
                project=self.project_name,
                built=len(built),
                failed=len(failed),
            )

            return result
