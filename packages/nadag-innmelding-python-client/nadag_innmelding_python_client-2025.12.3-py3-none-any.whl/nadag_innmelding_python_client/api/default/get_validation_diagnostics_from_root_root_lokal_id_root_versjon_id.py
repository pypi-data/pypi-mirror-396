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
    root_lokal_id: UUID,
    root_versjon_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/validation/diagnosticsFromRoot/{root_lokal_id}/{root_versjon_id}".format(
            root_lokal_id=quote(str(root_lokal_id), safe=""),
            root_versjon_id=quote(str(root_versjon_id), safe=""),
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
    root_lokal_id: UUID,
    root_versjon_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | DiagnosticsDto]:
    """Fetches a DiagnosticsDto from root ID.

     Fetches all diagnostics from the Identifikasjon of a root.

    Args:
        root_lokal_id (UUID):
        root_versjon_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DiagnosticsDto]
    """

    kwargs = _get_kwargs(
        root_lokal_id=root_lokal_id,
        root_versjon_id=root_versjon_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    root_lokal_id: UUID,
    root_versjon_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Any | DiagnosticsDto | None:
    """Fetches a DiagnosticsDto from root ID.

     Fetches all diagnostics from the Identifikasjon of a root.

    Args:
        root_lokal_id (UUID):
        root_versjon_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | DiagnosticsDto
    """

    return sync_detailed(
        root_lokal_id=root_lokal_id,
        root_versjon_id=root_versjon_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    root_lokal_id: UUID,
    root_versjon_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | DiagnosticsDto]:
    """Fetches a DiagnosticsDto from root ID.

     Fetches all diagnostics from the Identifikasjon of a root.

    Args:
        root_lokal_id (UUID):
        root_versjon_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DiagnosticsDto]
    """

    kwargs = _get_kwargs(
        root_lokal_id=root_lokal_id,
        root_versjon_id=root_versjon_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    root_lokal_id: UUID,
    root_versjon_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Any | DiagnosticsDto | None:
    """Fetches a DiagnosticsDto from root ID.

     Fetches all diagnostics from the Identifikasjon of a root.

    Args:
        root_lokal_id (UUID):
        root_versjon_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | DiagnosticsDto
    """

    return (
        await asyncio_detailed(
            root_lokal_id=root_lokal_id,
            root_versjon_id=root_versjon_id,
            client=client,
        )
    ).parsed
