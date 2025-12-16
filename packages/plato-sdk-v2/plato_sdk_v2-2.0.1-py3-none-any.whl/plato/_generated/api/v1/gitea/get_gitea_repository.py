"""Get Gitea Repository"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.repository_response import RepositoryResponse


def _build_request_args(
    owner: str,
    repo: str,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/gitea/repositories/{owner}/{repo}"

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
    owner: str,
    repo: str,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> RepositoryResponse:
    """Get a specific Gitea repository"""

    request_args = _build_request_args(
        owner=owner,
        repo=repo,
        authorization=authorization,
        x_internal_service=x_internal_service,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return RepositoryResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> RepositoryResponse:
    """Get a specific Gitea repository"""

    request_args = _build_request_args(
        owner=owner,
        repo=repo,
        authorization=authorization,
        x_internal_service=x_internal_service,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return RepositoryResponse.from_dict(response.json())
