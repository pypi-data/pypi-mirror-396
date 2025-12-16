"""Get Env Recording"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args(
    session_id: str,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/session/{session_id}/env-recording"

    return {
        "method": "GET",
        "url": url,
    }


def sync(
    client: httpx.Client,
    session_id: str,
) -> Any:
    """Get env recording video URL and events for a session.

    This is for recordings created by the EnvGen Recorder extension,
    stored at env_recordings/{session_id}/."""

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
    """Get env recording video URL and events for a session.

    This is for recordings created by the EnvGen Recorder extension,
    stored at env_recordings/{session_id}/."""

    request_args = _build_request_args(
        session_id=session_id,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
