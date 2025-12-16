from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.get_artifact_downloads_response import GetArtifactDownloadsResponse
from ...types import Unset


def _get_kwargs(
    organization_slug: str,
    project_name: str,
    job_uuid: str,
    *,
    scenario_id: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["scenario_id"] = scenario_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization_slug}/{project_name}/job/{job_uuid}/artifact-downloads".format(
            organization_slug=organization_slug,
            project_name=project_name,
            job_uuid=job_uuid,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Error | GetArtifactDownloadsResponse | None:
    if response.status_code == 200:
        response_200 = GetArtifactDownloadsResponse.from_dict(response.json())

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
) -> Response[Any | Error | GetArtifactDownloadsResponse]:
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
    scenario_id: str | Unset = UNSET,
) -> Response[Any | Error | GetArtifactDownloadsResponse]:
    """Get all artifacts for a job with signed download URLs, grouped by run.

     Optional query parameter:
        - scenario_id: Filter artifacts for a specific scenario (format: run_n_scenario_name)

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        scenario_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | GetArtifactDownloadsResponse]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        job_uuid=job_uuid,
        scenario_id=scenario_id,
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
    scenario_id: str | Unset = UNSET,
) -> Any | Error | GetArtifactDownloadsResponse | None:
    """Get all artifacts for a job with signed download URLs, grouped by run.

     Optional query parameter:
        - scenario_id: Filter artifacts for a specific scenario (format: run_n_scenario_name)

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        scenario_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | GetArtifactDownloadsResponse
    """

    return sync_detailed(
        organization_slug=organization_slug,
        project_name=project_name,
        job_uuid=job_uuid,
        client=client,
        scenario_id=scenario_id,
    ).parsed


async def asyncio_detailed(
    organization_slug: str,
    project_name: str,
    job_uuid: str,
    *,
    client: AuthenticatedClient | Client,
    scenario_id: str | Unset = UNSET,
) -> Response[Any | Error | GetArtifactDownloadsResponse]:
    """Get all artifacts for a job with signed download URLs, grouped by run.

     Optional query parameter:
        - scenario_id: Filter artifacts for a specific scenario (format: run_n_scenario_name)

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        scenario_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | GetArtifactDownloadsResponse]
    """

    kwargs = _get_kwargs(
        organization_slug=organization_slug,
        project_name=project_name,
        job_uuid=job_uuid,
        scenario_id=scenario_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_slug: str,
    project_name: str,
    job_uuid: str,
    *,
    client: AuthenticatedClient | Client,
    scenario_id: str | Unset = UNSET,
) -> Any | Error | GetArtifactDownloadsResponse | None:
    """Get all artifacts for a job with signed download URLs, grouped by run.

     Optional query parameter:
        - scenario_id: Filter artifacts for a specific scenario (format: run_n_scenario_name)

    Args:
        organization_slug (str):
        project_name (str):
        job_uuid (str):
        scenario_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | GetArtifactDownloadsResponse
    """

    return (
        await asyncio_detailed(
            organization_slug=organization_slug,
            project_name=project_name,
            job_uuid=job_uuid,
            client=client,
            scenario_id=scenario_id,
        )
    ).parsed
