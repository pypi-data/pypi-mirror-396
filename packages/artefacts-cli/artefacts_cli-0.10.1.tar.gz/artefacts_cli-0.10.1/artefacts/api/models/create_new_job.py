from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

from typing import cast


T = TypeVar("T", bound="CreateNewJob")


@_attrs_define
class CreateNewJob:
    """
    Attributes:
        start (float):
        status (str):
        params (str):
        jobname (str):
        timeout (int):
        n_subjobs (int | Unset):
        message (None | str | Unset):
        commit (None | str | Unset):
        ref (None | str | Unset):
        project (None | str | Unset):
        project_id (None | str | Unset):
    """

    start: float
    status: str
    params: str
    jobname: str
    timeout: int
    n_subjobs: int | Unset = UNSET
    message: None | str | Unset = UNSET
    commit: None | str | Unset = UNSET
    ref: None | str | Unset = UNSET
    project: None | str | Unset = UNSET
    project_id: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        start = self.start

        status = self.status

        params = self.params

        jobname = self.jobname

        timeout = self.timeout

        n_subjobs = self.n_subjobs

        message: None | str | Unset
        if isinstance(self.message, Unset):
            message = UNSET
        else:
            message = self.message

        commit: None | str | Unset
        if isinstance(self.commit, Unset):
            commit = UNSET
        else:
            commit = self.commit

        ref: None | str | Unset
        if isinstance(self.ref, Unset):
            ref = UNSET
        else:
            ref = self.ref

        project: None | str | Unset
        if isinstance(self.project, Unset):
            project = UNSET
        else:
            project = self.project

        project_id: None | str | Unset
        if isinstance(self.project_id, Unset):
            project_id = UNSET
        else:
            project_id = self.project_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "start": start,
                "status": status,
                "params": params,
                "jobname": jobname,
                "timeout": timeout,
            }
        )
        if n_subjobs is not UNSET:
            field_dict["n_subjobs"] = n_subjobs
        if message is not UNSET:
            field_dict["message"] = message
        if commit is not UNSET:
            field_dict["commit"] = commit
        if ref is not UNSET:
            field_dict["ref"] = ref
        if project is not UNSET:
            field_dict["project"] = project
        if project_id is not UNSET:
            field_dict["project_id"] = project_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start = d.pop("start")

        status = d.pop("status")

        params = d.pop("params")

        jobname = d.pop("jobname")

        timeout = d.pop("timeout")

        n_subjobs = d.pop("n_subjobs", UNSET)

        def _parse_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        message = _parse_message(d.pop("message", UNSET))

        def _parse_commit(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        commit = _parse_commit(d.pop("commit", UNSET))

        def _parse_ref(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ref = _parse_ref(d.pop("ref", UNSET))

        def _parse_project(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        project = _parse_project(d.pop("project", UNSET))

        def _parse_project_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        project_id = _parse_project_id(d.pop("project_id", UNSET))

        create_new_job = cls(
            start=start,
            status=status,
            params=params,
            jobname=jobname,
            timeout=timeout,
            n_subjobs=n_subjobs,
            message=message,
            commit=commit,
            ref=ref,
            project=project,
            project_id=project_id,
        )

        return create_new_job
