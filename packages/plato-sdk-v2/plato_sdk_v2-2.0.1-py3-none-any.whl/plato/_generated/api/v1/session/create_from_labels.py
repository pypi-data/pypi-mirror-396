"""Create From Labels"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.create_test_case_from_labels_request import CreateTestCaseFromLabelsRequest


def _build_request_args(
    session_id: str,
    body: CreateTestCaseFromLabelsRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/session/{session_id}/create-from-labels"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    session_id: str,
    body: CreateTestCaseFromLabelsRequest,
) -> Any:
    """Create a new test case from labels of a session that has a sample test case.
    This endpoint:
    1. Validates that the session has a test case with is_sample=true
    2. Creates a new test case with the provided task prompt and name
    3. Updates the session to use the new test case
    4. Runs generate_mutations and other post-creation tasks"""

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
    body: CreateTestCaseFromLabelsRequest,
) -> Any:
    """Create a new test case from labels of a session that has a sample test case.
    This endpoint:
    1. Validates that the session has a test case with is_sample=true
    2. Creates a new test case with the provided task prompt and name
    3. Updates the session to use the new test case
    4. Runs generate_mutations and other post-creation tasks"""

    request_args = _build_request_args(
        session_id=session_id,
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
