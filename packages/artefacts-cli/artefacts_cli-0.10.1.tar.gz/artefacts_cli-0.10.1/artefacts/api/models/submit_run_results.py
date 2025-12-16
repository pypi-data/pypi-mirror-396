from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
    from ..models.submit_run_results_metrics import SubmitRunResultsMetrics
    from ..models.submit_run_results_tests_item import SubmitRunResultsTestsItem
    from ..models.submit_run_results_uploads import SubmitRunResultsUploads


T = TypeVar("T", bound="SubmitRunResults")


@_attrs_define
class SubmitRunResults:
    """
    Attributes:
        job_id (str):
        run_n (int):
        start (float):
        params (str):
        end (float):
        duration (float):
        success (bool):
        uploads (SubmitRunResultsUploads):
        tests (list[SubmitRunResultsTestsItem]):
        metrics (SubmitRunResultsMetrics):
        scenario_name (None | str | Unset):
    """

    job_id: str
    run_n: int
    start: float
    params: str
    end: float
    duration: float
    success: bool
    uploads: SubmitRunResultsUploads
    tests: list[SubmitRunResultsTestsItem]
    metrics: SubmitRunResultsMetrics
    scenario_name: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        run_n = self.run_n

        start = self.start

        params = self.params

        end = self.end

        duration = self.duration

        success = self.success

        uploads = self.uploads.to_dict()

        tests = []
        for tests_item_data in self.tests:
            tests_item = tests_item_data.to_dict()
            tests.append(tests_item)

        metrics = self.metrics.to_dict()

        scenario_name: None | str | Unset
        if isinstance(self.scenario_name, Unset):
            scenario_name = UNSET
        else:
            scenario_name = self.scenario_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "job_id": job_id,
                "run_n": run_n,
                "start": start,
                "params": params,
                "end": end,
                "duration": duration,
                "success": success,
                "uploads": uploads,
                "tests": tests,
                "metrics": metrics,
            }
        )
        if scenario_name is not UNSET:
            field_dict["scenario_name"] = scenario_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.submit_run_results_metrics import SubmitRunResultsMetrics
        from ..models.submit_run_results_tests_item import SubmitRunResultsTestsItem
        from ..models.submit_run_results_uploads import SubmitRunResultsUploads

        d = dict(src_dict)
        job_id = d.pop("job_id")

        run_n = d.pop("run_n")

        start = d.pop("start")

        params = d.pop("params")

        end = d.pop("end")

        duration = d.pop("duration")

        success = d.pop("success")

        uploads = SubmitRunResultsUploads.from_dict(d.pop("uploads"))

        tests = []
        _tests = d.pop("tests")
        for tests_item_data in _tests:
            tests_item = SubmitRunResultsTestsItem.from_dict(tests_item_data)

            tests.append(tests_item)

        metrics = SubmitRunResultsMetrics.from_dict(d.pop("metrics"))

        def _parse_scenario_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        scenario_name = _parse_scenario_name(d.pop("scenario_name", UNSET))

        submit_run_results = cls(
            job_id=job_id,
            run_n=run_n,
            start=start,
            params=params,
            end=end,
            duration=duration,
            success=success,
            uploads=uploads,
            tests=tests,
            metrics=metrics,
            scenario_name=scenario_name,
        )

        return submit_run_results
