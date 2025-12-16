"""Interface Cursor"""

from __future__ import annotations

import httpx

from plato._generated.models.cursor_position_request import CursorPositionRequest
from plato._generated.models.cursor_position_response import CursorPositionResponse


def sync(
    client: httpx.Client,
    job_id: str,
    body: CursorPositionRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> CursorPositionResponse:
    """Move the cursor to a position without clicking."""

    url = f"/api/v2/interface/{job_id}/cursor"

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

    return CursorPositionResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    job_id: str,
    body: CursorPositionRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> CursorPositionResponse:
    """Move the cursor to a position without clicking."""

    url = f"/api/v2/interface/{job_id}/cursor"

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

    return CursorPositionResponse.from_dict(response.json())
