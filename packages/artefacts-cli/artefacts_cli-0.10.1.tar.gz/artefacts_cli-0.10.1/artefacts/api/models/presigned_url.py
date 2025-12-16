from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define


if TYPE_CHECKING:
    from ..models.presigned_url_fields import PresignedUrlFields


T = TypeVar("T", bound="PresignedUrl")


@_attrs_define
class PresignedUrl:
    """
    Attributes:
        url (str):
        fields (PresignedUrlFields):
    """

    url: str
    fields: PresignedUrlFields

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        fields = self.fields.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "url": url,
                "fields": fields,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.presigned_url_fields import PresignedUrlFields

        d = dict(src_dict)
        url = d.pop("url")

        fields = PresignedUrlFields.from_dict(d.pop("fields"))

        presigned_url = cls(
            url=url,
            fields=fields,
        )

        return presigned_url
