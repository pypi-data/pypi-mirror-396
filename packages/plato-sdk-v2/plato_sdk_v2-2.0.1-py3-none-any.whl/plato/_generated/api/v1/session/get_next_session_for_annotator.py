"""Get Next Session For Annotator"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args(
    exclude_session_id: str | None | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/session/next-for-annotator"

    params: dict[str, Any] = {}
    if exclude_session_id is not None:
        params["exclude_session_id"] = exclude_session_id

    return {
        "method": "GET",
        "url": url,
        "params": params,
    }


def sync(
    client: httpx.Client,
    exclude_session_id: str | None | None = None,
) -> Any:
    """Get the next session for an annotator based on the same filtering criteria used in the Sessions page.
    This endpoint filters sessions server-side for better performance."""

    request_args = _build_request_args(
        exclude_session_id=exclude_session_id,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    exclude_session_id: str | None | None = None,
) -> Any:
    """Get the next session for an annotator based on the same filtering criteria used in the Sessions page.
    This endpoint filters sessions server-side for better performance."""

    request_args = _build_request_args(
        exclude_session_id=exclude_session_id,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
