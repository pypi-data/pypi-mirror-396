"""Interface Type"""

from __future__ import annotations

import httpx

from plato._generated.models.type_request import TypeRequest
from plato._generated.models.type_response import TypeResponse


def sync(
    client: httpx.Client,
    job_id: str,
    body: TypeRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> TypeResponse:
    """Type text on the interface."""

    url = f"/api/v2/interface/{job_id}/type"

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

    return TypeResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    job_id: str,
    body: TypeRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> TypeResponse:
    """Type text on the interface."""

    url = f"/api/v2/interface/{job_id}/type"

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

    return TypeResponse.from_dict(response.json())
