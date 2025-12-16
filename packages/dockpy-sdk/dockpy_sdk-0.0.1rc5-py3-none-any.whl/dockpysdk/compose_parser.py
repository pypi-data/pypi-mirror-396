# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Compose file parser with multi-file support.

Author: A M (am@bbdevs.com)
Created At: 08 Nov 2025
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from ruyaml import YAML

from dockpycore.exceptions import DockerSDKError
from dockpycore.logging import get_logger

from .models import ComposeFile, ComposeNetwork, ComposeService, ComposeVolume


__all__ = [
    "ComposeParser",
    "discover_compose_files",
    "merge_compose_files",
    "parse_compose_file",
]

logger = get_logger(__name__)

# Create YAML instance
_yaml = YAML()
_yaml.preserve_quotes = True
_yaml.default_flow_style = False


class ComposeParserError(DockerSDKError):
    """Error parsing compose file."""


def _substitute_env_vars(value: str, env: dict[str, str] | None = None) -> str:
    """Substitute environment variables in string.

    Supports ${VAR} and ${VAR:-default} syntax.

    Args:
        value: String with environment variable references
        env: Environment variables dict (default: os.environ)

    Returns:
        String with substituted values
    """
    if env is None:
        env = dict(os.environ)

    # Pattern: ${VAR} or ${VAR:-default}
    pattern = r"\$\{([^:}]+)(?::-([^}]*))?\}"

    def replace(match: re.Match[str]) -> str:
        var_name = match.group(1)
        default = match.group(2) if match.lastindex and match.lastindex > 1 else None

        if var_name in env:
            return env[var_name]
        if default is not None:
            return default
        return match.group(0)  # Return original if not found

    return re.sub(pattern, replace, value)


