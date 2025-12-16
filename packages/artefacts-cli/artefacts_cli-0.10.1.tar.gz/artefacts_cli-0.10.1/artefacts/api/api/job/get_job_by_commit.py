from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.job import Job


def _get_kwargs(
    organization_slug: str,
    project_name: str,
    *,
    commit_id: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["commit_id"] = commit_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization_slug}/{project_name}/job/".format(
            organization_slug=organization_slug,
            project_name=project_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Error | Job | None:
    if response.status_code == 200:
        response_200 = Job.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
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
    commit_id: str,
) -> Response[Any | Error | Job]:
    """Get job details for a specific commit

    Args:
        organization_slug (str):
        project_name (str):
        commit_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | Job]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        commit_id=commit_id,
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
    commit_id: str,
) -> Any | Error | Job | None:
    """Get job details for a specific commit

    Args:
        organization_slug (str):
        project_name (str):
        commit_id (str):

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
        commit_id=commit_id,
    ).parsed


async def asyncio_detailed(
    organization_slug: str,
    project_name: str,
    *,
    client: AuthenticatedClient | Client,
    commit_id: str,
) -> Response[Any | Error | Job]:
    """Get job details for a specific commit

    Args:
        organization_slug (str):
        project_name (str):
        commit_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | Job]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        commit_id=commit_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_slug: str,
    project_name: str,
    *,
    client: AuthenticatedClient | Client,
    commit_id: str,
) -> Any | Error | Job | None:
    """Get job details for a specific commit

    Args:
        organization_slug (str):
        project_name (str):
        commit_id (str):

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
            commit_id=commit_id,
        )
    ).parsed
