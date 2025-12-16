"""Get My Gitea Info"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.gitea_info_response import GiteaInfoResponse


def _build_request_args(
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/gitea/my-info"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    return {
        "method": "GET",
        "url": url,
        "headers": headers,
    }


def sync(
    client: httpx.Client,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> GiteaInfoResponse:
    """Get the current user's Gitea info (auto-provisions if needed)"""

    request_args = _build_request_args(
        authorization=authorization,
        x_internal_service=x_internal_service,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return GiteaInfoResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> GiteaInfoResponse:
    """Get the current user's Gitea info (auto-provisions if needed)"""

    request_args = _build_request_args(
        authorization=authorization,
        x_internal_service=x_internal_service,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return GiteaInfoResponse.from_dict(response.json())
