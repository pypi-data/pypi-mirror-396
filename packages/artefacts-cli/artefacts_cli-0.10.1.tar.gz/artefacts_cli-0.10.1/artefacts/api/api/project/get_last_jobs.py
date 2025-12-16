from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.last_jobs_response import LastJobsResponse
from ...types import Unset


def _get_kwargs(
    organization_slug: str,
    project_name: str,
    *,
    branch: str | Unset = UNSET,
    job_name: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["branch"] = branch

    params["job_name"] = job_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization_slug}/{project_name}/recent-jobs".format(
            organization_slug=organization_slug,
            project_name=project_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Error | LastJobsResponse | None:
    if response.status_code == 200:
        response_200 = LastJobsResponse.from_dict(response.json())

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
) -> Response[Any | Error | LastJobsResponse]:
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
    branch: str | Unset = UNSET,
    job_name: str | Unset = UNSET,
) -> Response[Any | Error | LastJobsResponse]:
    """Get the last 20 jobs for the project with their status and metadata.

     Optionally filter by branch name from commit_ref and/or job name.

        Query params:
        - branch: filter by git branch name in commit_ref or machine name (e.g., 'main', 'feature-auth')
        - job_name: filter by specific job name (e.g., 'test_odometry', 'build')

    Args:
        organization_slug (str):
        project_name (str):
        branch (str | Unset):
        job_name (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | LastJobsResponse]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        branch=branch,
        job_name=job_name,
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
    branch: str | Unset = UNSET,
    job_name: str | Unset = UNSET,
) -> Any | Error | LastJobsResponse | None:
    """Get the last 20 jobs for the project with their status and metadata.

     Optionally filter by branch name from commit_ref and/or job name.

        Query params:
        - branch: filter by git branch name in commit_ref or machine name (e.g., 'main', 'feature-auth')
        - job_name: filter by specific job name (e.g., 'test_odometry', 'build')

    Args:
        organization_slug (str):
        project_name (str):
        branch (str | Unset):
        job_name (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | LastJobsResponse
    """

    return sync_detailed(
        organization_slug=organization_slug,
        project_name=project_name,
        client=client,
        branch=branch,
        job_name=job_name,
    ).parsed


async def asyncio_detailed(
    organization_slug: str,
    project_name: str,
    *,
    client: AuthenticatedClient | Client,
    branch: str | Unset = UNSET,
    job_name: str | Unset = UNSET,
) -> Response[Any | Error | LastJobsResponse]:
    """Get the last 20 jobs for the project with their status and metadata.

     Optionally filter by branch name from commit_ref and/or job name.

        Query params:
        - branch: filter by git branch name in commit_ref or machine name (e.g., 'main', 'feature-auth')
        - job_name: filter by specific job name (e.g., 'test_odometry', 'build')

    Args:
        organization_slug (str):
        project_name (str):
        branch (str | Unset):
        job_name (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | LastJobsResponse]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        branch=branch,
        job_name=job_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_slug: str,
    project_name: str,
    *,
    client: AuthenticatedClient | Client,
    branch: str | Unset = UNSET,
    job_name: str | Unset = UNSET,
) -> Any | Error | LastJobsResponse | None:
    """Get the last 20 jobs for the project with their status and metadata.

     Optionally filter by branch name from commit_ref and/or job name.

        Query params:
        - branch: filter by git branch name in commit_ref or machine name (e.g., 'main', 'feature-auth')
        - job_name: filter by specific job name (e.g., 'test_odometry', 'build')

    Args:
        organization_slug (str):
        project_name (str):
        branch (str | Unset):
        job_name (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | LastJobsResponse
    """

    return (
        await asyncio_detailed(
            organization_slug=organization_slug,
            project_name=project_name,
            client=client,
            branch=branch,
            job_name=job_name,
        )
    ).parsed
