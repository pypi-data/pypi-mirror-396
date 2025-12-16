from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.create_new_job import CreateNewJob
from ...models.error import Error
from ...models.job import Job


def _get_kwargs(
    organization_slug: str,
    project_name: str,
    *,
    body: CreateNewJob,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/{organization_slug}/{project_name}/job/".format(
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
) -> Any | Error | Job | None:
    if response.status_code == 200:
        response_200 = Job.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

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
) -> Response[Any | Error | Job]:
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
    body: CreateNewJob,
) -> Response[Any | Error | Job]:
    """Entrypoint for run-local

    Args:
        organization_slug (str):
        project_name (str):
        body (CreateNewJob):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | Job]
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
    body: CreateNewJob,
) -> Any | Error | Job | None:
    """Entrypoint for run-local

    Args:
        organization_slug (str):
        project_name (str):
        body (CreateNewJob):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | Job
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
    body: CreateNewJob,
) -> Response[Any | Error | Job]:
    """Entrypoint for run-local

    Args:
        organization_slug (str):
        project_name (str):
        body (CreateNewJob):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | Job]
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
    body: CreateNewJob,
) -> Any | Error | Job | None:
    """Entrypoint for run-local

    Args:
        organization_slug (str):
        project_name (str):
        body (CreateNewJob):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | Job
    """

    return (
        await asyncio_detailed(
            organization_slug=organization_slug,
            project_name=project_name,
            client=client,
            body=body,
        )
    ).parsed
