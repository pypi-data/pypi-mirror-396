"""Update Session Testcase"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.update_session_test_case_request import UpdateSessionTestCaseRequest


def _build_request_args(
    session_id: str,
    body: UpdateSessionTestCaseRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/session/{session_id}/testcase"

    return {
        "method": "PUT",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    session_id: str,
    body: UpdateSessionTestCaseRequest,
) -> Any:
    """Associate a testcase with an existing session.
    Only available to Plato org (org_id == 5) for internal tooling."""

    request_args = _build_request_args(
        session_id=session_id,
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    session_id: str,
    body: UpdateSessionTestCaseRequest,
) -> Any:
    """Associate a testcase with an existing session.
    Only available to Plato org (org_id == 5) for internal tooling."""

    request_args = _build_request_args(
        session_id=session_id,
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
