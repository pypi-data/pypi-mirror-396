"""Interface Key"""

from __future__ import annotations

import httpx

from plato._generated.models.key_request import KeyRequest
from plato._generated.models.key_response import KeyResponse


def sync(
    client: httpx.Client,
    job_id: str,
    body: KeyRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> KeyResponse:
    """Press a key or key combination.

    Examples: 'Enter', 'Tab', 'ctrl+c', 'alt+tab', 'shift+a'"""

    url = f"/api/v2/interface/{job_id}/key"

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

    return KeyResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    job_id: str,
    body: KeyRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> KeyResponse:
    """Press a key or key combination.

    Examples: 'Enter', 'Tab', 'ctrl+c', 'alt+tab', 'shift+a'"""

    url = f"/api/v2/interface/{job_id}/key"

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

    return KeyResponse.from_dict(response.json())
