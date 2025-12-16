"""Get Ui Events"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args(
    session_id: str,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/session/{session_id}/ui-events"

    return {
        "method": "GET",
        "url": url,
    }


def sync(
    client: httpx.Client,
    session_id: str,
) -> Any:
    """Get UI events for a session from S3."""

    request_args = _build_request_args(
        session_id=session_id,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    session_id: str,
) -> Any:
    """Get UI events for a session from S3."""

    request_args = _build_request_args(
        session_id=session_id,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
