from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.geoteknisk_unders import GeotekniskUnders
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    ekstern_id: str,
    ekstern_navnerom: str,
    ekstern_versjon_id: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["eksternId"] = ekstern_id

    params["eksternNavnerom"] = ekstern_navnerom

    params["eksternVersjonId"] = ekstern_versjon_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/nadag/innmelding/v1/GeotekniskUnders",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GeotekniskUnders | None:
    if response.status_code == 200:
        response_200 = GeotekniskUnders.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GeotekniskUnders]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    ekstern_id: str,
    ekstern_navnerom: str,
    ekstern_versjon_id: str | Unset = UNSET,
) -> Response[GeotekniskUnders]:
    """Fetches a GeotekniskUnders by external id.

     Fetches a GeotekniskUnders by external id. Returns the most recent one.

    Args:
        ekstern_id (str):
        ekstern_navnerom (str):
        ekstern_versjon_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GeotekniskUnders]
    """

    kwargs = _get_kwargs(
        ekstern_id=ekstern_id,
        ekstern_navnerom=ekstern_navnerom,
        ekstern_versjon_id=ekstern_versjon_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    ekstern_id: str,
    ekstern_navnerom: str,
    ekstern_versjon_id: str | Unset = UNSET,
) -> GeotekniskUnders | None:
    """Fetches a GeotekniskUnders by external id.

     Fetches a GeotekniskUnders by external id. Returns the most recent one.

    Args:
        ekstern_id (str):
        ekstern_navnerom (str):
        ekstern_versjon_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GeotekniskUnders
    """

    return sync_detailed(
        client=client,
        ekstern_id=ekstern_id,
        ekstern_navnerom=ekstern_navnerom,
        ekstern_versjon_id=ekstern_versjon_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    ekstern_id: str,
    ekstern_navnerom: str,
    ekstern_versjon_id: str | Unset = UNSET,
) -> Response[GeotekniskUnders]:
    """Fetches a GeotekniskUnders by external id.

     Fetches a GeotekniskUnders by external id. Returns the most recent one.

    Args:
        ekstern_id (str):
        ekstern_navnerom (str):
        ekstern_versjon_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GeotekniskUnders]
    """

    kwargs = _get_kwargs(
        ekstern_id=ekstern_id,
        ekstern_navnerom=ekstern_navnerom,
        ekstern_versjon_id=ekstern_versjon_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    ekstern_id: str,
    ekstern_navnerom: str,
    ekstern_versjon_id: str | Unset = UNSET,
) -> GeotekniskUnders | None:
    """Fetches a GeotekniskUnders by external id.

     Fetches a GeotekniskUnders by external id. Returns the most recent one.

    Args:
        ekstern_id (str):
        ekstern_navnerom (str):
        ekstern_versjon_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GeotekniskUnders
    """

    return (
        await asyncio_detailed(
            client=client,
            ekstern_id=ekstern_id,
            ekstern_navnerom=ekstern_navnerom,
            ekstern_versjon_id=ekstern_versjon_id,
        )
    ).parsed
