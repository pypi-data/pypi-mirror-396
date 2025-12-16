# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Data models for Docker SDK.

Author: A M (am@bbdevs.com)
Created At: 08 Nov 2025
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


__all__ = [
    "ComposeFile",
    "ComposeNetwork",
    "ComposeService",
    "ComposeVolume",
    "Container",
    "ContainerInspect",
    "ContainerLog",
    "ContainerStats",
    "Image",
    "ImageDetail",
    "ImageInspect",
]


@dataclass(frozen=True)
class Container:
    """Lightweight container representation.

    Used for listing containers and basic operations.
    """

    id: str
    name: str
    image: str
    image_id: str
    status: str
    command: str
    state: str
    created: str
    ports: dict[str, list[dict[str, Any]]]
    labels: dict[str, str]
    names: list[str]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Container:
        """Create Container from Docker API response.

        Args:
            data: Container data from API

        Returns:
            Container instance
        """
        return cls(
            id=data["Id"],
            name=data["Names"][0].lstrip("/") if data.get("Names") else "",
            image=data.get("Image", ""),
            image_id=data.get("ImageID", ""),
            command=data.get("Command", ""),
            status=data.get("Status", ""),
            state=data.get("State", ""),
            created=data.get("Created", ""),
            ports=data.get("Ports", {}),
            labels=data.get("Labels") or {},
            names=[n.lstrip("/") for n in data.get("Names", [])],
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "image_id": self.image_id,
            "command": self.command,
            "status": self.status,
            "state": self.state,
            "created": self.created,
            "ports": self.ports,
            "labels": self.labels,
            "names": self.names,
        }


@dataclass(frozen=True)
class ContainerInspect:
    """Detailed container information.

    Used for inspect operations with full container details.
    """

    id: str
    name: str
    image: str
    created: str
    state: ContainerState
    config: ContainerConfig
    host_config: dict[str, Any]
    network_settings: dict[str, Any]
    mounts: list[dict[str, Any]]
    size_rw: int = 0
    size_root_fs: int = 0

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ContainerInspect:
        """Create ContainerInspect from Docker API response.

        Args:
            data: Container inspect data from API

        Returns:
            ContainerInspect instance
        """
        return cls(
            id=data["Id"],
            name=data["Name"].lstrip("/"),
            image=data["Image"],
            created=data["Created"],
            state=ContainerState.from_api(data["State"]),
            config=ContainerConfig.from_api(data["Config"]),
            host_config=data.get("HostConfig", {}),
            network_settings=data.get("NetworkSettings", {}),
            mounts=data.get("Mounts", []),
            size_rw=data.get("SizeRw", 0),
            size_root_fs=data.get("SizeRootFs", 0),
        )


@dataclass(frozen=True)
class ContainerState:
    """Container state information."""

    status: str
    running: bool
    paused: bool
    restarting: bool
    oom_killed: bool
    dead: bool
    pid: int
    exit_code: int
    error: str
    started_at: str
    finished_at: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ContainerState:
        """Create ContainerState from API response."""
        return cls(
            status=data.get("Status", ""),
            running=data.get("Running", False),
            paused=data.get("Paused", False),
            restarting=data.get("Restarting", False),
            oom_killed=data.get("OOMKilled", False),
            dead=data.get("Dead", False),
            pid=data.get("Pid", 0),
            exit_code=data.get("ExitCode", 0),
            error=data.get("Error", ""),
            started_at=data.get("StartedAt", ""),
            finished_at=data.get("FinishedAt", ""),
        )


