from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.create_remote import CreateRemote
from ...models.create_remote_response import CreateRemoteResponse
from ...models.error import Error


def _get_kwargs(
    organization_slug: str,
    project_name: str,
    *,
    body: CreateRemote,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/{organization_slug}/{project_name}/create_remote_job".format(
            organization_slug=organization_slug,
            project_name=project_name,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | CreateRemoteResponse | Error | None:
    if response.status_code == 200:
        response_200 = CreateRemoteResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 402:
        response_402 = Error.from_dict(response.json())

        return response_402

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
) -> Response[Any | CreateRemoteResponse | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_slug: str,
    project_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateRemote,
) -> Response[Any | CreateRemoteResponse | Error]:
    """New starting point for running infrastructure jobs.

     It decides the job ID before upload, allowing for snappier UX.
        It also means we can pass params like the artefacts.yml contents even for remote jobs.

    Args:
        organization_slug (str):
        project_name (str):
        body (CreateRemote):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | CreateRemoteResponse | Error]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_slug: str,
    project_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateRemote,
) -> Any | CreateRemoteResponse | Error | None:
    """New starting point for running infrastructure jobs.

     It decides the job ID before upload, allowing for snappier UX.
        It also means we can pass params like the artefacts.yml contents even for remote jobs.

    Args:
        organization_slug (str):
        project_name (str):
        body (CreateRemote):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | CreateRemoteResponse | Error
    """

    return sync_detailed(
        organization_slug=organization_slug,
        project_name=project_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_slug: str,
    project_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateRemote,
) -> Response[Any | CreateRemoteResponse | Error]:
    """New starting point for running infrastructure jobs.

     It decides the job ID before upload, allowing for snappier UX.
        It also means we can pass params like the artefacts.yml contents even for remote jobs.

    Args:
        organization_slug (str):
        project_name (str):
        body (CreateRemote):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | CreateRemoteResponse | Error]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_slug: str,
    project_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateRemote,
) -> Any | CreateRemoteResponse | Error | None:
    """New starting point for running infrastructure jobs.

     It decides the job ID before upload, allowing for snappier UX.
        It also means we can pass params like the artefacts.yml contents even for remote jobs.

    Args:
        organization_slug (str):
        project_name (str):
        body (CreateRemote):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | CreateRemoteResponse | Error
    """

    return (
        await asyncio_detailed(
            organization_slug=organization_slug,
            project_name=project_name,
            client=client,
            body=body,
        )
    ).parsed
