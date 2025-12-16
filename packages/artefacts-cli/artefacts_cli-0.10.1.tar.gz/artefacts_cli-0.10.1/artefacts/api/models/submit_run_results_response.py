from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define


if TYPE_CHECKING:
    from ..models.submit_run_results_response_upload_urls import (
        SubmitRunResultsResponseUploadUrls,
    )


T = TypeVar("T", bound="SubmitRunResultsResponse")


@_attrs_define
class SubmitRunResultsResponse:
    """
    Attributes:
        upload_urls (SubmitRunResultsResponseUploadUrls):
    """

    upload_urls: SubmitRunResultsResponseUploadUrls

    def to_dict(self) -> dict[str, Any]:
        upload_urls = self.upload_urls.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "upload_urls": upload_urls,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.submit_run_results_response_upload_urls import (
            SubmitRunResultsResponseUploadUrls,
        )

        d = dict(src_dict)
        upload_urls = SubmitRunResultsResponseUploadUrls.from_dict(d.pop("upload_urls"))

        submit_run_results_response = cls(
            upload_urls=upload_urls,
        )

        return submit_run_results_response
