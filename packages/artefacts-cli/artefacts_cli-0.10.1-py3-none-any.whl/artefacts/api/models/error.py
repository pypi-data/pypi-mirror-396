from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define

from ..types import UNSET, Unset


if TYPE_CHECKING:
    from ..models.error_errors import ErrorErrors


T = TypeVar("T", bound="Error")


@_attrs_define
class Error:
    """
    Attributes:
        error (str | Unset):
        errors (ErrorErrors | Unset):
    """

    error: str | Unset = UNSET
    errors: ErrorErrors | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        error = self.error

        errors: dict[str, Any] | Unset = UNSET
        if not isinstance(self.errors, Unset):
            errors = self.errors.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if error is not UNSET:
            field_dict["error"] = error
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_errors import ErrorErrors

        d = dict(src_dict)
        error = d.pop("error", UNSET)

        _errors = d.pop("errors", UNSET)
        errors: ErrorErrors | Unset
        if isinstance(_errors, Unset):
            errors = UNSET
        else:
            errors = ErrorErrors.from_dict(_errors)

        error = cls(
            error=error,
            errors=errors,
        )

        return error
