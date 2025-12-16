"""Create Agent Artifact"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.create_agent_artifact_request import CreateAgentArtifactRequest


def _build_request_args(
    body: CreateAgentArtifactRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/agent-artifacts/"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: CreateAgentArtifactRequest,
) -> Any:
    """Create Agent Artifact"""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: CreateAgentArtifactRequest,
) -> Any:
    """Create Agent Artifact"""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
