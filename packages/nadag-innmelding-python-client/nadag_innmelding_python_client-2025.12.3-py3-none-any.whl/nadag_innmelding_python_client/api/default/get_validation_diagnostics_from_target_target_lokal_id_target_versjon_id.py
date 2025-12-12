from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.diagnostics_dto import DiagnosticsDto
from ...types import Response


def _get_kwargs(
    target_lokal_id: UUID,
    target_versjon_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/validation/diagnosticsFromTarget/{target_lokal_id}/{target_versjon_id}".format(
            target_lokal_id=quote(str(target_lokal_id), safe=""),
            target_versjon_id=quote(str(target_versjon_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | DiagnosticsDto | None:
    if response.status_code == 200:
        response_200 = DiagnosticsDto.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | DiagnosticsDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    target_lokal_id: UUID,
    target_versjon_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | DiagnosticsDto]:
    """Fetches diagnostics for a target ID.

     Fetches all diagnostics from the Identifikasjon of a target.

    Args:
        target_lokal_id (UUID):
        target_versjon_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DiagnosticsDto]
    """

    kwargs = _get_kwargs(
        target_lokal_id=target_lokal_id,
        target_versjon_id=target_versjon_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    target_lokal_id: UUID,
    target_versjon_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Any | DiagnosticsDto | None:
    """Fetches diagnostics for a target ID.

     Fetches all diagnostics from the Identifikasjon of a target.

    Args:
        target_lokal_id (UUID):
        target_versjon_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | DiagnosticsDto
    """

    return sync_detailed(
        target_lokal_id=target_lokal_id,
        target_versjon_id=target_versjon_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    target_lokal_id: UUID,
    target_versjon_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | DiagnosticsDto]:
    """Fetches diagnostics for a target ID.

     Fetches all diagnostics from the Identifikasjon of a target.

    Args:
        target_lokal_id (UUID):
        target_versjon_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DiagnosticsDto]
    """

    kwargs = _get_kwargs(
        target_lokal_id=target_lokal_id,
        target_versjon_id=target_versjon_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    target_lokal_id: UUID,
    target_versjon_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Any | DiagnosticsDto | None:
    """Fetches diagnostics for a target ID.

     Fetches all diagnostics from the Identifikasjon of a target.

    Args:
        target_lokal_id (UUID):
        target_versjon_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | DiagnosticsDto
    """

    return (
        await asyncio_detailed(
            target_lokal_id=target_lokal_id,
            target_versjon_id=target_versjon_id,
            client=client,
        )
    ).parsed
