"""Get Agent Artifact By Public Id"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args(
    public_id: str,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/agent-artifacts/{public_id}"

    return {
        "method": "GET",
        "url": url,
    }


def sync(
    client: httpx.Client,
    public_id: str,
) -> Any:
    """Get Agent Artifact By Public Id"""

    request_args = _build_request_args(
        public_id=public_id,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    public_id: str,
) -> Any:
    """Get Agent Artifact By Public Id"""

    request_args = _build_request_args(
        public_id=public_id,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
