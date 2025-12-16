from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define


from typing import cast


T = TypeVar("T", bound="ArtifactResponse")


@_attrs_define
class ArtifactResponse:
    """
    Attributes:
        filename (str):
        size (int):
        download_url (None | str):
    """

    filename: str
    size: int
    download_url: None | str

    def to_dict(self) -> dict[str, Any]:
        filename = self.filename

        size = self.size

        download_url: None | str
        download_url = self.download_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "filename": filename,
                "size": size,
                "download_url": download_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        filename = d.pop("filename")

        size = d.pop("size")

        def _parse_download_url(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        download_url = _parse_download_url(d.pop("download_url"))

        artifact_response = cls(
            filename=filename,
            size=size,
            download_url=download_url,
        )

        return artifact_response
