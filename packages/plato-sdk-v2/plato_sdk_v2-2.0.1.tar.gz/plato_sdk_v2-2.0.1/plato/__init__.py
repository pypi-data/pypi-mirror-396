# Plato SDK
#
# v1: Legacy SDK (deprecated)
# v2: New SDK with separate sync/async modules
#
# Usage (v2 - recommended):
#   from plato.v2.sync import Client
#   from plato.v2.async_ import Client
#   from plato import EnvOption
#
# Usage (v1 - deprecated):
#   from plato import Plato, SyncPlato

# Defer imports to avoid circular issues with _generated
__all__ = ["EnvOption", "v2"]


def __getattr__(name):
    """Lazy import to avoid loading all modules at once."""
    if name == "v2":
        from plato import v2

        return v2
    if name == "EnvOption":
        from plato._generated.models.env_option import EnvOption

        return EnvOption
    if name in ("Plato", "SyncPlato", "PlatoTask", "v1"):
        try:
            from plato import v1

            if name == "v1":
                return v1
            return getattr(v1, name)
        except ImportError:
            raise AttributeError(f"module 'plato' has no attribute '{name}' (v1 unavailable)")
    raise AttributeError(f"module 'plato' has no attribute '{name}'")
