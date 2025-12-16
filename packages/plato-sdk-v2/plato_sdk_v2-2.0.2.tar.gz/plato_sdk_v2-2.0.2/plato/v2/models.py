"""Plato SDK v2 - Models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SimConfig(BaseModel):
    """Compute configuration for a blank VM."""

    cpus: int = Field(default=1, ge=1, le=8, description="vCPUs")
    memory: int = Field(default=2048, ge=512, le=16384, description="Memory in MB")
    disk: int = Field(default=10240, ge=1024, le=102400, description="Disk space in MB")


class EnvOption(BaseModel):
    """Configuration for a single environment in a session.

    Each EnvOption creates one job/VM. Provide either:
    - artifact_id: Use a specific artifact/snapshot
    - sim_config: Start a blank VM with specified resources

    If neither is provided, resolves artifact via the prod-latest tag.
    """

    simulator: str = Field(description="Simulator name (e.g., 'espocrm')")
    alias: str | None = Field(
        default=None,
        description="Custom name for this environment (defaults to simulator name)",
    )
    artifact_id: str | None = Field(default=None, description="Specific artifact/snapshot ID to use")
    sim_config: SimConfig | None = Field(
        default=None,
        description="Compute config for blank VM (mutually exclusive with artifact_id)",
    )

    @classmethod
    def from_simulator(cls, simulator: str, alias: str | None = None) -> EnvOption:
        """Create an EnvOption from just a simulator name (uses prod-latest artifact)."""
        return cls(simulator=simulator, alias=alias)

    @classmethod
    def from_artifact(cls, simulator: str, artifact_id: str, alias: str | None = None) -> EnvOption:
        """Create an EnvOption from a simulator and artifact_id."""
        return cls(simulator=simulator, artifact_id=artifact_id, alias=alias)

    @classmethod
    def blank_vm(
        cls,
        simulator: str,
        alias: str | None = None,
        cpus: int = 1,
        memory: int = 2048,
        disk: int = 10240,
    ) -> EnvOption:
        """Create an EnvOption for a blank VM with custom resources."""
        return cls(
            simulator=simulator,
            alias=alias,
            sim_config=SimConfig(cpus=cpus, memory=memory, disk=disk),
        )
