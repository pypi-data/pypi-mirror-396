from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define


if TYPE_CHECKING:
    from ..models.artifact_response import ArtifactResponse


T = TypeVar("T", bound="ScenarioMapResponse")


@_attrs_define
class ScenarioMapResponse:
    """
    Attributes:
        scenario_id (str):
        name (str):
        run_n (int):
        artifacts (list[ArtifactResponse]):
    """

    scenario_id: str
    name: str
    run_n: int
    artifacts: list[ArtifactResponse]

    def to_dict(self) -> dict[str, Any]:
        scenario_id = self.scenario_id

        name = self.name

        run_n = self.run_n

        artifacts = []
        for artifacts_item_data in self.artifacts:
            artifacts_item = artifacts_item_data.to_dict()
            artifacts.append(artifacts_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scenario_id": scenario_id,
                "name": name,
                "run_n": run_n,
                "artifacts": artifacts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.artifact_response import ArtifactResponse

        d = dict(src_dict)
        scenario_id = d.pop("scenario_id")

        name = d.pop("name")

        run_n = d.pop("run_n")

        artifacts = []
        _artifacts = d.pop("artifacts")
        for artifacts_item_data in _artifacts:
            artifacts_item = ArtifactResponse.from_dict(artifacts_item_data)

            artifacts.append(artifacts_item)

        scenario_map_response = cls(
            scenario_id=scenario_id,
            name=name,
            run_n=run_n,
            artifacts=artifacts,
        )

        return scenario_map_response
