"""Update Testcase"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.test_case_update_request import TestCaseUpdateRequest


def _build_request_args(
    id: int,
    body: TestCaseUpdateRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/testcases/{id}"

    return {
        "method": "PUT",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    id: int,
    body: TestCaseUpdateRequest,
) -> Any:
    """Update Testcase"""

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
    body: TestCaseUpdateRequest,
) -> Any:
    """Update Testcase"""

    request_args = _build_request_args(
        id=id,
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
