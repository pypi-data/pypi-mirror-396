# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""dockpysdk: Docker SDK with async operations.

Author: A M (am@bbdevs.com)

Created At: 08 Nov 2025
"""

from __future__ import annotations

from .client import AsyncDockerClient
from .compose_dependencies import DependencyResolver
from .compose_orchestrator import ComposeOrchestrator
from .compose_parser import ComposeParser, discover_compose_files, merge_compose_files, parse_compose_file
from .models import ComposeFile, ComposeNetwork, ComposeService, ComposeVolume
from .networks import NetworkManager
from .volumes import VolumeManager


__version__ = "1.0.0"

__all__ = [
    "AsyncDockerClient",
    "ComposeFile",
    "ComposeNetwork",
    "ComposeOrchestrator",
    "ComposeParser",
    "ComposeService",
    "ComposeVolume",
    "DependencyResolver",
    "NetworkManager",
    "VolumeManager",
    "__version__",
    "discover_compose_files",
    "merge_compose_files",
    "parse_compose_file",
]