@dataclass(frozen=True)
class ContainerConfig:
    """Container configuration."""

    hostname: str
    domainname: str
    user: str
    attach_stdin: bool
    attach_stdout: bool
    attach_stderr: bool
    tty: bool
    open_stdin: bool
    stdin_once: bool
    env: list[str]
    cmd: list[str] | None
    image: str
    volumes: dict[str, Any]
    working_dir: str
    entrypoint: list[str] | None
    labels: dict[str, str]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ContainerConfig:
        """Create ContainerConfig from API response."""
        return cls(
            hostname=data.get("Hostname", ""),
            domainname=data.get("Domainname", ""),
            user=data.get("User", ""),
            attach_stdin=data.get("AttachStdin", False),
            attach_stdout=data.get("AttachStdout", False),
            attach_stderr=data.get("AttachStderr", False),
            tty=data.get("Tty", False),
            open_stdin=data.get("OpenStdin", False),
            stdin_once=data.get("StdinOnce", False),
            env=data.get("Env") or [],
            cmd=data.get("Cmd"),
            image=data.get("Image", ""),
            volumes=data.get("Volumes") or {},
            working_dir=data.get("WorkingDir", ""),
            entrypoint=data.get("Entrypoint"),
            labels=data.get("Labels") or {},
        )


@dataclass(frozen=True)
class ContainerStats:
    """Container resource usage statistics."""

    cpu_percent: float
    memory_usage: int
    memory_limit: int
    memory_percent: float
    network_rx_bytes: int
    network_tx_bytes: int
    block_read_bytes: int
    block_write_bytes: int
    pids: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ContainerStats:
        """Create ContainerStats from API response.

        Args:
            data: Stats data from API

        Returns:
            ContainerStats instance
        """
        # Calculate CPU percentage
        cpu_delta = data["cpu_stats"]["cpu_usage"]["total_usage"] - data["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = data["cpu_stats"]["system_cpu_usage"] - data["precpu_stats"]["system_cpu_usage"]
        online_cpus = data["cpu_stats"].get("online_cpus", 1)

        cpu_percent = 0.0
        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * online_cpus * 100.0

        # Memory stats
        memory_stats = data.get("memory_stats", {})
        memory_usage = memory_stats.get("usage", 0)
        memory_limit = memory_stats.get("limit", 0)
        memory_percent = (memory_usage / memory_limit * 100.0) if memory_limit > 0 else 0.0

        # Network stats
        networks = data.get("networks", {})
        network_rx = sum(net.get("rx_bytes", 0) for net in networks.values())
        network_tx = sum(net.get("tx_bytes", 0) for net in networks.values())

        # Block I/O stats
        blkio_stats = data.get("blkio_stats", {})
        io_service_bytes = blkio_stats.get("io_service_bytes_recursive", [])
        block_read = sum(entry.get("value", 0) for entry in io_service_bytes if entry.get("op") == "Read")
        block_write = sum(entry.get("value", 0) for entry in io_service_bytes if entry.get("op") == "Write")

        # PIDs
        pids = data.get("pids_stats", {}).get("current", 0)

        return cls(
            cpu_percent=round(cpu_percent, 2),
            memory_usage=memory_usage,
            memory_limit=memory_limit,
            memory_percent=round(memory_percent, 2),
            network_rx_bytes=network_rx,
            network_tx_bytes=network_tx,
            block_read_bytes=block_read,
            block_write_bytes=block_write,
            pids=pids,
        )


@dataclass(frozen=True)
class ContainerLog:
    """Container log entry."""

    stream: str  # "stdout" or "stderr"
    timestamp: str
    message: str

    @classmethod
    def from_line(cls, line: str) -> ContainerLog:
        """Parse log line from Docker API.

        Docker log format: [stream_type][timestamp] message

        Args:
            line: Raw log line

        Returns:
            ContainerLog instance
        """
        # Simple parsing - Docker returns lines with stream prefix
        # Format: \x01\x00\x00\x00\x00\x00\x00\x1fmessage
        # First byte: 1=stdout, 2=stderr
        if isinstance(line, bytes) and len(line) > 8:
            stream_type = "stdout" if line[0] == 1 else "stderr"
            message = line[8:].decode("utf-8")
        elif isinstance(line, bytes):
            stream_type = "stdout"
            message = line.decode("utf-8")
        else:
            # String input - default to stdout
            stream_type = "stdout"
            message = line

        return cls(
            stream=stream_type,
            timestamp="",  # Will be populated if timestamps are enabled
            message=message.rstrip("\n"),
        )


@dataclass(frozen=True)
class Image:
    """Lightweight image representation.

    Used for listing images and basic operations.
    """

    id: str
    repo_tags: list[str]
    repo_digests: list[str]
    size: int
    virtual_size: int
    created: int
    shared_size: int | None
    labels: dict[str, str]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Image:
        """Create Image from Docker API response.

        Args:
            data: Image data from API

        Returns:
            Image instance
        """
        return cls(
            id=data["Id"],
            repo_tags=data.get("RepoTags") or [],
            repo_digests=data.get("RepoDigests") or [],
            size=data.get("Size", 0),
            virtual_size=data.get("VirtualSize", 0),
            created=data.get("Created", 0),
            shared_size=data.get("SharedSize"),
            labels=data.get("Labels") or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "repo_tags": self.repo_tags,
            "repo_digests": self.repo_digests,
            "size": self.size,
            "virtual_size": self.virtual_size,
            "created": self.created,
            "shared_size": self.shared_size,
            "labels": self.labels,
        }


@dataclass(frozen=True)
class ImageDetail:
    """Image layer/history entry."""

    created: str
    created_by: str
    empty_layer: bool
    comment: str


@dataclass(frozen=True)
class ImageInspect:
    """Detailed image information.

    Used for inspect operations with full image details.
    """

    id: str
    repo_tags: list[str]
    repo_digests: list[str]
    parent: str
    created: str
    config: dict[str, Any]
    size: int
    virtual_size: int
    author: str
    architecture: str
    os: str
    os_version: str | None
    docker_version: str
    history: list[ImageDetail]
    graph_driver: dict[str, Any]
    root_fs: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ImageInspect:
        """Create ImageInspect from Docker API response.

        Args:
            data: Image inspect data from API

        Returns:
            ImageInspect instance
        """
        history_list = []
        for entry in data.get("History", []):
            history_list.append(
                ImageDetail(
                    created=entry.get("Created", ""),
                    created_by=entry.get("CreatedBy", ""),
                    empty_layer=entry.get("EmptyLayer", False),
                    comment=entry.get("Comment", ""),
                )
            )

        return cls(
            id=data["Id"],
            repo_tags=data.get("RepoTags") or [],
            repo_digests=data.get("RepoDigests") or [],
            parent=data.get("Parent", ""),
            created=data.get("Created", ""),
            config=data.get("Config", {}),
            size=data.get("Size", 0),
            virtual_size=data.get("VirtualSize", 0),
            author=data.get("Author", ""),
            architecture=data.get("Architecture", ""),
            os=data.get("Os", ""),
            os_version=data.get("OsVersion"),
            docker_version=data.get("DockerVersion", ""),
            history=history_list,
            graph_driver=data.get("GraphDriver", {}),
            root_fs=data.get("RootFS", {}),
        )

    def get_primary_tag(self) -> str | None:
        """Get the primary repo tag (latest or first).

        Returns:
            Primary tag or None
        """
        if not self.repo_tags:
            return None

        # Look for "latest" tag
        for tag in self.repo_tags:
            if ":latest" in tag:
                return tag

        # Return first tag
        return self.repo_tags[0] if self.repo_tags else None


@dataclass(frozen=True)
class ComposeService:
    """Compose service definition."""

    name: str
    image: str | None
    build: dict[str, Any] | None
    command: list[str] | str | None
    entrypoint: list[str] | str | None
    environment: dict[str, str] | list[str] | None
    ports: list[str] | dict[str, Any] | None
    volumes: list[str] | dict[str, Any] | None
    networks: list[str] | dict[str, Any] | None
    depends_on: list[str] | dict[str, dict[str, str]] | None
    labels: dict[str, str] | None
    restart: str | None
    healthcheck: dict[str, Any] | None
    deploy: dict[str, Any] | None
    working_dir: str | None
    user: str | None
    hostname: str | None
    extra_hosts: list[str] | None
    config: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:  # noqa: PLR0912
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        result: dict[str, Any] = {}
        if self.image:
            result["image"] = self.image
        if self.build:
            result["build"] = self.build
        if self.command:
            result["command"] = self.command
        if self.entrypoint:
            result["entrypoint"] = self.entrypoint
        if self.environment:
            result["environment"] = self.environment
        if self.ports:
            result["ports"] = self.ports
        if self.volumes:
            result["volumes"] = self.volumes
        if self.networks:
            result["networks"] = self.networks
        if self.depends_on:
            result["depends_on"] = self.depends_on
        if self.labels:
            result["labels"] = self.labels
        if self.restart:
            result["restart"] = self.restart
        if self.healthcheck:
            result["healthcheck"] = self.healthcheck
        if self.deploy:
            result["deploy"] = self.deploy
        if self.working_dir:
            result["working_dir"] = self.working_dir
        if self.user:
            result["user"] = self.user
        if self.hostname:
            result["hostname"] = self.hostname
        if self.extra_hosts:
            result["extra_hosts"] = self.extra_hosts
        if self.config:
            result.update(self.config)
        return result


@dataclass(frozen=True)
class ComposeNetwork:
    """Compose network definition."""

    name: str
    driver: str | None
    driver_opts: dict[str, Any] | None
    external: bool
    external_name: str | None
    labels: dict[str, str] | None
    ipam: dict[str, Any] | None
    config: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        result: dict[str, Any] = {}
        if self.driver:
            result["driver"] = self.driver
        if self.driver_opts:
            result["driver_opts"] = self.driver_opts
        if self.external:
            result["external"] = self.external
        if self.external_name:
            result["name"] = self.external_name
        if self.labels:
            result["labels"] = self.labels
        if self.ipam:
            result["ipam"] = self.ipam
        if self.config:
            result.update(self.config)
        return result


@dataclass(frozen=True)
class ComposeVolume:
    """Compose volume definition."""

    name: str
    driver: str | None
    driver_opts: dict[str, Any] | None
    external: bool
    external_name: str | None
    labels: dict[str, str] | None
    config: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        result: dict[str, Any] = {}
        if self.driver:
            result["driver"] = self.driver
        if self.driver_opts:
            result["driver_opts"] = self.driver_opts
        if self.external:
            result["external"] = self.external
        if self.external_name:
            result["name"] = self.external_name
        if self.labels:
            result["labels"] = self.labels
        if self.config:
            result.update(self.config)
        return result


@dataclass(frozen=True)
class ComposeFile:
    """Compose file representation.

    Contains merged compose configuration from multiple files.
    """

    version: str | None
    name: str | None
    services: dict[str, ComposeService]
    networks: dict[str, ComposeNetwork] | None
    volumes: dict[str, ComposeVolume] | None
    configs: dict[str, Any] | None
    secrets: dict[str, Any] | None
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (Compose file format).

        Returns:
            Dictionary representation in Compose file format
        """
        result: dict[str, Any] = {}
        if self.version:
            result["version"] = self.version
        if self.name:
            result["name"] = self.name
        result["services"] = {name: svc.to_dict() for name, svc in self.services.items()}
        if self.networks:
            result["networks"] = {name: net.to_dict() for name, net in self.networks.items()}
        if self.volumes:
            result["volumes"] = {name: vol.to_dict() for name, vol in self.volumes.items()}
        if self.configs:
            result["configs"] = self.configs
        if self.secrets:
            result["secrets"] = self.secrets
        return result

    def get_service_names(self) -> list[str]:
        """Get list of service names.

        Returns:
            List of service names
        """
        return list(self.services.keys())

    def filter_services(self, service_names: list[str]) -> ComposeFile:
        """Filter compose file to include only specified services.

        Args:
            service_names: List of service names to include

        Returns:
            New ComposeFile with filtered services
        """
        filtered_services = {name: service for name, service in self.services.items() if name in service_names}
        return ComposeFile(
            version=self.version,
            name=self.name,
            services=filtered_services,
            networks=self.networks,
            volumes=self.volumes,
            configs=self.configs,
            secrets=self.secrets,
            raw=self.raw,
        )
