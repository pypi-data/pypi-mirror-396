"""Archive Organization Testcase"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.archive_organization_test_case_request import ArchiveOrganizationTestCaseRequest


def _build_request_args(
    body: ArchiveOrganizationTestCaseRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/testcases/archive-organization-testcase"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: ArchiveOrganizationTestCaseRequest,
) -> Any:
    """Archive an OrganizationTestCase by setting is_active=False.
    This removes the test case from the human recorder dashboard."""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: ArchiveOrganizationTestCaseRequest,
) -> Any:
    """Archive an OrganizationTestCase by setting is_active=False.
    This removes the test case from the human recorder dashboard."""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
