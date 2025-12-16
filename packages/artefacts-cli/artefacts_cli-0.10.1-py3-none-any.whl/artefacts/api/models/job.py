from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

from typing import cast


T = TypeVar("T", bound="Job")


@_attrs_define
class Job:
    """
    Attributes:
        job_id (str | Unset):
        start (float | Unset):  Example: 1676451245.596.
        start_iso (str | Unset):
        end (float | None | Unset):  Example: 1676451245.596.
        end_iso (None | str | Unset):
        duration (float | None | Unset):
        status (None | str | Unset):
        params (str | Unset):
        job_name (str | Unset):
        project (str | Unset):
        jobname (str | Unset):
        timeout (float | None | Unset):
        message (None | str | Unset):
        commit (None | str | Unset):
        commit_ref (None | str | Unset):
        ref (None | str | Unset):
        creator (str | Unset):
        success (bool | None | Unset):
    """

    job_id: str | Unset = UNSET
    start: float | Unset = UNSET
    start_iso: str | Unset = UNSET
    end: float | None | Unset = UNSET
    end_iso: None | str | Unset = UNSET
    duration: float | None | Unset = UNSET
    status: None | str | Unset = UNSET
    params: str | Unset = UNSET
    job_name: str | Unset = UNSET
    project: str | Unset = UNSET
    jobname: str | Unset = UNSET
    timeout: float | None | Unset = UNSET
    message: None | str | Unset = UNSET
    commit: None | str | Unset = UNSET
    commit_ref: None | str | Unset = UNSET
    ref: None | str | Unset = UNSET
    creator: str | Unset = UNSET
    success: bool | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        start = self.start

        start_iso = self.start_iso

        end: float | None | Unset
        if isinstance(self.end, Unset):
            end = UNSET
        else:
            end = self.end

        end_iso: None | str | Unset
        if isinstance(self.end_iso, Unset):
            end_iso = UNSET
        else:
            end_iso = self.end_iso

        duration: float | None | Unset
        if isinstance(self.duration, Unset):
            duration = UNSET
        else:
            duration = self.duration

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        params = self.params

        job_name = self.job_name

        project = self.project

        jobname = self.jobname

        timeout: float | None | Unset
        if isinstance(self.timeout, Unset):
            timeout = UNSET
        else:
            timeout = self.timeout

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

        commit_ref: None | str | Unset
        if isinstance(self.commit_ref, Unset):
            commit_ref = UNSET
        else:
            commit_ref = self.commit_ref

        ref: None | str | Unset
        if isinstance(self.ref, Unset):
            ref = UNSET
        else:
            ref = self.ref

        creator = self.creator

        success: bool | None | Unset
        if isinstance(self.success, Unset):
            success = UNSET
        else:
            success = self.success

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if job_id is not UNSET:
            field_dict["job_id"] = job_id
        if start is not UNSET:
            field_dict["start"] = start
        if start_iso is not UNSET:
            field_dict["start_iso"] = start_iso
        if end is not UNSET:
            field_dict["end"] = end
        if end_iso is not UNSET:
            field_dict["end_iso"] = end_iso
        if duration is not UNSET:
            field_dict["duration"] = duration
        if status is not UNSET:
            field_dict["status"] = status
        if params is not UNSET:
            field_dict["params"] = params
        if job_name is not UNSET:
            field_dict["job_name"] = job_name
        if project is not UNSET:
            field_dict["project"] = project
        if jobname is not UNSET:
            field_dict["jobname"] = jobname
        if timeout is not UNSET:
            field_dict["timeout"] = timeout
        if message is not UNSET:
            field_dict["message"] = message
        if commit is not UNSET:
            field_dict["commit"] = commit
        if commit_ref is not UNSET:
            field_dict["commit_ref"] = commit_ref
        if ref is not UNSET:
            field_dict["ref"] = ref
        if creator is not UNSET:
            field_dict["creator"] = creator
        if success is not UNSET:
            field_dict["success"] = success

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("job_id", UNSET)

        start = d.pop("start", UNSET)

        start_iso = d.pop("start_iso", UNSET)

        def _parse_end(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        end = _parse_end(d.pop("end", UNSET))

        def _parse_end_iso(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        end_iso = _parse_end_iso(d.pop("end_iso", UNSET))

        def _parse_duration(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        duration = _parse_duration(d.pop("duration", UNSET))

        def _parse_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        params = d.pop("params", UNSET)

        job_name = d.pop("job_name", UNSET)

        project = d.pop("project", UNSET)

        jobname = d.pop("jobname", UNSET)

        def _parse_timeout(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        timeout = _parse_timeout(d.pop("timeout", UNSET))

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

        def _parse_commit_ref(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        commit_ref = _parse_commit_ref(d.pop("commit_ref", UNSET))

        def _parse_ref(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ref = _parse_ref(d.pop("ref", UNSET))

        creator = d.pop("creator", UNSET)

        def _parse_success(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        success = _parse_success(d.pop("success", UNSET))

        job = cls(
            job_id=job_id,
            start=start,
            start_iso=start_iso,
            end=end,
            end_iso=end_iso,
            duration=duration,
            status=status,
            params=params,
            job_name=job_name,
            project=project,
            jobname=jobname,
            timeout=timeout,
            message=message,
            commit=commit,
            commit_ref=commit_ref,
            ref=ref,
            creator=creator,
            success=success,
        )

        return job
