from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define


if TYPE_CHECKING:
    from ..models.upload_source_response_upload_urls import (
        UploadSourceResponseUploadUrls,
    )


T = TypeVar("T", bound="UploadSourceResponse")


@_attrs_define
class UploadSourceResponse:
    """
    Attributes:
        upload_urls (UploadSourceResponseUploadUrls):
    """

    upload_urls: UploadSourceResponseUploadUrls

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
        from ..models.upload_source_response_upload_urls import (
            UploadSourceResponseUploadUrls,
        )

        d = dict(src_dict)
        upload_urls = UploadSourceResponseUploadUrls.from_dict(d.pop("upload_urls"))

        upload_source_response = cls(
            upload_urls=upload_urls,
        )

        return upload_source_response
