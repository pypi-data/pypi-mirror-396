"""Create"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.create_env_request import CreateEnvRequest
from plato._generated.models.make_env_response import MakeEnvResponse


def _build_request_args(
    body: CreateEnvRequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/env/make2"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_api_key is not None:
        headers["X-API-Key"] = x_api_key

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
        "headers": headers,
    }


def sync(
    client: httpx.Client,
    body: CreateEnvRequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> MakeEnvResponse:
    """Create"""

    request_args = _build_request_args(
        body=body,
        authorization=authorization,
        x_api_key=x_api_key,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return MakeEnvResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    body: CreateEnvRequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> MakeEnvResponse:
    """Create"""

    request_args = _build_request_args(
        body=body,
        authorization=authorization,
        x_api_key=x_api_key,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return MakeEnvResponse.from_dict(response.json())
