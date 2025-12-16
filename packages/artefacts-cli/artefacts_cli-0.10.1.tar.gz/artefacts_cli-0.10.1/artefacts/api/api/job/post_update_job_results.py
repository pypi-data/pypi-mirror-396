from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.error import Error
from ...models.update_job_results import UpdateJobResults


def _get_kwargs(
    organization_slug: str,
    project_name: str,
    job_uuid: str,
    *,
    body: UpdateJobResults,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/{organization_slug}/{project_name}/job/{job_uuid}/".format(
            organization_slug=organization_slug,
            project_name=project_name,
            job_uuid=job_uuid,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Error | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
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
) -> Response[Any | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_slug: str,
    project_name: str,
    job_uuid: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateJobResults,
) -> Response[Any | Error]:
    """Updates job status, with some values(such as billed duration) being cumulative

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        body (UpdateJobResults):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        job_uuid=job_uuid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_slug: str,
    project_name: str,
    job_uuid: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateJobResults,
) -> Any | Error | None:
    """Updates job status, with some values(such as billed duration) being cumulative

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        body (UpdateJobResults):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return sync_detailed(
        organization_slug=organization_slug,
        project_name=project_name,
        job_uuid=job_uuid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_slug: str,
    project_name: str,
    job_uuid: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateJobResults,
) -> Response[Any | Error]:
    """Updates job status, with some values(such as billed duration) being cumulative

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        body (UpdateJobResults):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        job_uuid=job_uuid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_slug: str,
    project_name: str,
    job_uuid: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateJobResults,
) -> Any | Error | None:
    """Updates job status, with some values(such as billed duration) being cumulative

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        body (UpdateJobResults):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return (
        await asyncio_detailed(
            organization_slug=organization_slug,
            project_name=project_name,
            job_uuid=job_uuid,
            client=client,
            body=body,
        )
    ).parsed
