# Plato SDK v2
#
# Usage:
#   from plato.v2 import Plato, Session, Environment  # Sync
#   from plato.v2 import AsyncPlato, AsyncSession, AsyncEnvironment  # Async
#   from plato.v2 import Env, SimConfigCompute  # Helpers

from plato.v2 import async_, sync

# Async exports (prefixed with Async)
from plato.v2.async_.client import AsyncPlato
from plato.v2.async_.environment import Environment as AsyncEnvironment
from plato.v2.async_.session import Session as AsyncSession

# Sync exports (default)
from plato.v2.sync.client import Plato
from plato.v2.sync.environment import Environment
from plato.v2.sync.session import Session

# Helper types
from plato.v2.types import (
    Env,
    EnvFromArtifact,
    EnvFromResource,
    EnvFromSimulator,
    SimConfigCompute,
)

__all__ = [
    # Sync
    "Plato",
    "Session",
    "Environment",
    # Async
    "AsyncPlato",
    "AsyncSession",
    "AsyncEnvironment",
    # Helpers
    "Env",
    "EnvFromSimulator",
    "EnvFromArtifact",
    "EnvFromResource",
    "SimConfigCompute",
    # Submodules
    "sync",
    "async_",
]
