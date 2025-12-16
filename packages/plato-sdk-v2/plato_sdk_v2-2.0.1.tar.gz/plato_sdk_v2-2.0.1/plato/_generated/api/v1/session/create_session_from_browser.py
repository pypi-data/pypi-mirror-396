"""Create Session From Browser"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.recording import Recording


def _build_request_args(
    body: Recording,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/session/from-browser"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: Recording,
) -> Any:
    """Create Session From Browser"""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: Recording,
) -> Any:
    """Create Session From Browser"""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
