from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.geoteknisk_borehull import GeotekniskBorehull
from ...types import UNSET, Response, Unset


def _get_kwargs(
    geoteknisk_borehull_id: str,
    *,
    include_metode: bool | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["includeMetode"] = include_metode

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/nadag/innmelding/v1/GeotekniskBorehull/{geoteknisk_borehull_id}".format(
            geoteknisk_borehull_id=quote(str(geoteknisk_borehull_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GeotekniskBorehull | None:
    if response.status_code == 200:
        response_200 = GeotekniskBorehull.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | GeotekniskBorehull]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    geoteknisk_borehull_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_metode: bool | Unset = UNSET,
) -> Response[Any | GeotekniskBorehull]:
    """Fetches a GeotekniskBorehull by id.

     Fetches a GeotekniskBorehull by id.

    Args:
        geoteknisk_borehull_id (str):
        include_metode (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | GeotekniskBorehull]
    """

    kwargs = _get_kwargs(
        geoteknisk_borehull_id=geoteknisk_borehull_id,
        include_metode=include_metode,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    geoteknisk_borehull_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_metode: bool | Unset = UNSET,
) -> Any | GeotekniskBorehull | None:
    """Fetches a GeotekniskBorehull by id.

     Fetches a GeotekniskBorehull by id.

    Args:
        geoteknisk_borehull_id (str):
        include_metode (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | GeotekniskBorehull
    """

    return sync_detailed(
        geoteknisk_borehull_id=geoteknisk_borehull_id,
        client=client,
        include_metode=include_metode,
    ).parsed


async def asyncio_detailed(
    geoteknisk_borehull_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_metode: bool | Unset = UNSET,
) -> Response[Any | GeotekniskBorehull]:
    """Fetches a GeotekniskBorehull by id.

     Fetches a GeotekniskBorehull by id.

    Args:
        geoteknisk_borehull_id (str):
        include_metode (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | GeotekniskBorehull]
    """

    kwargs = _get_kwargs(
        geoteknisk_borehull_id=geoteknisk_borehull_id,
        include_metode=include_metode,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    geoteknisk_borehull_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_metode: bool | Unset = UNSET,
) -> Any | GeotekniskBorehull | None:
    """Fetches a GeotekniskBorehull by id.

     Fetches a GeotekniskBorehull by id.

    Args:
        geoteknisk_borehull_id (str):
        include_metode (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | GeotekniskBorehull
    """

    return (
        await asyncio_detailed(
            geoteknisk_borehull_id=geoteknisk_borehull_id,
            client=client,
            include_metode=include_metode,
        )
    ).parsed
