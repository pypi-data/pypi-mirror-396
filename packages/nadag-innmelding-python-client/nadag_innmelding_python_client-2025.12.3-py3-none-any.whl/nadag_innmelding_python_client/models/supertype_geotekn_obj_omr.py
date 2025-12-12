from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.identifikasjon import Identifikasjon


T = TypeVar("T", bound="SupertypeGeoteknObjOmr")


@_attrs_define
class SupertypeGeoteknObjOmr:
    """abstrakt objekt som bærer en rekke egenskaper som er fagområde-uavhengige og kan benyttes for alle objekttyper

    Merknad:
    Spesielt i produktspesifikasjonsarbeid vil en velge egenskaper og av grensningslinjer fra denne klassen.

        Attributes:
            identifikasjon (Identifikasjon | Unset): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            oppdateringsdato (datetime.datetime | Unset): dato for siste endring på objektetdataene

                Merknad:
                Oppdateringsdato kan være forskjellig fra Datafangsdato ved at data som er registrert kan bufres en kortere
                eller lengre periode før disse legges inn i datasystemet (databasen).

                -Definition-
                Date and time at which this version of the spatial object was inserted or changed in the spatial data set.
    """

    identifikasjon: Identifikasjon | Unset = UNSET
    oppdateringsdato: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifikasjon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        oppdateringsdato: str | Unset = UNSET
        if not isinstance(self.oppdateringsdato, Unset):
            oppdateringsdato = self.oppdateringsdato.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if identifikasjon is not UNSET:
            field_dict["identifikasjon"] = identifikasjon
        if oppdateringsdato is not UNSET:
            field_dict["oppdateringsdato"] = oppdateringsdato

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.identifikasjon import Identifikasjon

        d = dict(src_dict)
        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Identifikasjon | Unset
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        _oppdateringsdato = d.pop("oppdateringsdato", UNSET)
        oppdateringsdato: datetime.datetime | Unset
        if isinstance(_oppdateringsdato, Unset):
            oppdateringsdato = UNSET
        else:
            oppdateringsdato = isoparse(_oppdateringsdato)

        supertype_geotekn_obj_omr = cls(
            identifikasjon=identifikasjon,
            oppdateringsdato=oppdateringsdato,
        )

        supertype_geotekn_obj_omr.additional_properties = d
        return supertype_geotekn_obj_omr

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
