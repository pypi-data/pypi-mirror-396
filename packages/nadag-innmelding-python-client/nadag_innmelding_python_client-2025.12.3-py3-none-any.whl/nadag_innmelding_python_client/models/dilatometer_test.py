from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dilatometer_test_data import DilatometerTestData
    from ..models.identifikasjon import Identifikasjon


T = TypeVar("T", bound="DilatometerTest")


@_attrs_define
class DilatometerTest:
    """en enkel innretning, formet som et flatt blad designet for å trykkes ned i bakken. Merknad: ble utviklet for å
    bestemme modulus for en jordart.
    <engelsk>a simple device, shaped in the form of a flat blade designed to be pushed into the ground Note: It was
    developed to evaluate the soil modulus.</engelsk>

        Attributes:
            json_type (Literal['DilatometerTest'] | Unset):
            identifikasjon (Identifikasjon | Unset): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            fra_borlengde (float | Unset): lengde målt fra toppen av kurven/linja som beskriver borehullforløpet [m]
                <engelsk>distance measured from the top of  the curve describing the borehole geometry</engelsk>
            til_borlengde (float | Unset): lengde målt fra toppen av kurven/linja som beskriver borehullforløpet [m]
                <engelsk>distance measured from the top of  the curve describing the borehole geometry</engelsk>
            insitu_test_start_tidspunkt (datetime.datetime | Unset): tidspunkt for start av in situ prøvningen<engelsk>start
                time for in situ testing</engelsk>
            insitu_test_slutt_tidspunkt (datetime.datetime | Unset): tidspunkt for stopp av in situ prøvningen<engelsk>stop
                time for in situ testing</engelsk>
            material_indeks (float | Unset): materialindeks<engelsk>material index</engelsk>
            horisontal_spenning_indeks (float | Unset): horisontalspenning index<engelsk>horizontal stress index</engelsk>
            dilatometer_modulus (float | Unset): dilatometer modulus<engelsk>dilatometer modulus</engelsk>
            dilatometer_observasjon (list[DilatometerTestData] | Unset):
    """

    json_type: Literal["DilatometerTest"] | Unset = UNSET
    identifikasjon: Identifikasjon | Unset = UNSET
    fra_borlengde: float | Unset = UNSET
    til_borlengde: float | Unset = UNSET
    insitu_test_start_tidspunkt: datetime.datetime | Unset = UNSET
    insitu_test_slutt_tidspunkt: datetime.datetime | Unset = UNSET
    material_indeks: float | Unset = UNSET
    horisontal_spenning_indeks: float | Unset = UNSET
    dilatometer_modulus: float | Unset = UNSET
    dilatometer_observasjon: list[DilatometerTestData] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        json_type = self.json_type

        identifikasjon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        fra_borlengde = self.fra_borlengde

        til_borlengde = self.til_borlengde

        insitu_test_start_tidspunkt: str | Unset = UNSET
        if not isinstance(self.insitu_test_start_tidspunkt, Unset):
            insitu_test_start_tidspunkt = self.insitu_test_start_tidspunkt.isoformat()

        insitu_test_slutt_tidspunkt: str | Unset = UNSET
        if not isinstance(self.insitu_test_slutt_tidspunkt, Unset):
            insitu_test_slutt_tidspunkt = self.insitu_test_slutt_tidspunkt.isoformat()

        material_indeks = self.material_indeks

        horisontal_spenning_indeks = self.horisontal_spenning_indeks

        dilatometer_modulus = self.dilatometer_modulus

        dilatometer_observasjon: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.dilatometer_observasjon, Unset):
            dilatometer_observasjon = []
            for dilatometer_observasjon_item_data in self.dilatometer_observasjon:
                dilatometer_observasjon_item = dilatometer_observasjon_item_data.to_dict()
                dilatometer_observasjon.append(dilatometer_observasjon_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if json_type is not UNSET:
            field_dict["jsonType"] = json_type
        if identifikasjon is not UNSET:
            field_dict["identifikasjon"] = identifikasjon
        if fra_borlengde is not UNSET:
            field_dict["fraBorlengde"] = fra_borlengde
        if til_borlengde is not UNSET:
            field_dict["tilBorlengde"] = til_borlengde
        if insitu_test_start_tidspunkt is not UNSET:
            field_dict["insituTestStartTidspunkt"] = insitu_test_start_tidspunkt
        if insitu_test_slutt_tidspunkt is not UNSET:
            field_dict["insituTestSluttTidspunkt"] = insitu_test_slutt_tidspunkt
        if material_indeks is not UNSET:
            field_dict["materialIndeks"] = material_indeks
        if horisontal_spenning_indeks is not UNSET:
            field_dict["horisontalSpenningIndeks"] = horisontal_spenning_indeks
        if dilatometer_modulus is not UNSET:
            field_dict["dilatometerModulus"] = dilatometer_modulus
        if dilatometer_observasjon is not UNSET:
            field_dict["dilatometerObservasjon"] = dilatometer_observasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dilatometer_test_data import DilatometerTestData
        from ..models.identifikasjon import Identifikasjon

        d = dict(src_dict)
        json_type = cast(Literal["DilatometerTest"] | Unset, d.pop("jsonType", UNSET))
        if json_type != "DilatometerTest" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'DilatometerTest', got '{json_type}'")

        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Identifikasjon | Unset
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        fra_borlengde = d.pop("fraBorlengde", UNSET)

        til_borlengde = d.pop("tilBorlengde", UNSET)

        _insitu_test_start_tidspunkt = d.pop("insituTestStartTidspunkt", UNSET)
        insitu_test_start_tidspunkt: datetime.datetime | Unset
        if isinstance(_insitu_test_start_tidspunkt, Unset):
            insitu_test_start_tidspunkt = UNSET
        else:
            insitu_test_start_tidspunkt = isoparse(_insitu_test_start_tidspunkt)

        _insitu_test_slutt_tidspunkt = d.pop("insituTestSluttTidspunkt", UNSET)
        insitu_test_slutt_tidspunkt: datetime.datetime | Unset
        if isinstance(_insitu_test_slutt_tidspunkt, Unset):
            insitu_test_slutt_tidspunkt = UNSET
        else:
            insitu_test_slutt_tidspunkt = isoparse(_insitu_test_slutt_tidspunkt)

        material_indeks = d.pop("materialIndeks", UNSET)

        horisontal_spenning_indeks = d.pop("horisontalSpenningIndeks", UNSET)

        dilatometer_modulus = d.pop("dilatometerModulus", UNSET)

        _dilatometer_observasjon = d.pop("dilatometerObservasjon", UNSET)
        dilatometer_observasjon: list[DilatometerTestData] | Unset = UNSET
        if _dilatometer_observasjon is not UNSET:
            dilatometer_observasjon = []
            for dilatometer_observasjon_item_data in _dilatometer_observasjon:
                dilatometer_observasjon_item = DilatometerTestData.from_dict(dilatometer_observasjon_item_data)

                dilatometer_observasjon.append(dilatometer_observasjon_item)

        dilatometer_test = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            insitu_test_start_tidspunkt=insitu_test_start_tidspunkt,
            insitu_test_slutt_tidspunkt=insitu_test_slutt_tidspunkt,
            material_indeks=material_indeks,
            horisontal_spenning_indeks=horisontal_spenning_indeks,
            dilatometer_modulus=dilatometer_modulus,
            dilatometer_observasjon=dilatometer_observasjon,
        )

        dilatometer_test.additional_properties = d
        return dilatometer_test

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
