"""Update Simulator"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.app_api_v1_env_routes_updatesimulatorrequest import AppApiV1EnvRoutesUpdatesimulatorrequest
from plato._generated.models.simulator_response import SimulatorResponse


def _build_request_args(
    id: int,
    body: AppApiV1EnvRoutesUpdatesimulatorrequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/env/simulators/{id}"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_api_key is not None:
        headers["X-API-Key"] = x_api_key

    return {
        "method": "PUT",
        "url": url,
        "json": body.to_dict(),
        "headers": headers,
    }


def sync(
    client: httpx.Client,
    id: int,
    body: AppApiV1EnvRoutesUpdatesimulatorrequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> SimulatorResponse:
    """Update Simulator"""

    request_args = _build_request_args(
        id=id,
        body=body,
        authorization=authorization,
        x_api_key=x_api_key,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return SimulatorResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    id: int,
    body: AppApiV1EnvRoutesUpdatesimulatorrequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> SimulatorResponse:
    """Update Simulator"""

    request_args = _build_request_args(
        id=id,
        body=body,
        authorization=authorization,
        x_api_key=x_api_key,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return SimulatorResponse.from_dict(response.json())
