# Plato SDK
#
# v1: Legacy SDK (deprecated)
# v2: New SDK with separate sync/async modules
#
# Usage (v2 - recommended):
#   from plato.v2 import AsyncPlato, Plato, Env
#
# Usage (v1 - deprecated):
#   from plato import Plato, SyncPlato

from plato import v2 as v2

__all__ = ["v2"]


def __getattr__(name: str):
    """Lazy import to avoid loading all modules at once."""
    if name in ("Plato", "SyncPlato", "PlatoTask", "v1"):
        try:
            from plato import v1

            if name == "v1":
                return v1
            return getattr(v1, name)
        except ImportError:
            raise AttributeError(f"module 'plato' has no attribute '{name}' (v1 unavailable)")
    raise AttributeError(f"module 'plato' has no attribute '{name}'")
