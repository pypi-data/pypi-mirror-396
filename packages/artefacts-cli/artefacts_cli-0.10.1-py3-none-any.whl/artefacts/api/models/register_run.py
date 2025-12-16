from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define

from ..types import UNSET, Unset


if TYPE_CHECKING:
    from ..models.register_run_tests_item import RegisterRunTestsItem


T = TypeVar("T", bound="RegisterRun")


@_attrs_define
class RegisterRun:
    """
    Attributes:
        job_id (str):
        run_n (int):
        start (float):
        tests (list[RegisterRunTestsItem]):
        params (str):
        scenario_name (str | Unset):
    """

    job_id: str
    run_n: int
    start: float
    tests: list[RegisterRunTestsItem]
    params: str
    scenario_name: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        run_n = self.run_n

        start = self.start

        tests = []
        for tests_item_data in self.tests:
            tests_item = tests_item_data.to_dict()
            tests.append(tests_item)

        params = self.params

        scenario_name = self.scenario_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "job_id": job_id,
                "run_n": run_n,
                "start": start,
                "tests": tests,
                "params": params,
            }
        )
        if scenario_name is not UNSET:
            field_dict["scenario_name"] = scenario_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.register_run_tests_item import RegisterRunTestsItem

        d = dict(src_dict)
        job_id = d.pop("job_id")

        run_n = d.pop("run_n")

        start = d.pop("start")

        tests = []
        _tests = d.pop("tests")
        for tests_item_data in _tests:
            tests_item = RegisterRunTestsItem.from_dict(tests_item_data)

            tests.append(tests_item)

        params = d.pop("params")

        scenario_name = d.pop("scenario_name", UNSET)

        register_run = cls(
            job_id=job_id,
            run_n=run_n,
            start=start,
            tests=tests,
            params=params,
            scenario_name=scenario_name,
        )

        return register_run
