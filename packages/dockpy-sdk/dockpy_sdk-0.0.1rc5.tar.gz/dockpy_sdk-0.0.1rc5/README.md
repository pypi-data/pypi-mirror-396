# dockpy-sdk

Pure Python Docker SDK with async operations and direct Docker Engine API access.

## Installation

```bash
pip install dockpy-sdk
```

## Features

- **Async/Await**: Built on asyncio and httpx
- **Direct API**: No subprocess calls, pure HTTP/Unix socket
- **Container Management**: Create, start, stop, logs, inspect, and more
- **Image Management**: Pull, push, build, tag, remove, and more
- **Type Safe**: 100% type hints with mypy support
- **Well Tested**: Comprehensive test coverage

## Quick Start

```python
from dockpysdk.client import AsyncDockerClient

async def main():
    async with AsyncDockerClient() as client:
        # List containers
        containers = await client.containers.list()
        for container in containers:
            print(f"{container.id}: {container.name}")

import asyncio
asyncio.run(main())
```

## Container Operations

```python
# Create and run a container
container = await client.containers.create(
    "nginx:latest",
    name="my-web-server"
)
await container.start()

# Get logs
logs = await client.containers.logs(container.id)

# Stop and remove
await container.stop()
await container.remove()
```

## Image Operations

```python
# Pull image
image = await client.images.pull("python:3.10")

# List images
images = await client.images.list()

# Build image
async for line in await client.images.build(dockerfile="Dockerfile"):
    print(line)
```

## Documentation

See the [main repository](https://gerrit.bbdevs.com/dockpy) for full documentation.

## License

Apache License 2.0 - See LICENSE file for details.

