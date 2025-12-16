"""Get Agent Artifacts"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args() -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/agent-artifacts/"

    return {
        "method": "GET",
        "url": url,
    }


def sync(
    client: httpx.Client,
) -> Any:
    """Get Agent Artifacts"""

    request_args = _build_request_args()

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
) -> Any:
    """Get Agent Artifacts"""

    request_args = _build_request_args()

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
