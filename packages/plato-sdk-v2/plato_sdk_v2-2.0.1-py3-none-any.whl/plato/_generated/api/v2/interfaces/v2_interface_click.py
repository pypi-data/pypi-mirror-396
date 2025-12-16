"""Interface Click"""

from __future__ import annotations

import httpx

from plato._generated.models.click_request import ClickRequest
from plato._generated.models.click_response import ClickResponse


def sync(
    client: httpx.Client,
    job_id: str,
    body: ClickRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> ClickResponse:
    """Click at a position on the interface."""

    url = f"/api/v2/interface/{job_id}/click"

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

    return ClickResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    job_id: str,
    body: ClickRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> ClickResponse:
    """Click at a position on the interface."""

    url = f"/api/v2/interface/{job_id}/click"

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

    return ClickResponse.from_dict(response.json())
