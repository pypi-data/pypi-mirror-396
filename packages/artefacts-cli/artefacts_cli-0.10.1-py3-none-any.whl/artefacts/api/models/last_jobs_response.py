from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define


if TYPE_CHECKING:
    from ..models.job import Job


T = TypeVar("T", bound="LastJobsResponse")


@_attrs_define
class LastJobsResponse:
    """
    Attributes:
        jobs (list[Job]):
    """

    jobs: list[Job]

    def to_dict(self) -> dict[str, Any]:
        jobs = []
        for jobs_item_data in self.jobs:
            jobs_item = jobs_item_data.to_dict()
            jobs.append(jobs_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "jobs": jobs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job import Job

        d = dict(src_dict)
        jobs = []
        _jobs = d.pop("jobs")
        for jobs_item_data in _jobs:
            jobs_item = Job.from_dict(jobs_item_data)

            jobs.append(jobs_item)

        last_jobs_response = cls(
            jobs=jobs,
        )

        return last_jobs_response