def _deep_merge_dict(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries.

    Override values take precedence. Arrays are replaced (not merged).

    Args:
        base: Base dictionary
        override: Override dictionary

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = _deep_merge_dict(result[key], value)
        else:
            # Override (or add new) value
            result[key] = value

    return result


def _deep_merge_services(base_services: dict[str, Any], override_services: dict[str, Any]) -> dict[str, Any]:
    """Deep merge service definitions.

    Args:
        base_services: Base services dict
        override_services: Override services dict

    Returns:
        Merged services dict
    """
    result = base_services.copy()

    for service_name, service_config in override_services.items():
        if service_name in result:
            # Merge existing service
            result[service_name] = _deep_merge_dict(result[service_name], service_config)
        else:
            # Add new service
            result[service_name] = service_config

    return result


def discover_compose_files(
    directory: str | Path,
    base_name: str | None = None,
    environment: str | None = None,
    explicit_files: list[str] | None = None,
) -> list[Path]:
    """Discover compose files based on naming convention.

    File resolution order:
    1. Explicit files (if provided via -f flag)
    2. Base file (compose.yml, docker-compose.yml, compose.yaml)
    3. Image file (*.image.yml, *.image.yaml)
    4. Environment file (*.{env}.yml, *.{env}.yaml)

    Args:
        directory: Directory to search in
        base_name: Base name for files (e.g., "jenkins")
        environment: Environment name (e.g., "dev", "prod")
        explicit_files: Explicit file paths (overrides auto-discovery)

    Returns:
        List of compose file paths in merge order

    Raises:
        ComposeParserError: If no files found or image file missing
    """
    directory = Path(directory).resolve()

    # If explicit files provided, use them
    if explicit_files:
        files = [Path(f).resolve() if not Path(f).is_absolute() else Path(f) for f in explicit_files]
        missing = [f for f in files if not f.exists()]
        if missing:
            msg = f"Compose files not found: {', '.join(str(f) for f in missing)}"
            raise ComposeParserError(msg)
        return files

    discovered: list[Path] = []

    # 1. Find base file (optional)
    base_patterns = ["compose.yml", "docker-compose.yml", "compose.yaml", "docker-compose.yaml"]
    for pattern in base_patterns:
        base_file = directory / pattern
        if base_file.exists():
            discovered.append(base_file)
            logger.debug("compose_base_file_found", file=str(base_file))
            break

    # 2. Find image file (required if base_name provided)
    if base_name:
        image_patterns = [
            f"{base_name}.image.yml",
            f"{base_name}.image.yaml",
            "*.image.yml",
            "*.image.yaml",
        ]
        for pattern in image_patterns:
            if "*" in pattern:
                # Glob pattern
                matches = list(directory.glob(pattern))
                if matches:
                    discovered.append(matches[0])
                    logger.debug("compose_image_file_found", file=str(matches[0]))
                    break
            else:
                # Exact pattern
                image_file = directory / pattern
                if image_file.exists():
                    discovered.append(image_file)
                    logger.debug("compose_image_file_found", file=str(image_file))
                    break
    else:
        # Try to find any .image.yml file
        image_matches = list(directory.glob("*.image.yml")) + list(directory.glob("*.image.yaml"))
        if image_matches:
            discovered.append(image_matches[0])
            logger.debug("compose_image_file_found", file=str(image_matches[0]))

    # 3. Find environment file (if environment specified)
    if environment:
        if base_name:
            env_patterns = [
                f"{base_name}.{environment}.yml",
                f"{base_name}.{environment}.yaml",
            ]
        else:
            env_patterns = [
                f"*.{environment}.yml",
                f"*.{environment}.yaml",
            ]

        for pattern in env_patterns:
            if "*" in pattern:
                # Glob pattern
                matches = list(directory.glob(pattern))
                if matches:
                    discovered.append(matches[0])
                    logger.debug("compose_env_file_found", file=str(matches[0]), env=environment)
                    break
            else:
                # Exact pattern
                env_file = directory / pattern
                if env_file.exists():
                    discovered.append(env_file)
                    logger.debug("compose_env_file_found", file=str(env_file), env=environment)
                    break

    if not discovered:
        msg = f"No compose files found in {directory}"
        raise ComposeParserError(msg)

    logger.info(
        "compose_files_discovered",
        directory=str(directory),
        files=[str(f) for f in discovered],
        count=len(discovered),
    )

    return discovered


def parse_compose_file(file_path: str | Path, env: dict[str, str] | None = None) -> dict[str, Any]:
    """Parse a single compose file.

    Args:
        file_path: Path to compose file
        env: Environment variables for substitution

    Returns:
        Parsed compose file as dictionary

    Raises:
        ComposeParserError: If file cannot be parsed
    """
    file_path = Path(file_path).resolve()

    if not file_path.exists():
        msg = f"Compose file not found: {file_path}"
        raise ComposeParserError(msg)

    logger.debug("compose_file_parsing", file=str(file_path))

    try:
        with file_path.open() as f:
            content = f.read()

        # Substitute environment variables
        if env is None:
            env = dict(os.environ)

        # Simple substitution for ${VAR} patterns in the content
        content = _substitute_env_vars(content, env)

        # Parse YAML
        data = _yaml.load(content)

        if not isinstance(data, dict):
            msg = f"Compose file must be a dictionary: {file_path}"
            raise ComposeParserError(msg)

        logger.debug("compose_file_parsed", file=str(file_path), services=len(data.get("services", {})))

        return data

    except Exception as e:
        msg = f"Error parsing compose file {file_path}: {e}"
        raise ComposeParserError(msg) from e


def merge_compose_files(files: list[Path] | list[str], env: dict[str, str] | None = None) -> dict[str, Any]:
    """Merge multiple compose files in order.

    Files are merged in the order provided. Later files override earlier ones.

    Args:
        files: List of compose file paths
        env: Environment variables for substitution

    Returns:
        Merged compose file as dictionary
    """
    if not files:
        msg = "No compose files to merge"
        raise ComposeParserError(msg)

    merged: dict[str, Any] = {}

    for file_path in files:
        file_data = parse_compose_file(file_path, env)

        # Merge top-level keys
        for key, value in file_data.items():
            if key == "services":
                # Special handling for services (deep merge)
                if "services" not in merged:
                    merged["services"] = {}
                merged["services"] = _deep_merge_services(merged["services"], value)
            elif key in ("networks", "volumes", "configs", "secrets"):
                # Merge these sections
                if key not in merged:
                    merged[key] = {}
                if isinstance(value, dict):
                    merged[key] = _deep_merge_dict(merged.get(key, {}), value)
                else:
                    merged[key] = value
            else:
                # Override other keys (version, name, etc.)
                merged[key] = value

    logger.info(
        "compose_files_merged",
        files=[str(f) for f in files],
        services=len(merged.get("services", {})),
    )

    return merged


def _parse_service(name: str, config: dict[str, Any]) -> ComposeService:
    """Parse a service configuration.

    Args:
        name: Service name
        config: Service configuration dict

    Returns:
        ComposeService instance
    """
    return ComposeService(
        name=name,
        image=config.get("image"),
        build=config.get("build"),
        command=config.get("command"),
        entrypoint=config.get("entrypoint"),
        environment=config.get("environment"),
        ports=config.get("ports"),
        volumes=config.get("volumes"),
        networks=config.get("networks"),
        depends_on=config.get("depends_on"),
        labels=config.get("labels"),
        restart=config.get("restart"),
        healthcheck=config.get("healthcheck"),
        deploy=config.get("deploy"),
        working_dir=config.get("working_dir"),
        user=config.get("user"),
        hostname=config.get("hostname"),
        extra_hosts=config.get("extra_hosts"),
        config=config,
    )


def _parse_network(name: str, config: dict[str, Any] | None) -> ComposeNetwork:
    """Parse a network configuration.

    Args:
        name: Network name
        config: Network configuration dict (None for simple networks)

    Returns:
        ComposeNetwork instance
    """
    if config is None:
        config = {}

    return ComposeNetwork(
        name=name,
        driver=config.get("driver"),
        driver_opts=config.get("driver_opts"),
        external=config.get("external", False),
        external_name=config.get("name") if config.get("external") else None,
        labels=config.get("labels"),
        ipam=config.get("ipam"),
        config=config,
    )


def _parse_volume(name: str, config: dict[str, Any] | None) -> ComposeVolume:
    """Parse a volume configuration.

    Args:
        name: Volume name
        config: Volume configuration dict (None for simple volumes)

    Returns:
        ComposeVolume instance
    """
    if config is None:
        config = {}

    return ComposeVolume(
        name=name,
        driver=config.get("driver"),
        driver_opts=config.get("driver_opts"),
        external=config.get("external", False),
        external_name=config.get("name") if config.get("external") else None,
        labels=config.get("labels"),
        config=config,
    )


class ComposeParser:
    """Compose file parser with multi-file support."""

    def __init__(self, directory: str | Path | None = None):
        """Initialize compose parser.

        Args:
            directory: Working directory for file discovery (default: current directory)
        """
        self.directory = Path(directory).resolve() if directory else Path.cwd()
        self.logger = get_logger(__name__)

    def discover_files(
        self,
        base_name: str | None = None,
        environment: str | None = None,
        explicit_files: list[str] | None = None,
    ) -> list[Path]:
        """Discover compose files.

        Args:
            base_name: Base name for files (e.g., "jenkins")
            environment: Environment name (e.g., "dev", "prod")
            explicit_files: Explicit file paths (overrides auto-discovery)

        Returns:
            List of compose file paths in merge order
        """
        return discover_compose_files(
            self.directory, base_name=base_name, environment=environment, explicit_files=explicit_files
        )

    def parse(
        self,
        base_name: str | None = None,
        environment: str | None = None,
        explicit_files: list[str] | None = None,
        service_filter: list[str] | None = None,
    ) -> ComposeFile:
        """Parse and merge compose files.

        Args:
            base_name: Base name for files (e.g., "jenkins")
            environment: Environment name (e.g., "dev", "prod")
            explicit_files: Explicit file paths (overrides auto-discovery)
            service_filter: List of service names to include (None = all services)

        Returns:
            Parsed ComposeFile instance

        Raises:
            ComposeParserError: If files cannot be parsed or merged
        """
        # Discover files
        files = self.discover_files(base_name=base_name, environment=environment, explicit_files=explicit_files)

        # Merge files
        merged_data = merge_compose_files(files)

        # Parse into models
        services: dict[str, ComposeService] = {}
        for name, config in merged_data.get("services", {}).items():
            services[name] = _parse_service(name, config)

        # Filter services if requested
        if service_filter:
            services = {name: svc for name, svc in services.items() if name in service_filter}

        networks: dict[str, ComposeNetwork] | None = None
        if "networks" in merged_data:
            networks = {}
            for name, config in merged_data["networks"].items():
                networks[name] = _parse_network(name, config)

        volumes: dict[str, ComposeVolume] | None = None
        if "volumes" in merged_data:
            volumes = {}
            for name, config in merged_data["volumes"].items():
                volumes[name] = _parse_volume(name, config)

        compose_file = ComposeFile(
            version=merged_data.get("version"),
            name=merged_data.get("name"),
            services=services,
            networks=networks,
            volumes=volumes,
            configs=merged_data.get("configs"),
            secrets=merged_data.get("secrets"),
            raw=merged_data,
        )

        self.logger.info(
            "compose_file_parsed",
            files=[str(f) for f in files],
            services=list(compose_file.services.keys()),
            environment=environment,
        )

        return compose_file
