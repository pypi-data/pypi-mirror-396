from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define


if TYPE_CHECKING:
    from ..models.scenario_map_response import ScenarioMapResponse


T = TypeVar("T", bound="GetArtifactDownloadsResponse")


@_attrs_define
class GetArtifactDownloadsResponse:
    """
    Attributes:
        runs (list[ScenarioMapResponse]):
        total_files_count (int):
        total_size_bytes (int):
    """

    runs: list[ScenarioMapResponse]
    total_files_count: int
    total_size_bytes: int

    def to_dict(self) -> dict[str, Any]:
        runs = []
        for runs_item_data in self.runs:
            runs_item = runs_item_data.to_dict()
            runs.append(runs_item)

        total_files_count = self.total_files_count

        total_size_bytes = self.total_size_bytes

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "runs": runs,
                "total_files_count": total_files_count,
                "total_size_bytes": total_size_bytes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scenario_map_response import ScenarioMapResponse

        d = dict(src_dict)
        runs = []
        _runs = d.pop("runs")
        for runs_item_data in _runs:
            runs_item = ScenarioMapResponse.from_dict(runs_item_data)

            runs.append(runs_item)

        total_files_count = d.pop("total_files_count")

        total_size_bytes = d.pop("total_size_bytes")

        get_artifact_downloads_response = cls(
            runs=runs,
            total_files_count=total_files_count,
            total_size_bytes=total_size_bytes,
        )

        return get_artifact_downloads_response
