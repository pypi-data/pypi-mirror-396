"""Archive Agent Artifact"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args(
    artifact_id: str,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/agent-artifacts/{artifact_id}"

    return {
        "method": "DELETE",
        "url": url,
    }


def sync(
    client: httpx.Client,
    artifact_id: str,
) -> Any:
    """Archive Agent Artifact"""

    request_args = _build_request_args(
        artifact_id=artifact_id,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    artifact_id: str,
) -> Any:
    """Archive Agent Artifact"""

    request_args = _build_request_args(
        artifact_id=artifact_id,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
