from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

from typing import cast


T = TypeVar("T", bound="UpdateJobResults")


@_attrs_define
class UpdateJobResults:
    """
    Attributes:
        status (str):
        duration (float | Unset):
        end (float | Unset): Ignored
        success (bool | Unset):
        project_id (None | str | Unset):
    """

    status: str
    duration: float | Unset = UNSET
    end: float | Unset = UNSET
    success: bool | Unset = UNSET
    project_id: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        duration = self.duration

        end = self.end

        success = self.success

        project_id: None | str | Unset
        if isinstance(self.project_id, Unset):
            project_id = UNSET
        else:
            project_id = self.project_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "status": status,
            }
        )
        if duration is not UNSET:
            field_dict["duration"] = duration
        if end is not UNSET:
            field_dict["end"] = end
        if success is not UNSET:
            field_dict["success"] = success
        if project_id is not UNSET:
            field_dict["project_id"] = project_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status")

        duration = d.pop("duration", UNSET)

        end = d.pop("end", UNSET)

        success = d.pop("success", UNSET)

        def _parse_project_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        project_id = _parse_project_id(d.pop("project_id", UNSET))

        update_job_results = cls(
            status=status,
            duration=duration,
            end=end,
            success=success,
            project_id=project_id,
        )

        return update_job_results
