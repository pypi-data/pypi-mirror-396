"""Version Bump Testcase"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.version_bump_request import VersionBumpRequest


def _build_request_args(
    id: int,
    body: VersionBumpRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/testcases/{id}/version-bump"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    id: int,
    body: VersionBumpRequest,
) -> Any:
    """Bump the version of a test case, add a note to version_update_notes, and set rejected to False."""

    request_args = _build_request_args(
        id=id,
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    id: int,
    body: VersionBumpRequest,
) -> Any:
    """Bump the version of a test case, add a note to version_update_notes, and set rejected to False."""

    request_args = _build_request_args(
        id=id,
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
