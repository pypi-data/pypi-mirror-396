from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.error import Error


def _get_kwargs(
    artifact_uuid: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/artifact/{artifact_uuid}/".format(
            artifact_uuid=artifact_uuid,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Error | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    artifact_uuid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | Error]:
    """Redirects to the signed S3 URL for a given artifact UUID.

    Args:
        artifact_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        artifact_uuid=artifact_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    artifact_uuid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | Error | None:
    """Redirects to the signed S3 URL for a given artifact UUID.

    Args:
        artifact_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return sync_detailed(
        artifact_uuid=artifact_uuid,
        client=client,
    ).parsed


async def asyncio_detailed(
    artifact_uuid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | Error]:
    """Redirects to the signed S3 URL for a given artifact UUID.

    Args:
        artifact_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        artifact_uuid=artifact_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    artifact_uuid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | Error | None:
    """Redirects to the signed S3 URL for a given artifact UUID.

    Args:
        artifact_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return (
        await asyncio_detailed(
            artifact_uuid=artifact_uuid,
            client=client,
        )
    ).parsed
