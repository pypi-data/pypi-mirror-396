from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.nadag_hoeyderef import NADAGHoeyderef
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.geoteknisk_tolket_lag import GeotekniskTolketLag
    from ..models.identifikasjon import Identifikasjon
    from ..models.point import Point


T = TypeVar("T", bound="GeotekniskTolketPunkt")


@_attrs_define
class GeotekniskTolketPunkt:
    """Punkt med geoteknisk tolkning i GeotekniskTolketLag

    Attributes:
        identifikasjon (Identifikasjon | Unset): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
            produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

            NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
            f.eks bygningsnummer.

            NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
        tolket_av (str | Unset): Hvem som har tolket punktet
        tolket_tidspunkt (datetime.datetime | Unset): Når tolkning ble utført
        navn (str | Unset): Navn på tolket punkt
        posisjon (Point | Unset):
        høyde (float | Unset): Terrenghøyde overflate for punkt med tolkning(/er)[m]
        h_ø_yde_referanse (NADAGHoeyderef | Unset): Brukte høydereferansesystemer i NADAG for egenskapen Høyde. EPSG-
            koder benyttes.
        har_tolket_lag (list[GeotekniskTolketLag] | Unset):
    """

    identifikasjon: Identifikasjon | Unset = UNSET
    tolket_av: str | Unset = UNSET
    tolket_tidspunkt: datetime.datetime | Unset = UNSET
    navn: str | Unset = UNSET
    posisjon: Point | Unset = UNSET
    høyde: float | Unset = UNSET
    h_ø_yde_referanse: NADAGHoeyderef | Unset = UNSET
    har_tolket_lag: list[GeotekniskTolketLag] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifikasjon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        tolket_av = self.tolket_av

        tolket_tidspunkt: str | Unset = UNSET
        if not isinstance(self.tolket_tidspunkt, Unset):
            tolket_tidspunkt = self.tolket_tidspunkt.isoformat()

        navn = self.navn

        posisjon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.posisjon, Unset):
            posisjon = self.posisjon.to_dict()

        høyde = self.høyde

        h_ø_yde_referanse: str | Unset = UNSET
        if not isinstance(self.h_ø_yde_referanse, Unset):
            h_ø_yde_referanse = self.h_ø_yde_referanse.value

        har_tolket_lag: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.har_tolket_lag, Unset):
            har_tolket_lag = []
            for har_tolket_lag_item_data in self.har_tolket_lag:
                har_tolket_lag_item = har_tolket_lag_item_data.to_dict()
                har_tolket_lag.append(har_tolket_lag_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if identifikasjon is not UNSET:
            field_dict["identifikasjon"] = identifikasjon
        if tolket_av is not UNSET:
            field_dict["tolketAv"] = tolket_av
        if tolket_tidspunkt is not UNSET:
            field_dict["tolketTidspunkt"] = tolket_tidspunkt
        if navn is not UNSET:
            field_dict["navn"] = navn
        if posisjon is not UNSET:
            field_dict["posisjon"] = posisjon
        if høyde is not UNSET:
            field_dict["høyde"] = høyde
        if h_ø_yde_referanse is not UNSET:
            field_dict["høydeReferanse"] = h_ø_yde_referanse
        if har_tolket_lag is not UNSET:
            field_dict["harTolketLag"] = har_tolket_lag

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.geoteknisk_tolket_lag import GeotekniskTolketLag
        from ..models.identifikasjon import Identifikasjon
        from ..models.point import Point

        d = dict(src_dict)
        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Identifikasjon | Unset
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        tolket_av = d.pop("tolketAv", UNSET)

        _tolket_tidspunkt = d.pop("tolketTidspunkt", UNSET)
        tolket_tidspunkt: datetime.datetime | Unset
        if isinstance(_tolket_tidspunkt, Unset):
            tolket_tidspunkt = UNSET
        else:
            tolket_tidspunkt = isoparse(_tolket_tidspunkt)

        navn = d.pop("navn", UNSET)

        _posisjon = d.pop("posisjon", UNSET)
        posisjon: Point | Unset
        if isinstance(_posisjon, Unset):
            posisjon = UNSET
        else:
            posisjon = Point.from_dict(_posisjon)

        høyde = d.pop("høyde", UNSET)

        _h_ø_yde_referanse = d.pop("høydeReferanse", UNSET)
        h_ø_yde_referanse: NADAGHoeyderef | Unset
        if isinstance(_h_ø_yde_referanse, Unset):
            h_ø_yde_referanse = UNSET
        else:
            h_ø_yde_referanse = NADAGHoeyderef(_h_ø_yde_referanse)

        _har_tolket_lag = d.pop("harTolketLag", UNSET)
        har_tolket_lag: list[GeotekniskTolketLag] | Unset = UNSET
        if _har_tolket_lag is not UNSET:
            har_tolket_lag = []
            for har_tolket_lag_item_data in _har_tolket_lag:
                har_tolket_lag_item = GeotekniskTolketLag.from_dict(har_tolket_lag_item_data)

                har_tolket_lag.append(har_tolket_lag_item)

        geoteknisk_tolket_punkt = cls(
            identifikasjon=identifikasjon,
            tolket_av=tolket_av,
            tolket_tidspunkt=tolket_tidspunkt,
            navn=navn,
            posisjon=posisjon,
            høyde=høyde,
            h_ø_yde_referanse=h_ø_yde_referanse,
            har_tolket_lag=har_tolket_lag,
        )

        geoteknisk_tolket_punkt.additional_properties = d
        return geoteknisk_tolket_punkt

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
