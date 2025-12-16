from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define


if TYPE_CHECKING:
    from ..models.create_remote_response_upload_urls import (
        CreateRemoteResponseUploadUrls,
    )


T = TypeVar("T", bound="CreateRemoteResponse")


@_attrs_define
class CreateRemoteResponse:
    """
    Attributes:
        upload_urls (CreateRemoteResponseUploadUrls):
        job_id (str):
    """

    upload_urls: CreateRemoteResponseUploadUrls
    job_id: str

    def to_dict(self) -> dict[str, Any]:
        upload_urls = self.upload_urls.to_dict()

        job_id = self.job_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "upload_urls": upload_urls,
                "job_id": job_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_remote_response_upload_urls import (
            CreateRemoteResponseUploadUrls,
        )

        d = dict(src_dict)
        upload_urls = CreateRemoteResponseUploadUrls.from_dict(d.pop("upload_urls"))

        job_id = d.pop("job_id")

        create_remote_response = cls(
            upload_urls=upload_urls,
            job_id=job_id,
        )

        return create_remote_response
