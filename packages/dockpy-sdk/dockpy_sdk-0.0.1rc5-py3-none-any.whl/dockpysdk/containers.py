# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Container management operations.

Author: A M (am@bbdevs.com)
Created At: 08 Nov 2025
"""

from __future__ import annotations

import io
import json
import tarfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import TYPE_CHECKING, Any

from dockpycore.exceptions import NotFound
from dockpycore.logging import get_logger, log_context

from .build_formatter import format_exec_output, format_logs_stream
from .models import Container, ContainerInspect, ContainerStats


if TYPE_CHECKING:
    from .http_client import DockerHTTPClient


__all__ = ["ContainerManager"]

logger = get_logger(__name__)


class ContainerManager:
    """Manage Docker containers.

    Provides methods for container lifecycle management, inspection,
    and monitoring.

    Usage:
        async with AsyncDockerClient() as client:
            # Create container
            container = await client.containers.create("nginx", name="web")

            # Start container
            await client.containers.start(container.id)

            # List containers
            containers = await client.containers.list()

            # Stop and remove
            await client.containers.stop(container.id)
            await client.containers.remove(container.id)
    """

    def __init__(self, client: DockerHTTPClient):
        """Initialize container manager.

        Args:
            client: HTTP client for API communication
        """
        self._client = client
        self.logger = get_logger("dockpysdk.containers")

    async def create(  # noqa: PLR0912
        self,
        image: str,
        *,
        name: str | None = None,
        command: list[str] | str | None = None,
        entrypoint: list[str] | str | None = None,
        environment: dict[str, str] | list[str] | None = None,
        working_dir: str | None = None,
        user: str | None = None,
        hostname: str | None = None,
        labels: dict[str, str] | None = None,
        volumes: dict[str, dict[str, str]] | None = None,
        ports: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Container:
        """Create a new container.

        Args:
            image: Image name (e.g., "nginx:latest")
            name: Container name
            command: Command to run
            entrypoint: Entrypoint override
            environment: Environment variables
            working_dir: Working directory
            user: Username or UID
            hostname: Container hostname
            labels: Container labels
            volumes: Volume mappings
            ports: Port bindings
            network: Network to connect to
            **kwargs: Additional container config

        Returns:
            Created container

        Example:
            container = await manager.create(
                "nginx:latest",
                name="web",
                ports={"80/tcp": 8080},
                environment={"ENV": "prod"},
            )
        """
        with log_context(operation="container_create", image=image, name=name):
            self.logger.info("container_create_start", image=image, name=name)

            # Build container config
            config: dict[str, Any] = {
                "Image": image,
            }

            if name:
                config["name"] = name
            if command:
                config["Cmd"] = command if isinstance(command, list) else [command]
            if entrypoint:
                config["Entrypoint"] = entrypoint if isinstance(entrypoint, list) else [entrypoint]
            if environment:
                if isinstance(environment, dict):
                    config["Env"] = [f"{k}={v}" for k, v in environment.items()]
                else:
                    config["Env"] = environment
            if working_dir:
                config["WorkingDir"] = working_dir
            if user:
                config["User"] = user
            if hostname:
                config["Hostname"] = hostname
            if labels:
                config["Labels"] = labels
            if volumes:
                # Convert to Docker API format
                # Supports both bind mount format: {"/host": {"bind": "/container", "mode": "ro"}}
                # and anonymous volume format: {"/container": {}}
                binds = []
                volume_config = {}
                for host_path, mount_config in volumes.items():
                    if isinstance(mount_config, dict) and "bind" in mount_config:
                        # Bind mount format: {"/host": {"bind": "/container", "mode": "ro"}}
                        container_path = mount_config["bind"]
                        mode = mount_config.get("mode", "rw")
                        binds.append(f"{host_path}:{container_path}:{mode}")
                    else:
                        # Anonymous volume format: {"/container": {}}
                        volume_config[host_path] = mount_config if isinstance(mount_config, dict) else {}

                if volume_config:
                    config["Volumes"] = volume_config
                if binds:
                    if "HostConfig" not in config:
                        config["HostConfig"] = {}
                    config["HostConfig"]["Binds"] = binds
            if ports:
                config["ExposedPorts"] = {port: {} for port in (ports.keys() if isinstance(ports, dict) else ports)}
                if isinstance(ports, dict):
                    config["HostConfig"] = {"PortBindings": ports}

            # Init flag support
            init: bool | None = kwargs.pop("init", None)
            if init is not None:
                if "HostConfig" not in config:
                    config["HostConfig"] = {}
                config["HostConfig"]["Init"] = init

            # Add any additional config
            config.update(kwargs)

            # Create container
            params = {"name": name} if name else {}
            response = await self._client.post("/containers/create", json=config, params=params)
            data = response.json()

            container_id = data["Id"]

            self.logger.info(
                "container_created",
                container_id=container_id,
                name=name,
                image=image,
            )

            # Return container info
            return await self.inspect(container_id)

    async def start(self, container_id: str) -> None:
        """Start a container.

        Args:
            container_id: Container ID or name

        Example:
            await manager.start("my-container")
        """
        with log_context(operation="container_start", container_id=container_id):
            self.logger.info("container_start", container_id=container_id)

            await self._client.post(f"/containers/{container_id}/start")

            self.logger.info("container_started", container_id=container_id)

    async def stop(self, container_id: str, timeout: int = 10, signal: str | None = None) -> None:
        """Stop a container.

        Args:
            container_id: Container ID or name
            timeout: Seconds to wait before killing
            signal: Signal to send to container (e.g., SIGTERM, SIGKILL)

        Example:
            await manager.stop("my-container", timeout=30)
            await manager.stop("my-container", signal="SIGKILL")
        """
        with log_context(operation="container_stop", container_id=container_id):
            self.logger.info("container_stop", container_id=container_id, timeout=timeout, signal=signal)

            params = {"t": timeout}
            if signal:
                params["signal"] = signal
            await self._client.post(f"/containers/{container_id}/stop", params=params)

            self.logger.info("container_stopped", container_id=container_id)

    async def remove(
        self,
        container_id: str,
        *,
        force: bool = False,
        volumes: bool = False,
    ) -> None:
        """Remove a container.

        Args:
            container_id: Container ID or name
            force: Force removal (kill if running)
            volumes: Remove associated volumes

        Example:
            await manager.remove("my-container", force=True)
        """
        with log_context(operation="container_remove", container_id=container_id):
            self.logger.info(
                "container_remove",
                container_id=container_id,
                force=force,
                volumes=volumes,
            )

            params = {"force": force, "v": volumes}
            await self._client.delete(f"/containers/{container_id}", params=params)

            self.logger.info("container_removed", container_id=container_id)

    async def list(
        self,
        *,
        all: bool = False,
        limit: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[Container]:
        """List containers.

        Args:
            all: Show all containers (default: only running)
            limit: Limit number of containers
            filters: Filter containers (e.g., {"status": ["running"]})

        Returns:
            List of containers

        Example:
            # List running containers
            containers = await manager.list()

            # List all containers
            containers = await manager.list(all=True)

            # Filter by status
            containers = await manager.list(filters={"status": ["exited"]})
        """
        with log_context(operation="container_list"):
            self.logger.debug("container_list", all=all, limit=limit)

            params: dict[str, Any] = {"all": all}
            if limit:
                params["limit"] = limit
            if filters:
                params["filters"] = json.dumps(filters)

            response = await self._client.get("/containers/json", params=params)
            data = response.json()

            containers = [Container.from_api(item) for item in data]

            self.logger.info("container_list_complete", count=len(containers))

            return containers

    async def inspect(self, container_id: str) -> Container:
        """Get container details.

        Args:
            container_id: Container ID or name

        Returns:
            Container with full details

        Example:
            container = await manager.inspect("my-container")
            print(f"Status: {container.status}")
        """
        with log_context(operation="container_inspect", container_id=container_id):
            self.logger.debug("container_inspect", container_id=container_id)

            response = await self._client.get(f"/containers/{container_id}/json")
            data = response.json()

            # Convert to Container (simplified view)
            container = Container(
                id=data["Id"],
                name=data["Name"].lstrip("/"),
                image=data["Config"]["Image"],
                image_id=data["Image"],
                status=data["State"]["Status"],
                state=data["State"]["Status"],
                command=data.get("Config", {}).get("Cmd") or data.get("Command", ""),
                created=data["Created"],
                ports=data.get("NetworkSettings", {}).get("Ports", {}),
                labels=data["Config"].get("Labels") or {},
                names=[data["Name"].lstrip("/")],
            )

            self.logger.debug("container_inspected", container_id=container_id)

            return container

    async def inspect_detailed(self, container_id: str) -> ContainerInspect:
        """Get detailed container information.

        Args:
            container_id: Container ID or name

        Returns:
            Detailed container information

        Example:
            details = await manager.inspect_detailed("my-container")
            print(f"Exit code: {details.state.exit_code}")
        """
        with log_context(operation="container_inspect_detailed", container_id=container_id):
            response = await self._client.get(f"/containers/{container_id}/json")
            data = response.json()

            return ContainerInspect.from_api(data)

    async def logs(
        self,
        container_id: str,
        *,
        stdout: bool = True,
        stderr: bool = True,
        follow: bool = False,
        tail: int | str | None = None,
        timestamps: bool = False,
        since: str | None = None,
        until: str | None = None,
        details: bool = False,
        format_output: bool = True,
    ) -> AsyncIterator[str]:
        """Stream container logs.

        Args:
            container_id: Container ID or name
            stdout: Include stdout
            stderr: Include stderr
            follow: Follow log output (stream)
            tail: Number of lines from end ("all" for all lines)
            timestamps: Include timestamps
            since: Show logs since timestamp (RFC3339, Unix timestamp, or relative like "2h")
            until: Show logs before timestamp (RFC3339, Unix timestamp, or relative like "2h")
            details: Include log details
            format_output: Format logs output in TUI-like style (default: True)

        Yields:
            Log lines

        Example:
            # Get last 100 lines
            async for line in manager.logs("my-container", tail=100):
                print(line)

            # Follow logs in real-time
            async for line in manager.logs("my-container", follow=True):
                print(line)

            # Get logs since 2 hours ago
            async for line in manager.logs("my-container", since="2h"):
                print(line)
        """
        with log_context(operation="container_logs", container_id=container_id):
            self.logger.debug(
                "container_logs",
                container_id=container_id,
                follow=follow,
            )

            params: dict[str, Any] = {
                "stdout": stdout,
                "stderr": stderr,
                "follow": follow,
                "timestamps": timestamps,
                "details": details,
            }
            if tail:
                params["tail"] = tail
            if since:
                params["since"] = since
            if until:
                params["until"] = until

            async def raw_logs() -> AsyncIterator[str]:
                async with self._client.stream("GET", f"/containers/{container_id}/logs", params=params) as response:
                    async for chunk in response.aiter_bytes():
                        if chunk:
                            # Docker log format: 8-byte header + message
                            # Skip header if present
                            if len(chunk) > 8:
                                message = chunk[8:].decode("utf-8", errors="replace")
                            else:
                                message = chunk.decode("utf-8", errors="replace")
                            yield message.rstrip("\n")

            if format_output:
                async for formatted_line in format_logs_stream(
                    raw_logs(), container_id, timestamps=timestamps, write_to_stdout=True
                ):
                    yield formatted_line
            else:
                async for line in raw_logs():
                    yield line

    async def exec(
        self,
        container_id: str,
        cmd: list[str] | str,
        *,
        workdir: str | None = None,
        environment: dict[str, str] | None = None,
        user: str | None = None,
        privileged: bool = False,
        format_output: bool = True,
    ) -> tuple[int, str]:
        """Execute command in container.

        Args:
            container_id: Container ID or name
            cmd: Command to execute
            workdir: Working directory
            environment: Environment variables
            user: User to run as
            privileged: Run in privileged mode
            format_output: Format exec output in TUI-like style (default: True)

        Returns:
            Tuple of (exit_code, output)

        Example:
            exit_code, output = await manager.exec(
                "my-container",
                ["ls", "-la", "/app"],
            )
            print(f"Exit code: {exit_code}")
            print(output)
        """
        with log_context(operation="container_exec", container_id=container_id):
            self.logger.info("container_exec", container_id=container_id, cmd=cmd)

            # Create exec instance
            exec_config: dict[str, Any] = {
                "AttachStdout": True,
                "AttachStderr": True,
                "Cmd": cmd if isinstance(cmd, list) else [cmd],
            }

            if workdir:
                exec_config["WorkingDir"] = workdir
            if environment:
                exec_config["Env"] = [f"{k}={v}" for k, v in environment.items()]
            if user:
                exec_config["User"] = user
            if privileged:
                exec_config["Privileged"] = privileged

            response = await self._client.post(
                f"/containers/{container_id}/exec",
                json=exec_config,
            )
            exec_id = response.json()["Id"]

            # Start exec with streaming to properly handle Docker stream format
            # Docker stream format: 8-byte header [stream_type(1), 0, 0, 0, size(4)] + payload
            start_config = {
                "Detach": False,
                "Tty": False,
            }

            output_chunks: list[str] = []
            async with self._client.stream(
                "POST",
                f"/exec/{exec_id}/start",
                json=start_config,
            ) as response:
                async for chunk in response.aiter_bytes():
                    if not chunk:
                        continue
                    # Docker multiplexes stdout/stderr with 8-byte headers
                    # Header format: [stream_type(1), 0, 0, 0, size(4)]
                    # stream_type: 0=stdin, 1=stdout, 2=stderr
                    decoded = self._decode_docker_stream(chunk)
                    if decoded:
                        output_chunks.append(decoded)

            output = "".join(output_chunks)

            # Get exit code
            response = await self._client.get(f"/exec/{exec_id}/json")
            exit_code = response.json().get("ExitCode", 0)

            self.logger.info(
                "container_exec_complete",
                container_id=container_id,
                exit_code=exit_code,
            )

            # Format output if requested
            if format_output:
                format_exec_output(cmd, output, exit_code, container_id, write_to_stdout=True)
                return exit_code, output

            return exit_code, output

    def _decode_docker_stream(self, chunk: bytes) -> str:
        """Decode Docker multiplexed stream chunk.

        Docker multiplexes stdout/stderr with 8-byte headers:
        - Byte 0: stream type (0=stdin, 1=stdout, 2=stderr)
        - Bytes 1-3: reserved (zeros)
        - Bytes 4-7: payload size (big-endian uint32)

        Args:
            chunk: Raw bytes from Docker stream

        Returns:
            Decoded string content
        """
        result = []
        pos = 0

        while pos < len(chunk):
            # Need at least 8 bytes for header
            if pos + 8 > len(chunk):
                # Remaining bytes without header - decode as-is
                result.append(chunk[pos:].decode("utf-8", errors="replace"))
                break

            # Parse header
            # stream_type = chunk[pos]  # 0=stdin, 1=stdout, 2=stderr
            size = int.from_bytes(chunk[pos + 4 : pos + 8], byteorder="big")

            # Skip header
            pos += 8

            # Extract payload
            if size > 0 and pos + size <= len(chunk):
                payload = chunk[pos : pos + size]
                result.append(payload.decode("utf-8", errors="replace"))
                pos += size
            elif size == 0:
                # Empty payload, continue
                continue
            else:
                # Incomplete chunk - decode remaining as-is
                result.append(chunk[pos:].decode("utf-8", errors="replace"))
                break

        return "".join(result)

    async def stats(
        self,
        container_id: str,
        *,
        stream: bool = False,
    ) -> ContainerStats | AsyncIterator[ContainerStats]:
        """Get container resource usage statistics.

        Args:
            container_id: Container ID or name
            stream: Stream stats continuously

        Returns:
            Single stats snapshot or async iterator of stats

        Example:
            # Get single snapshot
            stats = await manager.stats("my-container")
            print(f"CPU: {stats.cpu_percent}%")

            # Stream stats
            async for stats in await manager.stats("my-container", stream=True):
                print(f"Memory: {stats.memory_percent}%")
        """
        with log_context(operation="container_stats", container_id=container_id):
            self.logger.debug("container_stats", container_id=container_id, stream=stream)

            params = {"stream": stream}

            if stream:
                return self._stream_stats(container_id, params)
            response = await self._client.get(
                f"/containers/{container_id}/stats",
                params=params,
            )
            data = response.json()
            return ContainerStats.from_api(data)

    async def _stream_stats(
        self,
        container_id: str,
        params: dict[str, Any],
    ) -> AsyncIterator[ContainerStats]:
        """Stream container stats.

        Args:
            container_id: Container ID
            params: Request parameters

        Yields:
            Container stats
        """
        async with self._client.stream("GET", f"/containers/{container_id}/stats", params=params) as response:
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    yield ContainerStats.from_api(data)

    async def restart(self, container_id: str, timeout: int = 10) -> None:
        """Restart a container.

        Args:
            container_id: Container ID or name
            timeout: Seconds to wait before killing

        Example:
            await manager.restart("my-container")
        """
        with log_context(operation="container_restart", container_id=container_id):
            self.logger.info("container_restart", container_id=container_id)

            params = {"t": timeout}
            await self._client.post(f"/containers/{container_id}/restart", params=params)

            self.logger.info("container_restarted", container_id=container_id)

    async def pause(self, container_id: str) -> None:
        """Pause a container.

        Args:
            container_id: Container ID or name

        Example:
            await manager.pause("my-container")
        """
        with log_context(operation="container_pause", container_id=container_id):
            self.logger.info("container_pause", container_id=container_id)

            await self._client.post(f"/containers/{container_id}/pause")

            self.logger.info("container_paused", container_id=container_id)

    async def unpause(self, container_id: str) -> None:
        """Unpause a container.

        Args:
            container_id: Container ID or name

        Example:
            await manager.unpause("my-container")
        """
        with log_context(operation="container_unpause", container_id=container_id):
            self.logger.info("container_unpause", container_id=container_id)

            await self._client.post(f"/containers/{container_id}/unpause")

            self.logger.info("container_unpaused", container_id=container_id)

    async def wait(self, container_id: str, condition: str | None = None) -> int:
        """Wait for container to stop.

        Args:
            container_id: Container ID or name
            condition: Wait condition: "not-running", "next-exit", or "removed" (default: "not-running")

        Returns:
            Exit code

        Example:
            exit_code = await manager.wait("my-container")
            print(f"Container exited with code: {exit_code}")

            # Wait for next exit
            exit_code = await manager.wait("my-container", condition="next-exit")
        """
        with log_context(operation="container_wait", container_id=container_id):
            self.logger.info("container_wait", container_id=container_id, condition=condition)

            if condition:
                params = {"condition": condition}
                response = await self._client.post(f"/containers/{container_id}/wait", params=params)
            else:
                response = await self._client.post(f"/containers/{container_id}/wait")
            data = response.json()
            exit_code = data.get("StatusCode", 0)

            self.logger.info("container_wait_complete", container_id=container_id, exit_code=exit_code)

            return exit_code

    async def rename(self, container_id: str, new_name: str) -> None:
        """Rename a container.

        Args:
            container_id: Container ID or current name
            new_name: New container name

        Example:
            await manager.rename("old-name", "new-name")
        """
        with log_context(operation="container_rename", container_id=container_id):
            self.logger.info("container_rename", container_id=container_id, new_name=new_name)

            params = {"name": new_name}
            await self._client.post(f"/containers/{container_id}/rename", params=params)

            self.logger.info("container_renamed", container_id=container_id, new_name=new_name)

    async def prune(
        self,
        *,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Remove all stopped containers.

        Args:
            filters: Optional filters (e.g., {"until": "24h"})

        Returns:
            Dictionary with "ContainersDeleted" and "SpaceReclaimed" keys

        Example:
            result = await manager.prune()
            print(f"Deleted: {len(result['ContainersDeleted'])} containers")
        """
        with log_context(operation="container_prune"):
            self.logger.info("container_prune", filters=filters)

            params: dict[str, Any] = {}
            if filters:
                params["filters"] = filters

            response = await self._client.post("/containers/prune", params=params)
            data = response.json()

            deleted_count = len(data.get("ContainersDeleted", []))
            space_reclaimed = data.get("SpaceReclaimed", 0)

            self.logger.info(
                "containers_pruned",
                deleted_count=deleted_count,
                space_reclaimed=space_reclaimed,
            )

            return data

    async def top(self, container_id: str, ps_args: str = "-ef") -> dict[str, Any]:
        """List running processes in a container.

        Args:
            container_id: Container ID or name
            ps_args: Arguments for ps command (default: "-ef")

        Returns:
            Dictionary with "Titles" (column names) and "Processes" (list of process lists)

        Example:
            result = await manager.top("my-container")
            print(f"Processes: {result['Processes']}")
        """
        with log_context(operation="container_top", container_id=container_id):
            self.logger.debug("container_top", container_id=container_id, ps_args=ps_args)

            params = {"ps_args": ps_args}
            response = await self._client.get(f"/containers/{container_id}/top", params=params)
            data = response.json()

            process_count = len(data.get("Processes", []))
            self.logger.debug("container_top_complete", container_id=container_id, process_count=process_count)

            return data

    async def commit(
        self,
        container_id: str,
        *,
        repo: str | None = None,
        tag: str | None = None,
        author: str | None = None,
        message: str | None = None,
        changes: list[str] | None = None,
        pause: bool = True,
    ) -> str:
        """Create an image from a container.

        Args:
            container_id: Container ID or name
            repo: Repository name for the image
            tag: Tag name for the image
            author: Commit author
            message: Commit message
            changes: List of Dockerfile instructions (e.g., ["CMD /app/run.sh", "ENTRYPOINT bash"])
            pause: Pause container during commit (default: True)

        Returns:
            Image ID of the created image

        Example:
            image_id = await manager.commit(
                "my-container",
                repo="myrepo/myimage",
                tag="v1.0",
                author="John Doe",
                message="Initial commit",
                changes=["CMD /app/start.sh", "ENV APP_ENV=production"],
            )
        """
        with log_context(operation="container_commit", container_id=container_id):
            self.logger.info(
                "container_commit_start",
                container_id=container_id,
                repo=repo,
                tag=tag,
                pause=pause,
            )

            # Build query params - container ID is required
            params: dict[str, Any] = {"container": container_id, "pause": pause}
            if repo:
                params["repo"] = repo
            if tag:
                params["tag"] = tag
            if author:
                params["author"] = author
            if message:
                params["comment"] = message
            # Docker API expects 'changes' as repeated query params
            # httpx handles list values correctly: ?changes=X&changes=Y
            if changes:
                params["changes"] = changes

            # Docker commit API is POST /commit with container as query param
            response = await self._client.post("/commit", params=params)
            data = response.json()

            image_id = data.get("Id", "")
            self.logger.info("container_commit_complete", container_id=container_id, image_id=image_id)

            return image_id

    async def diff(self, container_id: str) -> list[dict[str, str]]:
        """Show filesystem changes in a container.

        Args:
            container_id: Container ID or name

        Returns:
            List of change dictionaries with "Path" and "Kind" fields.
            Kind values: 0 (modified), 1 (added), 2 (deleted)

        Example:
            changes = await manager.diff("my-container")
            for change in changes:
                print(f"{change['Kind']}: {change['Path']}")
        """
        with log_context(operation="container_diff", container_id=container_id):
            self.logger.debug("container_diff", container_id=container_id)

            response = await self._client.get(f"/containers/{container_id}/changes")
            data = response.json()

            change_count = len(data)
            self.logger.info("container_diff_complete", container_id=container_id, change_count=change_count)

            return data

    async def update(
        self,
        container_id: str,
        *,
        memory: int | None = None,
        memory_swap: int | None = None,
        cpu_quota: int | None = None,
        cpu_period: int | None = None,
        cpuset_cpus: str | None = None,
        cpuset_mems: str | None = None,
        cpu_shares: int | None = None,
        blkio_weight: int | None = None,
    ) -> dict[str, Any]:
        """Update container resource limits.

        Args:
            container_id: Container ID or name
            memory: Memory limit in bytes
            memory_swap: Memory + swap limit in bytes
            cpu_quota: CPU quota in microseconds
            cpu_period: CPU period in microseconds
            cpuset_cpus: CPUs to use (e.g., "0-3" or "0,1")
            cpuset_mems: Memory nodes to use
            cpu_shares: CPU shares (relative weight)
            blkio_weight: Block IO weight (10-1000)

        Returns:
            Dictionary with "Warnings" array

        Example:
            result = await manager.update(
                "my-container",
                memory=1024 * 1024 * 512,  # 512 MB
                cpu_shares=512,
            )
            if result.get("Warnings"):
                print(f"Warnings: {result['Warnings']}")
        """
        with log_context(operation="container_update", container_id=container_id):
            self.logger.info("container_update_start", container_id=container_id)

            resources: dict[str, Any] = {}

            if memory is not None:
                resources["Memory"] = memory
            if memory_swap is not None:
                resources["MemorySwap"] = memory_swap
            if cpu_quota is not None:
                resources["CpuQuota"] = cpu_quota
            if cpu_period is not None:
                resources["CpuPeriod"] = cpu_period
            if cpuset_cpus is not None:
                resources["CpusetCpus"] = cpuset_cpus
            if cpuset_mems is not None:
                resources["CpusetMems"] = cpuset_mems
            if cpu_shares is not None:
                resources["CpuShares"] = cpu_shares
            if blkio_weight is not None:
                resources["BlkioWeight"] = blkio_weight

            if not resources:
                self.logger.warning("container_update_no_resources", container_id=container_id)
                return {"Warnings": []}

            body = {"Resources": resources}
            response = await self._client.post(f"/containers/{container_id}/update", json=body)
            data = response.json()

            warnings = data.get("Warnings", [])
            self.logger.info(
                "container_update_complete",
                container_id=container_id,
                warning_count=len(warnings),
            )

            return data

    async def cp(
        self,
        container_id: str,
        src_path: str,
        dst_path: str,
        *,
        direction: str = "from",
    ) -> None:
        """Copy files/folders between container and host.

        Args:
            container_id: Container ID or name
            src_path: Source path
            dst_path: Destination path
            direction: "from" (container to host) or "to" (host to container)

        Example:
            # Copy from container to host
            await manager.cp("my-container", "/app/data", "/tmp/data", direction="from")

            # Copy from host to container
            await manager.cp("my-container", "/tmp/file.txt", "/app/file.txt", direction="to")
        """
        with log_context(operation="container_cp", container_id=container_id, direction=direction):
            self.logger.info(
                "container_cp_start",
                container_id=container_id,
                src_path=src_path,
                dst_path=dst_path,
                direction=direction,
            )

            if direction == "from":
                # Copy from container to host
                params = {"path": src_path}
                async with self._client.stream("GET", f"/containers/{container_id}/archive", params=params) as response:
                    # Read tar archive from response
                    tar_data = b""
                    async for chunk in response.aiter_bytes():
                        tar_data += chunk

                # Extract tar to destination
                dst = Path(dst_path)
                if dst.is_dir() or not dst.exists():
                    # Extract to directory
                    extract_path = dst_path if dst.is_dir() else dst.parent
                    Path(extract_path).mkdir(parents=True, exist_ok=True)
                    with tarfile.open(fileobj=io.BytesIO(tar_data)) as tar:
                        tar.extractall(path=extract_path, filter="data")
                else:
                    # Extract single file
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    with tarfile.open(fileobj=io.BytesIO(tar_data)) as tar:
                        members = tar.getmembers()
                        if members:
                            member = members[0]
                            with tar.extractfile(member) as f:
                                if f:
                                    dst.write_bytes(f.read())

            else:
                # Copy from host to container
                src = Path(src_path)
                if not src.exists():
                    raise NotFound("file", src_path)

                # Create tar archive in memory with normalized metadata
                tar_buffer = io.BytesIO()
                with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
                    if src.is_file():
                        tarinfo = tar.gettarinfo(src_path, arcname=src.name)
                        tarinfo.mtime = 0
                        tarinfo.uid = 0
                        tarinfo.gid = 0
                        tarinfo.uname = ""
                        tarinfo.gname = ""
                        with src.open("rb") as f:
                            tar.addfile(tarinfo, f)
                    else:
                        # For directories, collect files for deterministic ordering
                        files_to_add: list[tuple[Path, str]] = []
                        for item in src.rglob("*"):
                            if item.is_dir():
                                continue
                            rel_path = item.relative_to(src)
                            rel_str = str(rel_path).replace("\\", "/")
                            files_to_add.append((item, f"{src.name}/{rel_str}"))

                        # Sort for deterministic ordering
                        files_to_add.sort(key=lambda x: x[1])

                        # Add files with normalized metadata
                        for item, arcname in files_to_add:
                            tarinfo = tar.gettarinfo(item, arcname=arcname)
                            tarinfo.mtime = 0
                            tarinfo.uid = 0
                            tarinfo.gid = 0
                            tarinfo.uname = ""
                            tarinfo.gname = ""
                            with item.open("rb") as f:
                                tar.addfile(tarinfo, f)

                tar_data = tar_buffer.getvalue()

                # PUT to container
                params = {"path": dst_path}
                await self._client.put(
                    f"/containers/{container_id}/archive",
                    params=params,
                    content=tar_data,
                    headers={"Content-Type": "application/x-tar"},
                )

            self.logger.info("container_cp_complete", container_id=container_id, direction=direction)
