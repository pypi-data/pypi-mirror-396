"""Search Sessions By Ids"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args(
    session_ids: str,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/session/search-sessions-replays"

    params: dict[str, Any] = {}
    if session_ids is not None:
        params["session_ids"] = session_ids

    return {
        "method": "GET",
        "url": url,
        "params": params,
    }


def sync(
    client: httpx.Client,
    session_ids: str,
) -> Any:
    """Search for specific original sessions by their IDs and return them with their replays.
    Session IDs should be space-separated."""

    request_args = _build_request_args(
        session_ids=session_ids,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    session_ids: str,
) -> Any:
    """Search for specific original sessions by their IDs and return them with their replays.
    Session IDs should be space-separated."""

    request_args = _build_request_args(
        session_ids=session_ids,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
