"""Get Replay Score Data"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args(
    agent_artifact_id: int,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/session/replay-score/{agent_artifact_id}"

    return {
        "method": "GET",
        "url": url,
    }


def sync(
    client: httpx.Client,
    agent_artifact_id: int,
) -> Any:
    """Get replay score data for a specific agent artifact ID.
    Returns original sessions and their corresponding replay sessions with summary statistics."""

    request_args = _build_request_args(
        agent_artifact_id=agent_artifact_id,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    agent_artifact_id: int,
) -> Any:
    """Get replay score data for a specific agent artifact ID.
    Returns original sessions and their corresponding replay sessions with summary statistics."""

    request_args = _build_request_args(
        agent_artifact_id=agent_artifact_id,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
