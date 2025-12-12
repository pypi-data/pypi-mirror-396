from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PlatebelastningData")


@_attrs_define
class PlatebelastningData:
    """data fra måling av in situ deformasjons- og konsolideringsegenskaper i friksjonsjordarter.<engelsk>data from
    measurements of in situ deformation- and consolidation properties in friction soils.</engelsk>

        Attributes:
            tid_fra_start (int | Unset): tid fra start av prøvingen [minutter]<engelsk>time from the start of testing
                (minutes)</engelsk>
            anvendt_last (float | Unset): last overført til skruplate gjennom stangsystemet [kN]<engelsk>load transferred to
                the screw plate through the rod system</engelsk>
            nedpressing_hastighet (float | Unset): nedpressingshastighet av skruplate ved gjennomføring av prøving [m/min]
                <engelsk>settlement rate for the screw plate during testing</engelsk>
            deformasjon (float | Unset): endring i form som følge av tilført kraft [mm] <engelsk>change in shape because of
                force </engelsk>
    """

    tid_fra_start: int | Unset = UNSET
    anvendt_last: float | Unset = UNSET
    nedpressing_hastighet: float | Unset = UNSET
    deformasjon: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tid_fra_start = self.tid_fra_start

        anvendt_last = self.anvendt_last

        nedpressing_hastighet = self.nedpressing_hastighet

        deformasjon = self.deformasjon

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tid_fra_start is not UNSET:
            field_dict["tidFraStart"] = tid_fra_start
        if anvendt_last is not UNSET:
            field_dict["anvendtLast"] = anvendt_last
        if nedpressing_hastighet is not UNSET:
            field_dict["nedpressingHastighet"] = nedpressing_hastighet
        if deformasjon is not UNSET:
            field_dict["deformasjon"] = deformasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tid_fra_start = d.pop("tidFraStart", UNSET)

        anvendt_last = d.pop("anvendtLast", UNSET)

        nedpressing_hastighet = d.pop("nedpressingHastighet", UNSET)

        deformasjon = d.pop("deformasjon", UNSET)

        platebelastning_data = cls(
            tid_fra_start=tid_fra_start,
            anvendt_last=anvendt_last,
            nedpressing_hastighet=nedpressing_hastighet,
            deformasjon=deformasjon,
        )

        platebelastning_data.additional_properties = d
        return platebelastning_data

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
