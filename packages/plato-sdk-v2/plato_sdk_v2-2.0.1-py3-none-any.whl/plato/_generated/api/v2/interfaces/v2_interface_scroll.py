"""Interface Scroll"""

from __future__ import annotations

import httpx

from plato._generated.models.scroll_request import ScrollRequest
from plato._generated.models.scroll_response import ScrollResponse


def sync(
    client: httpx.Client,
    job_id: str,
    body: ScrollRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> ScrollResponse:
    """Scroll the interface.

    Positive y scrolls down, negative y scrolls up.
    Positive x scrolls right, negative x scrolls left."""

    url = f"/api/v2/interface/{job_id}/scroll"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    response = client.request(
        "POST",
        url,
        json=body.to_dict(),
        headers=headers,
    )
    response.raise_for_status()

    return ScrollResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    job_id: str,
    body: ScrollRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> ScrollResponse:
    """Scroll the interface.

    Positive y scrolls down, negative y scrolls up.
    Positive x scrolls right, negative x scrolls left."""

    url = f"/api/v2/interface/{job_id}/scroll"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    response = await client.request(
        "POST",
        url,
        json=body.to_dict(),
        headers=headers,
    )
    response.raise_for_status()

    return ScrollResponse.from_dict(response.json())
