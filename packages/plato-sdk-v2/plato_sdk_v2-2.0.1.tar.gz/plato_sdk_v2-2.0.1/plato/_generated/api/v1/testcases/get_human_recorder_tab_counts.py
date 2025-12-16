"""Get Human Recorder Tab Counts"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args(
    admin_view: bool | None = None,
    is_sample: bool | None = None,
    organization_id: int | None | None = None,
    simulator_id: int | None | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/testcases/human-recorder/tab-counts"

    params: dict[str, Any] = {}
    if admin_view is not None:
        params["admin_view"] = admin_view
    if is_sample is not None:
        params["is_sample"] = is_sample
    if organization_id is not None:
        params["organization_id"] = organization_id
    if simulator_id is not None:
        params["simulator_id"] = simulator_id

    return {
        "method": "GET",
        "url": url,
        "params": params,
    }


def sync(
    client: httpx.Client,
    admin_view: bool | None = None,
    is_sample: bool | None = None,
    organization_id: int | None | None = None,
    simulator_id: int | None | None = None,
) -> Any:
    """Get counts for all human recorder tabs from OrganizationTestCase.stage

    Args:
        organization_id: Optional organization ID to query. If provided and user is admin,
                        will query that organization. Non-admin users can only access their own organization.
        simulator_id: Optional simulator ID to filter by."""

    request_args = _build_request_args(
        admin_view=admin_view,
        is_sample=is_sample,
        organization_id=organization_id,
        simulator_id=simulator_id,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    admin_view: bool | None = None,
    is_sample: bool | None = None,
    organization_id: int | None | None = None,
    simulator_id: int | None | None = None,
) -> Any:
    """Get counts for all human recorder tabs from OrganizationTestCase.stage

    Args:
        organization_id: Optional organization ID to query. If provided and user is admin,
                        will query that organization. Non-admin users can only access their own organization.
        simulator_id: Optional simulator ID to filter by."""

    request_args = _build_request_args(
        admin_view=admin_view,
        is_sample=is_sample,
        organization_id=organization_id,
        simulator_id=simulator_id,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
