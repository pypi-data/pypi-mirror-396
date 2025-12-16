"""Log State Mutation"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.log_response import LogResponse


def _build_request_args(
    session_id: str,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/env/{session_id}/log"

    return {
        "method": "POST",
        "url": url,
    }


def sync(
    client: httpx.Client,
    session_id: str,
) -> LogResponse:
    """Log a state mutation or batch of mutations."""

    request_args = _build_request_args(
        session_id=session_id,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return LogResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    session_id: str,
) -> LogResponse:
    """Log a state mutation or batch of mutations."""

    request_args = _build_request_args(
        session_id=session_id,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return LogResponse.from_dict(response.json())
