"""Assign Testcase To Organizations"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.assign_test_case_to_organizations_request import AssignTestCaseToOrganizationsRequest


def _build_request_args(
    id: int,
    body: AssignTestCaseToOrganizationsRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/testcases/{id}/assign-to-organizations"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    id: int,
    body: AssignTestCaseToOrganizationsRequest,
) -> Any:
    """Assign a test case to multiple annotator organizations.
    Creates OrganizationTestCase entries for each organization."""

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
    body: AssignTestCaseToOrganizationsRequest,
) -> Any:
    """Assign a test case to multiple annotator organizations.
    Creates OrganizationTestCase entries for each organization."""

    request_args = _build_request_args(
        id=id,
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
