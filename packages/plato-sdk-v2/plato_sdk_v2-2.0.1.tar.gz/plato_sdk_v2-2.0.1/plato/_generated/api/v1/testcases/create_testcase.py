"""Create Testcase"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.test_case_create_request import TestCaseCreateRequest


def _build_request_args(
    body: TestCaseCreateRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/testcases"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: TestCaseCreateRequest,
) -> Any:
    """Create Testcase"""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: TestCaseCreateRequest,
) -> Any:
    """Create Testcase"""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
