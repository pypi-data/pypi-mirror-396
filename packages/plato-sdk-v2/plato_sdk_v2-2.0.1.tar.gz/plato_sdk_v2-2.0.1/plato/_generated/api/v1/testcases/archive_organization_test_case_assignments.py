"""Archive Organization Test Case Assignments"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.archive_organization_assignments_request import ArchiveOrganizationAssignmentsRequest


def _build_request_args(
    body: ArchiveOrganizationAssignmentsRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/testcases/organization-assignments/archive"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: ArchiveOrganizationAssignmentsRequest,
) -> Any:
    """Archive multiple OrganizationTestCase assignments.
    Admin-only endpoint for archiving annotator test assignments."""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: ArchiveOrganizationAssignmentsRequest,
) -> Any:
    """Archive multiple OrganizationTestCase assignments.
    Admin-only endpoint for archiving annotator test assignments."""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
