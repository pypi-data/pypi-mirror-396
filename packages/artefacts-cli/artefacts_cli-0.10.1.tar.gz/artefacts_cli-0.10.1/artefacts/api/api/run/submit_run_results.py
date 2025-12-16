from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.error import Error
from ...models.submit_run_results import SubmitRunResults
from ...models.submit_run_results_response import SubmitRunResultsResponse


def _get_kwargs(
    organization_slug: str,
    project_name: str,
    job_uuid: str,
    run_n: int,
    *,
    body: SubmitRunResults,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/{organization_slug}/{project_name}/job/{job_uuid}/run/{run_n}/".format(
            organization_slug=organization_slug,
            project_name=project_name,
            job_uuid=job_uuid,
            run_n=run_n,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Error | SubmitRunResultsResponse | None:
    if response.status_code == 200:
        response_200 = SubmitRunResultsResponse.from_dict(response.json())

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
) -> Response[Any | Error | SubmitRunResultsResponse]:
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
    run_n: int,
    *,
    client: AuthenticatedClient | Client,
    body: SubmitRunResults,
) -> Response[Any | Error | SubmitRunResultsResponse]:
    """Submits results for a run

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        run_n (int):
        body (SubmitRunResults):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | SubmitRunResultsResponse]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        job_uuid=job_uuid,
        run_n=run_n,
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
    run_n: int,
    *,
    client: AuthenticatedClient | Client,
    body: SubmitRunResults,
) -> Any | Error | SubmitRunResultsResponse | None:
    """Submits results for a run

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        run_n (int):
        body (SubmitRunResults):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | SubmitRunResultsResponse
    """

    return sync_detailed(
        organization_slug=organization_slug,
        project_name=project_name,
        job_uuid=job_uuid,
        run_n=run_n,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_slug: str,
    project_name: str,
    job_uuid: str,
    run_n: int,
    *,
    client: AuthenticatedClient | Client,
    body: SubmitRunResults,
) -> Response[Any | Error | SubmitRunResultsResponse]:
    """Submits results for a run

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        run_n (int):
        body (SubmitRunResults):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | SubmitRunResultsResponse]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        job_uuid=job_uuid,
        run_n=run_n,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_slug: str,
    project_name: str,
    job_uuid: str,
    run_n: int,
    *,
    client: AuthenticatedClient | Client,
    body: SubmitRunResults,
) -> Any | Error | SubmitRunResultsResponse | None:
    """Submits results for a run

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        run_n (int):
        body (SubmitRunResults):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | SubmitRunResultsResponse
    """

    return (
        await asyncio_detailed(
            organization_slug=organization_slug,
            project_name=project_name,
            job_uuid=job_uuid,
            run_n=run_n,
            client=client,
            body=body,
        )
    ).parsed
