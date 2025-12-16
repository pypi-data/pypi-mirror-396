"""Get Session"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args(
    session_id: str,
    include_images: bool | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/session/{session_id}"

    params: dict[str, Any] = {}
    if include_images is not None:
        params["include_images"] = include_images

    return {
        "method": "GET",
        "url": url,
        "params": params,
    }


def sync(
    client: httpx.Client,
    session_id: str,
    include_images: bool | None = None,
) -> Any:
    """Get Session"""

    request_args = _build_request_args(
        session_id=session_id,
        include_images=include_images,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    session_id: str,
    include_images: bool | None = None,
) -> Any:
    """Get Session"""

    request_args = _build_request_args(
        session_id=session_id,
        include_images=include_images,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
