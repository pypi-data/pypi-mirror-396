# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Dependency resolution for compose services.

Author: A M (am@bbdevs.com)
Created At: 08 Nov 2025
"""

from __future__ import annotations

from collections import defaultdict

from dockpycore.exceptions import DockerSDKError
from dockpycore.logging import get_logger

from .models import ComposeFile, ComposeService


__all__ = [
    "DependencyResolver",
    "detect_circular_dependencies",
    "resolve_shutdown_order",
    "resolve_startup_order",
]

logger = get_logger(__name__)


class DependencyError(DockerSDKError):
    """Error resolving dependencies."""


class CircularDependencyError(DependencyError):
    """Circular dependency detected."""


def _extract_dependencies(service: ComposeService) -> list[str]:
    """Extract service dependencies from depends_on.

    Args:
        service: Service configuration

    Returns:
        List of service names this service depends on
    """
    if not service.depends_on:
        return []

    dependencies: list[str] = []

    if isinstance(service.depends_on, list):
        for dep in service.depends_on:
            if isinstance(dep, str):
                dependencies.append(dep)
            elif isinstance(dep, dict):
                # depends_on with conditions: {service: {condition: "service_started"}}
                dependencies.extend(dep.keys())
    elif isinstance(service.depends_on, dict):
        # depends_on as dict: {service: {condition: "service_started"}}
        dependencies.extend(service.depends_on.keys())

    return dependencies


def _build_dependency_graph(compose_file: ComposeFile) -> dict[str, list[str]]:
    """Build dependency graph from compose file.

    Args:
        compose_file: Parsed compose file

    Returns:
        Dictionary mapping service name to list of dependencies
    """
    graph: dict[str, list[str]] = {}

    for service_name, service in compose_file.services.items():
        dependencies = _extract_dependencies(service)
        graph[service_name] = dependencies

        # Validate dependencies exist
        for dep in dependencies:
            if dep not in compose_file.services:
                logger.warning(
                    "compose_dependency_missing",
                    service=service_name,
                    dependency=dep,
                )

    return graph


def detect_circular_dependencies(compose_file: ComposeFile) -> list[list[str]]:
    """Detect circular dependencies in compose file.

    Uses DFS to find cycles in the dependency graph.

    Args:
        compose_file: Parsed compose file

    Returns:
        List of cycles (each cycle is a list of service names)
    """
    graph = _build_dependency_graph(compose_file)
    visited: set[str] = set()
    rec_stack: set[str] = set()
    cycles: list[list[str]] = []

    def dfs(node: str, path: list[str]) -> None:
        """DFS to detect cycles."""
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path)
            elif neighbor in rec_stack:
                # Cycle detected
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        rec_stack.remove(node)
        path.pop()

    for service in compose_file.services:
        if service not in visited:
            dfs(service, [])

    return cycles


def resolve_startup_order(compose_file: ComposeFile, service_filter: list[str] | None = None) -> list[str]:
    """Resolve service startup order using topological sort.

    Args:
        compose_file: Parsed compose file
        service_filter: List of service names to include (None = all services)

    Returns:
        List of service names in startup order

    Raises:
        CircularDependencyError: If circular dependencies detected
    """
    # Check for circular dependencies
    cycles = detect_circular_dependencies(compose_file)
    if cycles:
        cycle_str = " -> ".join(cycles[0])
        msg = f"Circular dependency detected: {cycle_str}"
        raise CircularDependencyError(msg)

    # Build dependency graph
    graph = _build_dependency_graph(compose_file)

    # Filter services if requested
    if service_filter:
        # Only include filtered services and their dependencies
        filtered_graph: dict[str, list[str]] = {}
        for service in service_filter:
            if service in graph:
                # Include service and its dependencies (if in filter)
                filtered_graph[service] = [dep for dep in graph[service] if dep in service_filter]
        graph = filtered_graph

    # Topological sort using Kahn's algorithm
    # Calculate in-degree for each node
    in_degree: dict[str, int] = defaultdict(int)
    for service in graph:
        in_degree[service] = 0

    for service, dependencies in graph.items():
        for dep in dependencies:
            if dep in graph:  # Only count if dependency is in graph
                in_degree[service] += 1

    # Find all nodes with no incoming edges
    queue: list[str] = [service for service in graph if in_degree[service] == 0]
    result: list[str] = []

    while queue:
        # Remove a node with no incoming edges
        node = queue.pop(0)
        result.append(node)

        # For each neighbor, decrease in-degree
        for neighbor, dependencies in graph.items():
            if node in dependencies:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

    # Check if all nodes were processed
    if len(result) != len(graph):
        # This shouldn't happen if no cycles, but handle it
        remaining = set(graph.keys()) - set(result)
        logger.warning(
            "compose_dependency_resolution_incomplete",
            remaining=list(remaining),
        )
        # Add remaining services (they might be disconnected)
        result.extend(remaining)

    logger.info(
        "compose_startup_order_resolved",
        order=result,
        services=len(result),
    )

    return result


def resolve_shutdown_order(compose_file: ComposeFile, service_filter: list[str] | None = None) -> list[str]:
    """Resolve service shutdown order (reverse of startup order).

    Args:
        compose_file: Parsed compose file
        service_filter: List of service names to include (None = all services)

    Returns:
        List of service names in shutdown order (reverse dependency order)
    """
    startup_order = resolve_startup_order(compose_file, service_filter=service_filter)
    shutdown_order = list(reversed(startup_order))

    logger.info(
        "compose_shutdown_order_resolved",
        order=shutdown_order,
        services=len(shutdown_order),
    )

    return shutdown_order


class DependencyResolver:
    """Dependency resolver for compose services."""

    def __init__(self, compose_file: ComposeFile):
        """Initialize dependency resolver.

        Args:
            compose_file: Parsed compose file
        """
        self.compose_file = compose_file
        self.logger = get_logger(__name__)

    def get_dependencies(self, service_name: str) -> list[str]:
        """Get dependencies for a service.

        Args:
            service_name: Service name

        Returns:
            List of service names this service depends on
        """
        if service_name not in self.compose_file.services:
            return []

        service = self.compose_file.services[service_name]
        return _extract_dependencies(service)

    def get_dependents(self, service_name: str) -> list[str]:
        """Get services that depend on this service.

        Args:
            service_name: Service name

        Returns:
            List of service names that depend on this service
        """
        dependents: list[str] = []

        for name, service in self.compose_file.services.items():
            dependencies = _extract_dependencies(service)
            if service_name in dependencies:
                dependents.append(name)

        return dependents

    def resolve_startup_order(self, service_filter: list[str] | None = None) -> list[str]:
        """Resolve service startup order.

        Args:
            service_filter: List of service names to include (None = all services)

        Returns:
            List of service names in startup order
        """
        return resolve_startup_order(self.compose_file, service_filter=service_filter)

    def resolve_shutdown_order(self, service_filter: list[str] | None = None) -> list[str]:
        """Resolve service shutdown order.

        Args:
            service_filter: List of service names to include (None = all services)

        Returns:
            List of service names in shutdown order
        """
        return resolve_shutdown_order(self.compose_file, service_filter=service_filter)

    def detect_circular_dependencies(self) -> list[list[str]]:
        """Detect circular dependencies.

        Returns:
            List of cycles (each cycle is a list of service names)
        """
        return detect_circular_dependencies(self.compose_file)

    def can_start_parallel(self, services: list[str]) -> bool:
        """Check if services can be started in parallel.

        Services can be started in parallel if they don't depend on each other.

        Args:
            services: List of service names

        Returns:
            True if services can be started in parallel
        """
        # Build dependency set for all services
        all_deps: set[str] = set()
        for service in services:
            deps = self.get_dependencies(service)
            all_deps.update(deps)

        # Check if any service in the list depends on another in the list
        service_set = set(services)
        return not (service_set & all_deps)  # No intersection means no dependencies
