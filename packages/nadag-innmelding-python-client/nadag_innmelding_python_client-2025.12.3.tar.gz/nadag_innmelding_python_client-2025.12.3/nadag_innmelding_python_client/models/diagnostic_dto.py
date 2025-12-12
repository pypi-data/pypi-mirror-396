from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.severity import Severity
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.diagnostic_dto_root_owner import DiagnosticDtoRootOwner
    from ..models.diagnostic_dto_target import DiagnosticDtoTarget


T = TypeVar("T", bound="DiagnosticDto")


@_attrs_define
class DiagnosticDto:
    """Result from checking a single validation rule.

    Attributes:
        validation_id (UUID | Unset): Identifier for the validation
        target (DiagnosticDtoTarget | Unset): Reference (identifier) for the target domain model object
        property_ (str | Unset): The property of the target domain model object that was checked
        severity (Severity | Unset):
        description (str | Unset): The human-readable description of the diagnostic
        root_owner (DiagnosticDtoRootOwner | Unset): Reference (identifier) for the root owner of the target
        timestamp (datetime.datetime | Unset): The timestamp of the validation
    """

    validation_id: UUID | Unset = UNSET
    target: DiagnosticDtoTarget | Unset = UNSET
    property_: str | Unset = UNSET
    severity: Severity | Unset = UNSET
    description: str | Unset = UNSET
    root_owner: DiagnosticDtoRootOwner | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        validation_id: str | Unset = UNSET
        if not isinstance(self.validation_id, Unset):
            validation_id = str(self.validation_id)

        target: dict[str, Any] | Unset = UNSET
        if not isinstance(self.target, Unset):
            target = self.target.to_dict()

        property_ = self.property_

        severity: str | Unset = UNSET
        if not isinstance(self.severity, Unset):
            severity = self.severity.value

        description = self.description

        root_owner: dict[str, Any] | Unset = UNSET
        if not isinstance(self.root_owner, Unset):
            root_owner = self.root_owner.to_dict()

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if validation_id is not UNSET:
            field_dict["validationId"] = validation_id
        if target is not UNSET:
            field_dict["target"] = target
        if property_ is not UNSET:
            field_dict["property"] = property_
        if severity is not UNSET:
            field_dict["severity"] = severity
        if description is not UNSET:
            field_dict["description"] = description
        if root_owner is not UNSET:
            field_dict["rootOwner"] = root_owner
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.diagnostic_dto_root_owner import DiagnosticDtoRootOwner
        from ..models.diagnostic_dto_target import DiagnosticDtoTarget

        d = dict(src_dict)
        _validation_id = d.pop("validationId", UNSET)
        validation_id: UUID | Unset
        if isinstance(_validation_id, Unset):
            validation_id = UNSET
        else:
            validation_id = UUID(_validation_id)

        _target = d.pop("target", UNSET)
        target: DiagnosticDtoTarget | Unset
        if isinstance(_target, Unset):
            target = UNSET
        else:
            target = DiagnosticDtoTarget.from_dict(_target)

        property_ = d.pop("property", UNSET)

        _severity = d.pop("severity", UNSET)
        severity: Severity | Unset
        if isinstance(_severity, Unset):
            severity = UNSET
        else:
            severity = Severity(_severity)

        description = d.pop("description", UNSET)

        _root_owner = d.pop("rootOwner", UNSET)
        root_owner: DiagnosticDtoRootOwner | Unset
        if isinstance(_root_owner, Unset):
            root_owner = UNSET
        else:
            root_owner = DiagnosticDtoRootOwner.from_dict(_root_owner)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = isoparse(_timestamp)

        diagnostic_dto = cls(
            validation_id=validation_id,
            target=target,
            property_=property_,
            severity=severity,
            description=description,
            root_owner=root_owner,
            timestamp=timestamp,
        )

        diagnostic_dto.additional_properties = d
        return diagnostic_dto

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
