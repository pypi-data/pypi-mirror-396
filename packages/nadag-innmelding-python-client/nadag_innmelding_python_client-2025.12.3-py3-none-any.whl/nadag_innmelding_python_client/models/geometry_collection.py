from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.geometry import Geometry


T = TypeVar("T", bound="GeometryCollection")


@_attrs_define
class GeometryCollection:
    """
    Attributes:
        type_ (Literal['GeometryCollection'] | Unset):
        geometries (list[Geometry] | Unset):
    """

    type_: Literal["GeometryCollection"] | Unset = UNSET
    geometries: list[Geometry] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        geometries: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.geometries, Unset):
            geometries = []
            for geometries_item_data in self.geometries:
                geometries_item = geometries_item_data.to_dict()
                geometries.append(geometries_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if geometries is not UNSET:
            field_dict["geometries"] = geometries

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.geometry import Geometry

        d = dict(src_dict)
        type_ = cast(Literal["GeometryCollection"] | Unset, d.pop("type", UNSET))
        if type_ != "GeometryCollection" and not isinstance(type_, Unset):
            raise ValueError(f"type must match const 'GeometryCollection', got '{type_}'")

        _geometries = d.pop("geometries", UNSET)
        geometries: list[Geometry] | Unset = UNSET
        if _geometries is not UNSET:
            geometries = []
            for geometries_item_data in _geometries:
                geometries_item = Geometry.from_dict(geometries_item_data)

                geometries.append(geometries_item)

        geometry_collection = cls(
            type_=type_,
            geometries=geometries,
        )

        geometry_collection.additional_properties = d
        return geometry_collection

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
