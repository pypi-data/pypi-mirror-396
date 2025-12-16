"""Create Computer Interface"""

from __future__ import annotations

import httpx

from plato._generated.models.computer_interface_option import ComputerInterfaceOption
from plato._generated.models.interface_info import InterfaceInfo


def sync(
    client: httpx.Client,
    body: ComputerInterfaceOption,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> InterfaceInfo:
    """Create a computer interface.

    Computer interfaces provide click, type, screenshot, and keyboard/mouse
    control for computer-use scenarios."""

    url = "/api/v2/interface/computer/create"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    response = client.request(
        "POST",
        url,
        json=body.to_dict(),
        headers=headers,
    )
    response.raise_for_status()

    return InterfaceInfo.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    body: ComputerInterfaceOption,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> InterfaceInfo:
    """Create a computer interface.

    Computer interfaces provide click, type, screenshot, and keyboard/mouse
    control for computer-use scenarios."""

    url = "/api/v2/interface/computer/create"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    response = await client.request(
        "POST",
        url,
        json=body.to_dict(),
        headers=headers,
    )
    response.raise_for_status()

    return InterfaceInfo.from_dict(response.json())
