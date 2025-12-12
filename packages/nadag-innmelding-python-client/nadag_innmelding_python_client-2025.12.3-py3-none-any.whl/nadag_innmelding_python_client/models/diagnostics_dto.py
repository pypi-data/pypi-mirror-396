from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.severity import Severity
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.diagnostic_dto import DiagnosticDto


T = TypeVar("T", bound="DiagnosticsDto")


@_attrs_define
class DiagnosticsDto:
    """A Dto for Diagnostic instances, with a list of DiagnosticDto instances.

    Attributes:
        max_severity (Severity | Unset):
        diagnostics (list[DiagnosticDto] | Unset): The list of diagnostics, with details about each diagnostic.
    """

    max_severity: Severity | Unset = UNSET
    diagnostics: list[DiagnosticDto] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        max_severity: str | Unset = UNSET
        if not isinstance(self.max_severity, Unset):
            max_severity = self.max_severity.value

        diagnostics: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.diagnostics, Unset):
            diagnostics = []
            for diagnostics_item_data in self.diagnostics:
                diagnostics_item = diagnostics_item_data.to_dict()
                diagnostics.append(diagnostics_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if max_severity is not UNSET:
            field_dict["maxSeverity"] = max_severity
        if diagnostics is not UNSET:
            field_dict["diagnostics"] = diagnostics

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.diagnostic_dto import DiagnosticDto

        d = dict(src_dict)
        _max_severity = d.pop("maxSeverity", UNSET)
        max_severity: Severity | Unset
        if isinstance(_max_severity, Unset):
            max_severity = UNSET
        else:
            max_severity = Severity(_max_severity)

        _diagnostics = d.pop("diagnostics", UNSET)
        diagnostics: list[DiagnosticDto] | Unset = UNSET
        if _diagnostics is not UNSET:
            diagnostics = []
            for diagnostics_item_data in _diagnostics:
                diagnostics_item = DiagnosticDto.from_dict(diagnostics_item_data)

                diagnostics.append(diagnostics_item)

        diagnostics_dto = cls(
            max_severity=max_severity,
            diagnostics=diagnostics,
        )

        diagnostics_dto.additional_properties = d
        return diagnostics_dto

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
