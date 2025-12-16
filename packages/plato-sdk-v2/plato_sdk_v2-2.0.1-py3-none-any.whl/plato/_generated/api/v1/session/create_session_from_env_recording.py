"""Create Session From Env Recording"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args() -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/session/from-env-recording"

    return {
        "method": "POST",
        "url": url,
    }


def sync(
    client: httpx.Client,
) -> Any:
    """Create a session from environment recording files (video and events JSON).
    Similar to HAR sessions, this creates a RunSession and uploads the files to S3.
    Supports both user session and API key authentication."""

    request_args = _build_request_args()

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
) -> Any:
    """Create a session from environment recording files (video and events JSON).
    Similar to HAR sessions, this creates a RunSession and uploads the files to S3.
    Supports both user session and API key authentication."""

    request_args = _build_request_args()

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
