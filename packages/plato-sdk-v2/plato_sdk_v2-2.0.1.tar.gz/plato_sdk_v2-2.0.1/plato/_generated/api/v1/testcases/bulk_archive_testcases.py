"""Bulk Archive Testcases"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.bulk_archive_test_cases_request import BulkArchiveTestCasesRequest


def _build_request_args(
    body: BulkArchiveTestCasesRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/testcases/bulk-archive"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: BulkArchiveTestCasesRequest,
) -> Any:
    """Bulk Archive Testcases"""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: BulkArchiveTestCasesRequest,
) -> Any:
    """Bulk Archive Testcases"""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
