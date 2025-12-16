from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="CreateRemote")


@_attrs_define
class CreateRemote:
    """
    Attributes:
        params (str):
        jobname (str):
        timeout (int):
    """

    params: str
    jobname: str
    timeout: int

    def to_dict(self) -> dict[str, Any]:
        params = self.params

        jobname = self.jobname

        timeout = self.timeout

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "params": params,
                "jobname": jobname,
                "timeout": timeout,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        params = d.pop("params")

        jobname = d.pop("jobname")

        timeout = d.pop("timeout")

        create_remote = cls(
            params=params,
            jobname=jobname,
            timeout=timeout,
        )

        return create_remote
