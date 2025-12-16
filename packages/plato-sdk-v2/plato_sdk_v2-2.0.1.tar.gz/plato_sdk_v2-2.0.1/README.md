# Plato Python SDK

Python SDK for the Plato API v2.

## Installation

```bash
pip install plato-sdk
```

## Quick Start

```python
from plato.v2 import Client, Env

# Synchronous usage
with Client() as client:
    # Create a session with an environment
    with client.session(envs=[Env.artifact("espocrm")]) as session:
        # Batch operations on all environments
        session.reset()
        state = session.get_state()

        # Per-environment operations
        for env in session.envs:
            result = env.execute("ls -la")
            print(result)
```

## Environment Configuration

The SDK provides three modes for creating environments using the `Env` helper, which returns `EnvConfig` objects:

### Mode 1: Simulator with Tag (Default)

Start from a snapshotted artifact using "simulator:tag" format:

```python
from plato.v2 import Client, Env

with Client() as client:
    # Use default :prod-latest tag
    session = client.session(envs=[Env.artifact("espocrm")])
    # Equivalent to: Env.artifact("espocrm:prod-latest")

    # Use custom tag
    session = client.session(envs=[Env.artifact("espocrm:staging")])

    # With custom alias
    session = client.session(envs=[Env.artifact("espocrm", alias="crm")])
```

### Mode 2: Explicit Artifact ID

Start
from
a
specific
artifact
snapshot
using
its
ID:

```python
from plato.v2 import Client, Env

with Client() as client:
    # Use explicit artifact ID
    session = client.session(envs=[
        Env.artifact(artifact_id="artifact-123", alias="my-env")
    ])
```

### Mode 3: Custom VM Resources

Create
a
blank
VM
with
custom
CPU,
memory,
and
disk
configuration:

```python
from plato.v2 import Client, Env, SimConfigCompute

with Client() as client:
    # Create blank VM with custom resources
    session = client.session(envs=[
        Env.resource(
            "redis",
            SimConfigCompute(cpus=4, memory=8192, disk=20000),
            alias="cache"
        )
    ])
```

### Multiple Environments

```python
from plato.v2 import Client, Env, SimConfigCompute

with Client() as client:
    # Mix artifact and resource-based environments
    envs = [
        Env.artifact("espocrm", alias="crm"),
        Env.artifact("wordpress:staging", alias="blog"),
        Env.resource("redis", SimConfigCompute(cpus=2, memory=4096), alias="cache"),
    ]

    with client.session.from_envs(envs) as session:
        # Access environments by alias
        crm = session.get_env("crm")
        blog = session.get_env("blog")
        cache = session.get_env("cache")

        if crm:
            crm.execute("echo 'Hello CRM'")
        if blog:
            blog.execute("echo 'Hello Blog'")
```

### Create Session from Task

```python
from plato.v2 import Client

with Client() as client:
    # Create session from a task ID
    session = client.from_task(task_id=123)
```

## Async Usage

```python
import asyncio
from plato.v2 import AsyncClient, Env

async def main():
    async with AsyncClient() as client:
        async with await client.session(envs=[Env.artifact("espocrm")]) as session:
            await session.reset()
            state = await session.get_state()

            for env in session.envs:
                result = await env.execute("ls -la")
                print(result)

asyncio.run(main())
```

## Session Operations

```python
from plato.v2 import Client, Env

with Client() as client:
    with client.session(envs=[Env.artifact("espocrm")]) as session:
        # Reset all environments
        session.reset()

        # Get state from all environments
        state = session.get_state()

        # Execute command on all environments
        results = session.execute("ls -la", timeout=30)

        # Create snapshot of all environments
        snapshots = session.snapshot()

        # Evaluate session
        evaluation = session.evaluate()

        # Send heartbeat (automatically done when using context manager)
        session.heartbeat()
```

## Per-Environment Operations

```python
from plato.v2 import Client, Env

with Client() as client:
    with client.session(envs=[Env.artifact("espocrm", alias="crm")]) as session:
        # Get specific environment
        env = session.get_env("crm")

        if env:
            # Execute command
            result = env.execute("pwd")
            print(result.stdout)

            # Reset environment
            env.reset()

            # Create snapshot
            snapshot = env.snapshot()

            # Get state
            state = env.get_state()

            # Close environment
            env.close()
```

## Configuration

Set
your
API
key
via
environment
variable:

```bash
export PLATO_API_KEY=your-api-key
```

Or
pass
it
directly:

```python
from plato.v2 import Client

client = Client(api_key="your-api-key")
```

Configure
custom
base
URL:

```bash
export PLATO_BASE_URL=https://custom.plato.so
```

Or:

```python
client = Client(base_url="https://custom.plato.so")
```

## License

MIT
