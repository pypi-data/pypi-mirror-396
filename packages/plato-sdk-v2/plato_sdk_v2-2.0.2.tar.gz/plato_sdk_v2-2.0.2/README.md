# Plato Python SDK

Python SDK for the Plato API v2.

## Installation

```bash
pip install plato-sdk-v2
```

Or with uv:

```bash
uv add plato-sdk-v2
```

## Configuration

Create a `.env` file in your project root:

```bash
PLATO_API_KEY=your-api-key
PLATO_BASE_URL=https://plato.so  # optional, defaults to https://plato.so
```

Or set environment variables directly:

```bash
export PLATO_API_KEY=your-api-key
```

## Usage

There are two main flows depending on your use case:

### Flow 1: Create Session from Environments

Use this when you want to spin up environments for development, testing, or custom automation.

```python
import asyncio
from plato.v2 import AsyncPlato, Env

async def main():
    plato = AsyncPlato()

    # Create session with one or more environments
    # (heartbeat starts automatically to keep session alive)
    session = await plato.sessions.create(
        envs=[
            Env.simulator("gitea", dataset="blank", alias="gitea"),
            Env.simulator("kanboard", alias="kanboard"),
        ],
        timeout=600,
    )

    # Reset environments to initial state
    await session.reset()

    # Get public URLs for browser access
    public_urls = await session.get_public_url()
    for alias, url in public_urls.items():
        print(f"{alias}: {url}")

    # ============================================
    # Interact with environments via browser/API
    # ============================================

    # Get state mutations from all environments
    state = await session.get_state()
    print(state)

    # Cleanup
    await session.close()
    await plato.close()

asyncio.run(main())
```

### Flow 2: Create Session from Task

Use this when running evaluations against predefined tasks. This flow includes task evaluation at the end.

```python
import asyncio
from plato.v2 import AsyncPlato

async def main():
    plato = AsyncPlato()

    # Create session from task ID
    # (heartbeat starts automatically to keep session alive)
    session = await plato.sessions.create(task=123, timeout=600)

    # Reset environments to initial state
    await session.reset()

    # Get public URLs for browser access
    public_urls = await session.get_public_url()
    for alias, url in public_urls.items():
        print(f"{alias}: {url}")

    # ============================================
    # Interact with environments via browser/API
    # ============================================

    # Get state mutations from all environments
    state = await session.get_state()
    print(state)

    # Evaluate task completion
    evaluation = await session.evaluate()
    print(f"Task completed: {evaluation}")

    # Cleanup
    await session.close()
    await plato.close()

asyncio.run(main())
```

## Environment Configuration

Two ways to specify environments:

```python
from plato.v2 import Env

# 1. From simulator (most common)
Env.simulator("gitea")                          # default tag
Env.simulator("gitea", tag="staging")           # specific tag
Env.simulator("gitea", dataset="blank")         # specific dataset
Env.simulator("gitea", alias="my-git")          # custom alias

# 2. From artifact ID
Env.artifact("artifact-abc123")
Env.artifact("artifact-abc123", alias="my-env")
```

## Per-Environment Operations

Access individual environments within a session:

```python
# Get all environments
for env in session.envs:
    print(f"{env.alias}: {env.job_id}")

# Get specific environment by alias
gitea = session.get_env("gitea")

if gitea:
    # Execute shell command
    result = await gitea.execute("whoami", timeout=30)
    print(result)

    # Get state for this environment only
    state = await gitea.get_state()

    # Reset this environment only
    await gitea.reset()
```

## Sync Client

A synchronous client is also available:

```python
from plato.v2 import Plato, Env

plato = Plato()

# Heartbeat starts automatically
session = plato.sessions.create(
    envs=[Env.simulator("gitea", alias="gitea")],
    timeout=600,
)

session.reset()

public_urls = session.get_public_url()
state = session.get_state()

session.close()
plato.close()
```

## License

MIT
