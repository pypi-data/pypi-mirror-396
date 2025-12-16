# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Image management operations.

Author: A M (am@bbdevs.com)
Created At: 08 Nov 2025
"""

from __future__ import annotations

import fnmatch
import io
import json
import re
import tarfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import TYPE_CHECKING, Any

from dockpycore.logging import get_logger, log_context

from .build_formatter import format_build_stream, format_pull_stream, format_push_stream
from .models import Image, ImageInspect


if TYPE_CHECKING:
    from .http_client import DockerHTTPClient


__all__ = ["ImageManager"]

logger = get_logger(__name__)


class ImageManager:
    """Manage Docker images.

    Provides methods for image lifecycle management, building,
    and inspection.

    Usage:
        async with AsyncDockerClient() as client:
            # Pull an image
            image = await client.images.pull("nginx:latest")

            # List images
            images = await client.images.list()

            # Tag image
            await client.images.tag("nginx:latest", "myregistry.com/nginx:v1")

            # Push image
            await client.images.push("myregistry.com/nginx:v1")

            # Remove image
            await client.images.remove("nginx:latest")
    """

    def __init__(self, client: DockerHTTPClient):
        """Initialize image manager.

        Args:
            client: HTTP client for API communication
        """
        self._client = client
        self.logger = get_logger("dockpysdk.images")

    async def list(
        self,
        *,
        all: bool = False,
        filters: dict[str, Any] | None = None,
        shared_size: bool = False,
    ) -> list[Image]:
        """List images.

        Args:
            all: Include untagged images
            filters: Filter images
            shared_size: Include shared size

        Returns:
            List of images

        Example:
            # List all images
            images = await manager.list(all=True)

            # List images by repository
            images = await manager.list(
                filters={"reference": ["nginx"]}
            )
        """
        with log_context(operation="image_list"):
            self.logger.debug("image_list", all=all)

            params: dict[str, Any] = {
                "all": all,
                "shared-size": shared_size,
            }
            if filters:
                params["filters"] = json.dumps(filters)

            response = await self._client.get("/images/json", params=params)
            data = response.json()

            images = [Image.from_api(item) for item in data]

            self.logger.info("image_list_complete", count=len(images))

            return images

    async def pull(
        self,
        repository: str,
        *,
        tag: str = "latest",
        quiet: bool = False,
        format_output: bool = True,
    ) -> Image:
        """Pull an image from registry.

        Args:
            repository: Repository name (e.g., "nginx", "myregistry.com/image")
            tag: Image tag (default: latest)
            quiet: Suppress output
            format_output: Format pull output in TUI-like style (default: True)

        Returns:
            Pulled image

        Example:
            image = await manager.pull("nginx", tag="1.21")
            image = await manager.pull("myregistry.com/app", tag="v1.0")
        """
        with log_context(operation="image_pull", repository=repository):
            image_ref = f"{repository}:{tag}"
            self.logger.info("image_pull_start", image=image_ref)

            params = {"fromImage": repository, "tag": tag}
            if quiet:
                params["quiet"] = quiet

            should_format = format_output and not quiet

            if should_format:
                # Use streaming with formatter
                async def raw_lines() -> AsyncIterator[str]:
                    async with self._client.stream(
                        "POST",
                        "/images/create",
                        params=params,
                    ) as response:
                        async for line in response.aiter_lines():
                            yield line

                async for _data in format_pull_stream(raw_lines(), image_ref, write_to_stdout=True):
                    pass  # Formatter handles output, we just consume the stream
            else:
                # Use non-streaming for quiet mode
                await self._client.post(
                    "/images/create",
                    params=params,
                )

            self.logger.info("image_pulled", image=image_ref)

            # Return image info
            return await self.inspect(image_ref)

    async def push(
        self,
        repository: str,
        *,
        tag: str = "latest",
        quiet: bool = False,
        format_output: bool = True,
    ) -> None:
        """Push an image to registry.

        Args:
            repository: Repository name
            tag: Image tag
            quiet: Suppress output
            format_output: Format push output in TUI-like style (default: True)

        Example:
            await manager.push("myregistry.com/app", tag="v1.0")
        """
        with log_context(operation="image_push", repository=repository):
            image_ref = f"{repository}:{tag}"
            self.logger.info("image_push_start", image=image_ref)

            params = {"tag": image_ref}
            if quiet:
                params["quiet"] = quiet

            should_format = format_output and not quiet

            if should_format:
                # Use streaming with formatter
                async def raw_lines() -> AsyncIterator[str]:
                    async with self._client.stream(
                        "POST",
                        f"/images/{repository}/push",
                        params=params,
                    ) as response:
                        async for line in response.aiter_lines():
                            yield line

                async for _data in format_push_stream(raw_lines(), image_ref, write_to_stdout=True):
                    pass  # Formatter handles output, we just consume the stream
            else:
                # Use non-streaming for quiet mode
                await self._client.post(
                    f"/images/{repository}/push",
                    params=params,
                )

            self.logger.info("image_pushed", image=image_ref)

    async def tag(
        self,
        source: str,
        repository: str,
        *,
        tag: str = "latest",
    ) -> None:
        """Tag an image.

        Args:
            source: Source image name (e.g., "nginx:latest")
            repository: Target repository
            tag: Target tag

        Example:
            await manager.tag("nginx:latest", "myregistry.com/nginx", tag="v1.0")
        """
        with log_context(
            operation="image_tag",
            source=source,
            target=f"{repository}:{tag}",
        ):
            self.logger.info(
                "image_tag",
                source=source,
                repository=repository,
                tag=tag,
            )

            params = {
                "repo": repository,
                "tag": tag,
            }

            await self._client.post(
                f"/images/{source}/tag",
                params=params,
            )

            self.logger.info(
                "image_tagged",
                source=source,
                target=f"{repository}:{tag}",
            )

    async def inspect(self, image_id: str) -> Image:
        """Get image details.

        Args:
            image_id: Image ID or name

        Returns:
            Image with details

        Example:
            image = await manager.inspect("nginx:latest")
            print(f"Size: {image.size} bytes")
        """
        with log_context(operation="image_inspect", image_id=image_id):
            self.logger.debug("image_inspect", image_id=image_id)

            response = await self._client.get(f"/images/{image_id}/json")
            data = response.json()

            # Convert inspect response to Image model
            image = Image(
                id=data["Id"],
                repo_tags=data.get("RepoTags") or [],
                repo_digests=data.get("RepoDigests") or [],
                size=data.get("Size", 0),
                virtual_size=data.get("VirtualSize", 0),
                created=data.get("Created", 0),
                shared_size=data.get("SharedSize"),
                labels=data.get("Config", {}).get("Labels") or {},
            )

            self.logger.debug("image_inspected", image_id=image_id)

            return image

    async def inspect_detailed(self, image_id: str) -> ImageInspect:
        """Get detailed image information.

        Args:
            image_id: Image ID or name

        Returns:
            Detailed image information

        Example:
            details = await manager.inspect_detailed("nginx:latest")
            print(f"Architecture: {details.architecture}")
            print(f"OS: {details.os}")
        """
        with log_context(operation="image_inspect_detailed", image_id=image_id):
            response = await self._client.get(f"/images/{image_id}/json")
            data = response.json()

            return ImageInspect.from_api(data)

    async def remove(
        self,
        image_id: str,
        *,
        force: bool = False,
        noprune: bool = False,
    ) -> None:
        """Remove an image.

        Args:
            image_id: Image ID or name
            force: Force removal
            noprune: Do not delete untagged parents

        Example:
            await manager.remove("nginx:latest", force=True)
        """
        with log_context(operation="image_remove", image_id=image_id):
            self.logger.info(
                "image_remove",
                image_id=image_id,
                force=force,
                noprune=noprune,
            )

            params = {"force": force, "noprune": noprune}

            await self._client.delete(f"/images/{image_id}", params=params)

            self.logger.info("image_removed", image_id=image_id)

    async def history(self, image_id: str) -> list[dict[str, Any]]:
        """Get image history.

        Args:
            image_id: Image ID or name

        Returns:
            List of history entries

        Example:
            history = await manager.history("nginx:latest")
            for entry in history:
                print(f"Created: {entry['Created']}")
                print(f"By: {entry['CreatedBy']}")
        """
        with log_context(operation="image_history", image_id=image_id):
            self.logger.debug("image_history", image_id=image_id)

            response = await self._client.get(f"/images/{image_id}/history")
            data = response.json()

            self.logger.info("image_history_complete", image_id=image_id, count=len(data))

            return data

    async def prune(
        self,
        *,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Prune unused images.

        Args:
            filters: Filter pruning (e.g., {"dangling": ["true"]})

        Returns:
            Prune result with deleted images and freed space

        Example:
            result = await manager.prune()
            print(f"Deleted images: {len(result['ImagesDeleted'])}")
            print(f"Freed space: {result['SpaceReclaimed']}")
        """
        with log_context(operation="image_prune"):
            self.logger.info("image_prune_start")

            params: dict[str, Any] = {}
            if filters:
                params["filters"] = json.dumps(filters)

            response = await self._client.post("/images/prune", params=params)
            data = response.json()

            self.logger.info(
                "image_prune_complete",
                deleted_count=len(data.get("ImagesDeleted", [])),
                space_freed=data.get("SpaceReclaimed", 0),
            )

            return data

    async def search(
        self,
        term: str,
        *,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Search for images in registry.

        Args:
            term: Search term
            limit: Number of results

        Returns:
            List of search results

        Example:
            results = await manager.search("nginx", limit=10)
            for result in results:
                print(f"{result['Name']}: {result['Description']}")
        """
        with log_context(operation="image_search", term=term):
            self.logger.debug("image_search", term=term, limit=limit)

            params = {"term": term, "limit": limit}

            response = await self._client.get(
                "/images/search",
                params=params,
            )
            data = response.json()

            self.logger.info("image_search_complete", term=term, count=len(data))

            return data

    def _read_dockerignore(self, path: Path) -> list[str]:
        """Read and parse .dockerignore file.

        Args:
            path: Build context directory

        Returns:
            List of exclusion patterns from .dockerignore
        """
        dockerignore_path = path / ".dockerignore"
        if not dockerignore_path.exists():
            return []

        patterns: list[str] = []
        with dockerignore_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                patterns.append(line)

        return patterns

    def _create_build_context(
        self,
        path: Path,
        dockerfile: str = "Dockerfile",
        exclude: list[str] | None = None,
    ) -> bytes:
        """Create a tar archive from build context directory.

        Args:
            path: Build context directory
            dockerfile: Dockerfile path relative to context
            exclude: Additional patterns to exclude from context

        Returns:
            Tar archive bytes
        """
        # Read .dockerignore patterns
        exclude_patterns = self._read_dockerignore(path)

        # Add user-provided exclude patterns if any
        if exclude:
            exclude_patterns.extend(exclude)

        buffer = io.BytesIO()

        with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
            # Collect all files first for deterministic ordering
            files_to_add: list[tuple[Path, str]] = []

            for item in path.rglob("*"):
                if item.is_dir():
                    continue

                rel_path = item.relative_to(path)
                rel_str = str(rel_path).replace("\\", "/")  # Normalize path separators

                if self._should_exclude(rel_str, exclude_patterns):
                    continue

                files_to_add.append((item, rel_str))

            # Sort files for deterministic tar creation (important for caching)
            files_to_add.sort(key=lambda x: x[1])

            # Add files with normalized timestamps for cache stability
            for item, rel_str in files_to_add:
                self.logger.info("adding_file", file=rel_str)

                # Get file info and normalize timestamp for cache stability
                tarinfo = tar.gettarinfo(item, arcname=rel_str)
                # Set mtime to 0 to ensure consistent checksums when content doesn't change
                tarinfo.mtime = 0
                tarinfo.uid = 0
                tarinfo.gid = 0
                tarinfo.uname = ""
                tarinfo.gname = ""
                # Preserve mode (permissions) as it's content-relevant

                with item.open("rb") as f:
                    tar.addfile(tarinfo, f)

            # Add Dockerfile with normalized timestamp
            dockerfile_path = path / dockerfile
            if dockerfile_path.exists():
                tarinfo = tar.gettarinfo(dockerfile_path, arcname="Dockerfile")
                tarinfo.mtime = 0
                tarinfo.uid = 0
                tarinfo.gid = 0
                tarinfo.uname = ""
                tarinfo.gname = ""

                with dockerfile_path.open("rb") as f:
                    tar.addfile(tarinfo, f)

        buffer.seek(0)
        return buffer.read()

    def _should_exclude(self, rel_str: str, patterns: list[str]) -> bool:
        """Check if a path should be excluded based on Docker ignore patterns.

        Supports Docker .dockerignore format:
        - Directory patterns: "dir/" or "dir" matches directory and contents
        - Wildcards: "*.tar", "*cache*"
        - Root-relative: "/file" matches only at root
        - Path components: matches any part of the path

        Args:
            rel_str: Relative path string (normalized with forward slashes)
            patterns: List of exclusion patterns

        Returns:
            True if path should be excluded
        """
        path_parts = rel_str.split("/")

        for pattern in patterns:
            # Handle negation (future support - skip for now)
            if pattern.startswith("!"):
                continue

            # Normalize pattern
            pattern = pattern.strip()
            if not pattern:
                continue

            # Remove leading slash (Docker treats /pattern same as pattern)
            if pattern.startswith("/"):
                pattern = pattern[1:]

            # Check if pattern matches entire path
            if fnmatch.fnmatch(rel_str, pattern):
                return True

            # Check if pattern matches any path component
            for part in path_parts:
                if fnmatch.fnmatch(part, pattern):
                    return True

            # Handle directory patterns (pattern ending with / or exact directory match)
            pattern_base = pattern.rstrip("/")
            if pattern.endswith("/") or pattern_base in path_parts:
                # Check if any parent directory matches
                for i in range(len(path_parts)):
                    parent_path = "/".join(path_parts[: i + 1])
                    if fnmatch.fnmatch(parent_path, pattern_base):
                        return True
                    if pattern_base == parent_path:
                        return True

        return False

    def _build_params(
        self,
        *,
        tag: str | None,
        dockerfile: str,
        buildargs: dict[str, str] | None,
        labels: dict[str, str] | None,
        target: str | None,
        platform: str | None,
        quiet: bool,
        nocache: bool,
        rm: bool,
        forcerm: bool,
        pull: bool,
        memory: int | None,
        memswap: int | None,
        cpushares: int | None,
        cpusetcpus: str | None,
    ) -> dict[str, Any]:
        """Build query parameters for Docker build API."""
        params: dict[str, Any] = {"rm": rm, "forcerm": forcerm}

        param_map: dict[str, tuple[str, Any]] = {
            "t": ("t", tag),
            "dockerfile": ("dockerfile", dockerfile if dockerfile != "Dockerfile" else None),
            "buildargs": ("buildargs", json.dumps(buildargs) if buildargs else None),
            "labels": ("labels", json.dumps(labels) if labels else None),
            "target": ("target", target),
            "platform": ("platform", platform),
            "q": ("q", "1" if quiet else None),
            "nocache": ("nocache", "1" if nocache else None),
            "pull": ("pull", "1" if pull else None),
            "memory": ("memory", memory),
            "memswap": ("memswap", memswap),
            "cpushares": ("cpushares", cpushares),
            "cpusetcpus": ("cpusetcpus", cpusetcpus),
        }

        for _key, (param_name, value) in param_map.items():
            if value is not None:
                params[param_name] = value

        return params

    def _prepare_context(
        self,
        path: Path | str | None,
        dockerfile: str,
        dockerfile_content: str | None,
        exclude: list[str] | None,
    ) -> bytes:
        """Prepare build context as tar archive."""
        if path:
            context_path = Path(path)
            if not context_path.exists():
                raise FileNotFoundError(f"Build context not found: {context_path}")
            if not context_path.is_dir():
                raise NotADirectoryError(f"Build context must be a directory: {context_path}")
            return self._create_build_context(context_path, dockerfile, exclude)

        if dockerfile_content:
            buffer = io.BytesIO()
            with tarfile.open(fileobj=buffer, mode="w") as tar:
                dockerfile_bytes = dockerfile_content.encode("utf-8")
                info = tarfile.TarInfo(name="Dockerfile")
                info.size = len(dockerfile_bytes)
                # Normalize metadata for cache stability
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                tar.addfile(info, io.BytesIO(dockerfile_bytes))
            buffer.seek(0)
            return buffer.read()

        raise ValueError("Either 'path' or 'dockerfile_content' must be provided")

    def _extract_image_id(self, data: dict[str, Any]) -> str | None:
        """Extract image ID from build response."""
        if "aux" in data and "ID" in data["aux"]:
            return data["aux"]["ID"]
        if "stream" in data:
            match = re.search(r"Successfully built ([a-f0-9]+)", data["stream"])
            if match:
                return match.group(1)
        return None

    async def build(
        self,
        path: Path | str | None = None,
        *,
        dockerfile: str = "Dockerfile",
        dockerfile_content: str | None = None,
        tag: str | None = None,
        buildargs: dict[str, str] | None = None,
        labels: dict[str, str] | None = None,
        target: str | None = None,
        platform: str | None = None,
        quiet: bool = False,
        nocache: bool = False,
        rm: bool = True,
        forcerm: bool = False,
        pull: bool = False,
        memory: int | None = None,
        memswap: int | None = None,
        cpushares: int | None = None,
        cpusetcpus: str | None = None,
        exclude: list[str] | None = None,
        format_output: bool = True,
    ) -> Image:
        """Build an image from a directory context or Dockerfile content.

        Args:
            path: Build context directory path (recommended)
            dockerfile: Dockerfile path relative to context (default: "Dockerfile")
            dockerfile_content: Raw Dockerfile content (alternative to path)
            tag: Image tag (e.g., "myapp:v1.0")
            buildargs: Build-time variables (e.g., {"BUILD_PROJECT": "myapp"})
            labels: Labels to add to image
            target: Target build stage for multi-stage builds
            platform: Target platform (e.g., "linux/amd64")
            quiet: Suppress output
            nocache: Do not use cache
            rm: Remove intermediate containers (default: True)
            forcerm: Force remove intermediate containers
            pull: Always pull base images
            memory: Memory limit in bytes
            memswap: Memory swap limit in bytes
            cpushares: CPU shares
            cpusetcpus: CPUs to use (e.g., "0-3", "0,1")
            exclude: Patterns to exclude from build context
            format_output: Format build output in TUI-like style (default: True)

        Returns:
            Built Image with ID and tags

        Example:
            # Build from directory with build args
            image = await manager.build(
                path="/path/to/project",
                dockerfile="docker/Dockerfile.prod",
                tag="myapp:v1.0",
                buildargs={"BUILD_PROJECT": "myapp", "VERSION": "1.0"}
            )
            print(f"Built image: {image.id}")

            # Build from raw Dockerfile content
            image = await manager.build(
                dockerfile_content="FROM nginx\\nRUN apt-get update",
                tag="simple:latest"
            )
        """
        with log_context(operation="image_build", tag=tag, path=str(path) if path else None):
            self.logger.info(
                "image_build_start",
                tag=tag,
                path=str(path) if path else None,
                buildargs=list(buildargs.keys()) if buildargs else None,
            )

            params = self._build_params(
                tag=tag,
                dockerfile=dockerfile,
                buildargs=buildargs,
                labels=labels,
                target=target,
                platform=platform,
                quiet=quiet,
                nocache=nocache,
                rm=rm,
                forcerm=forcerm,
                pull=pull,
                memory=memory,
                memswap=memswap,
                cpushares=cpushares,
                cpusetcpus=cpusetcpus,
            )

            content = self._prepare_context(path, dockerfile, dockerfile_content, exclude)
            image_id: str | None = None

            # Determine if we should format output
            should_format = format_output and not quiet

            async with self._client.stream(
                "POST",
                "/build",
                params=params,
                content=content,
                headers={"Content-Type": "application/x-tar"},
            ) as response:
                if should_format:
                    # Use formatted output stream
                    async def raw_lines() -> AsyncIterator[str]:
                        async for line in response.aiter_lines():
                            yield line

                    async for data in format_build_stream(raw_lines(), tag=tag, write_to_stdout=True):
                        # Extract image_id from formatted stream
                        image_id = self._extract_image_id(data) or image_id

                        # Handle errors
                        if "error" in data:
                            error_msg = data.get("error", "Unknown build error")
                            error_detail = data.get("errorDetail", {}).get("message", error_msg)
                            self.logger.error("build_error", error=error_detail)
                            raise RuntimeError(f"Build failed: {error_detail}")
                else:
                    # Use original logging behavior
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            if "stream" in data and (stream_line := data["stream"].rstrip()):
                                if not quiet:
                                    self.logger.info("build_output", line=stream_line)
                            if "error" in data:
                                error_msg = data.get("error", "Unknown build error")
                                self.logger.error("build_error", error=error_msg)
                                raise RuntimeError(f"Build failed: {error_msg}")
                            image_id = self._extract_image_id(data) or image_id
                        except json.JSONDecodeError:
                            self.logger.warning("invalid_build_response", line=line)

            if not image_id:
                raise RuntimeError("Build completed but no image ID was returned")

            self.logger.info("image_build_complete", tag=tag, image_id=image_id)
            return await self.inspect(image_id)

    async def build_stream(
        self,
        path: Path | str | None = None,
        *,
        dockerfile: str = "Dockerfile",
        dockerfile_content: str | None = None,
        tag: str | None = None,
        buildargs: dict[str, str] | None = None,
        labels: dict[str, str] | None = None,
        target: str | None = None,
        platform: str | None = None,
        quiet: bool = False,
        nocache: bool = False,
        rm: bool = True,
        forcerm: bool = False,
        pull: bool = False,
        memory: int | None = None,
        memswap: int | None = None,
        cpushares: int | None = None,
        cpusetcpus: str | None = None,
        exclude: list[str] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Build an image and stream output.

        Same parameters as build(), but yields build output lines instead of
        returning the final image. Useful for progress display.

        Yields:
            Build output lines as dicts with "stream", "error", or "aux" keys

        Example:
            async for line in manager.build_stream(path=".", tag="myapp:v1"):
                if "stream" in line:
                    print(line["stream"], end="")
                elif "error" in line:
                    print(f"ERROR: {line['error']}")
        """
        with log_context(operation="image_build_stream", tag=tag):
            self.logger.info("image_build_stream_start", tag=tag)

            params = self._build_params(
                tag=tag,
                dockerfile=dockerfile,
                buildargs=buildargs,
                labels=labels,
                target=target,
                platform=platform,
                quiet=quiet,
                nocache=nocache,
                rm=rm,
                forcerm=forcerm,
                pull=pull,
                memory=memory,
                memswap=memswap,
                cpushares=cpushares,
                cpusetcpus=cpusetcpus,
            )

            content = self._prepare_context(path, dockerfile, dockerfile_content, exclude)

            async with self._client.stream(
                "POST",
                "/build",
                params=params,
                content=content,
                headers={"Content-Type": "application/x-tar"},
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            self.logger.warning("invalid_build_response", line=line)

            self.logger.info("image_build_stream_complete", tag=tag)

    async def load(self, tar_path: Path | str) -> Image:
        """Load image from tar file.

        Args:
            tar_path: Path to tar file containing the image

        Returns:
            Loaded image

        Example:
            image = await manager.load("/path/to/image.tar")
            print(f"Loaded: {image.repo_tags}")
        """
        path = Path(tar_path)

        with log_context(operation="image_load", tar_path=str(path)):
            self.logger.info("image_load_start", tar_path=str(path))

            if not path.exists():
                raise FileNotFoundError(f"Image tar file not found: {path}")

            # Read tar file
            tar_data = path.read_bytes()

            # POST to /images/load with streaming response
            # Docker API returns newline-delimited JSON stream
            image_ref = None
            async with self._client.stream(
                "POST",
                "/images/load",
                content=tar_data,
                headers={"Content-Type": "application/x-tar"},
            ) as response:
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        stream = data.get("stream", "")
                        # Extract image reference from response
                        # Patterns: "Loaded image: name:tag" or "Loaded image ID: sha256:..."
                        if match := re.search(r"Loaded image: ([^\s\n]+)", stream):
                            image_ref = match.group(1)
                        elif match := re.search(r"Loaded image ID: ([^\s\n]+)", stream):
                            image_ref = match.group(1)
                        # Check for error in response
                        if "error" in data:
                            error_msg = data.get("error", "Unknown error loading image")
                            self.logger.error("image_load_error", error=error_msg)
                            raise RuntimeError(f"Image load failed: {error_msg}")
                    except json.JSONDecodeError:
                        # Handle plain text response (older Docker versions)
                        if match := re.search(r"Loaded image: ([^\s\n]+)", line):
                            image_ref = match.group(1)
                        elif match := re.search(r"Loaded image ID: ([^\s\n]+)", line):
                            image_ref = match.group(1)

            self.logger.info("image_load_complete", tar_path=str(path), image_ref=image_ref)

            # Return image info
            if image_ref:
                return await self.inspect(image_ref)

            # If no reference found, return minimal image
            return Image(
                id="",
                repo_tags=[],
                repo_digests=[],
                size=0,
                virtual_size=0,
                created=0,
                shared_size=None,
                labels={},
            )

    async def save(self, image_id: str, output_path: Path | str) -> Path:
        """Save image to tar file.

        Args:
            image_id: Image ID or name to save
            output_path: Path to output tar file

        Returns:
            Path to saved tar file

        Example:
            path = await manager.save("nginx:latest", "/tmp/nginx.tar")
            print(f"Saved to: {path}")
        """
        path = Path(output_path)

        with log_context(operation="image_save", image_id=image_id, output_path=str(path)):
            self.logger.info("image_save_start", image_id=image_id, output_path=str(path))

            # Stream GET from /images/{name}/get
            async with self._client.stream("GET", f"/images/{image_id}/get") as response:
                # Write streamed chunks to file
                with path.open("wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)

            self.logger.info("image_save_complete", image_id=image_id, output_path=str(path))

            return path
