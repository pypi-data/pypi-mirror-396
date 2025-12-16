"""Close Interface"""

from __future__ import annotations

from typing import Any

import httpx


def sync(
    client: httpx.Client,
    job_id: str,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> dict[str, Any]:
    """Close an interface."""

    url = f"/api/v2/interface/{job_id}/close"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    response = client.request(
        "POST",
        url,
        headers=headers,
    )
    response.raise_for_status()

    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    job_id: str,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> dict[str, Any]:
    """Close an interface."""

    url = f"/api/v2/interface/{job_id}/close"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    response = await client.request(
        "POST",
        url,
        headers=headers,
    )
    response.raise_for_status()

    return response.json()
