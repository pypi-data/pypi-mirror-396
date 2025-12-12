from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.hoved_lag_klassifisering import HovedLagKlassifisering
from ..models.klassifiserings_metode import KlassifiseringsMetode
from ..models.nadag_hoeyderef import NADAGHoeyderef
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ekstern_identifikasjon import EksternIdentifikasjon
    from ..models.point import Point


T = TypeVar("T", bound="GeotekniskTolketLag")


@_attrs_define
class GeotekniskTolketLag:
    """Lag med geoteknisk tolkning

    Attributes:
        tolket_lag_id (str | Unset): Unik nøkkel for tolktet lag
        klassifisering_metode (KlassifiseringsMetode | Unset): oversikt over klassifiseringsmetoder for bestemmelse av
            grunnforhold<engelsk>overview of classification methods for determination of ground conditions</engelsk>
        hoved_lag_klassifiserings_kode (HovedLagKlassifisering | Unset): oversikt over lagdeling og jordart for
            klassifisering og identifisering av grunnforhold<engelsk>overview of stratification and soil type for
            classification and identification of ground conditions</engelsk>
        lag_beskrivelse (str | Unset): Beskrivelse av tolket lag feks. Sand
        tolket_av (str | Unset): Hvem som har gjort tolkning
        tolket_tidspunkt (datetime.datetime | Unset): Når tolkning ble utført
        tolkning_merknad (str | Unset): Kommentar til tolkning
        navn (str | Unset): Navn på tolket lag
        p_å_terreng_overflate (bool | Unset): Om tolkning er på terrengoverflate
        vurdering (float | Unset): Hvor sikker tolkning er, med  0=Udefinert,5=Sikker og glidende skala imellom.
        under_terreng_overflate (bool | Unset): Om tolkning er under terrengoverflate
        ekstern_identifikasjon (EksternIdentifikasjon | Unset): Identifikasjon av et objekt, ivaretatt av den ansvarlige
            leverandør inn til NADAG.
        posisjon (Point | Unset):
        høyde (float | Unset): Laghøyde for tolkning [m]
        h_ø_yde_referanse (NADAGHoeyderef | Unset): Brukte høydereferansesystemer i NADAG for egenskapen Høyde. EPSG-
            koder benyttes.
    """

    tolket_lag_id: str | Unset = UNSET
    klassifisering_metode: KlassifiseringsMetode | Unset = UNSET
    hoved_lag_klassifiserings_kode: HovedLagKlassifisering | Unset = UNSET
    lag_beskrivelse: str | Unset = UNSET
    tolket_av: str | Unset = UNSET
    tolket_tidspunkt: datetime.datetime | Unset = UNSET
    tolkning_merknad: str | Unset = UNSET
    navn: str | Unset = UNSET
    p_å_terreng_overflate: bool | Unset = UNSET
    vurdering: float | Unset = UNSET
    under_terreng_overflate: bool | Unset = UNSET
    ekstern_identifikasjon: EksternIdentifikasjon | Unset = UNSET
    posisjon: Point | Unset = UNSET
    høyde: float | Unset = UNSET
    h_ø_yde_referanse: NADAGHoeyderef | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tolket_lag_id = self.tolket_lag_id

        klassifisering_metode: str | Unset = UNSET
        if not isinstance(self.klassifisering_metode, Unset):
            klassifisering_metode = self.klassifisering_metode.value

        hoved_lag_klassifiserings_kode: str | Unset = UNSET
        if not isinstance(self.hoved_lag_klassifiserings_kode, Unset):
            hoved_lag_klassifiserings_kode = self.hoved_lag_klassifiserings_kode.value

        lag_beskrivelse = self.lag_beskrivelse

        tolket_av = self.tolket_av

        tolket_tidspunkt: str | Unset = UNSET
        if not isinstance(self.tolket_tidspunkt, Unset):
            tolket_tidspunkt = self.tolket_tidspunkt.isoformat()

        tolkning_merknad = self.tolkning_merknad

        navn = self.navn

        p_å_terreng_overflate = self.p_å_terreng_overflate

        vurdering = self.vurdering

        under_terreng_overflate = self.under_terreng_overflate

        ekstern_identifikasjon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = self.ekstern_identifikasjon.to_dict()

        posisjon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.posisjon, Unset):
            posisjon = self.posisjon.to_dict()

        høyde = self.høyde

        h_ø_yde_referanse: str | Unset = UNSET
        if not isinstance(self.h_ø_yde_referanse, Unset):
            h_ø_yde_referanse = self.h_ø_yde_referanse.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tolket_lag_id is not UNSET:
            field_dict["tolketLagID"] = tolket_lag_id
        if klassifisering_metode is not UNSET:
            field_dict["klassifiseringMetode"] = klassifisering_metode
        if hoved_lag_klassifiserings_kode is not UNSET:
            field_dict["hovedLagKlassifiseringsKode"] = hoved_lag_klassifiserings_kode
        if lag_beskrivelse is not UNSET:
            field_dict["lagBeskrivelse"] = lag_beskrivelse
        if tolket_av is not UNSET:
            field_dict["tolketAv"] = tolket_av
        if tolket_tidspunkt is not UNSET:
            field_dict["tolketTidspunkt"] = tolket_tidspunkt
        if tolkning_merknad is not UNSET:
            field_dict["tolkningMerknad"] = tolkning_merknad
        if navn is not UNSET:
            field_dict["navn"] = navn
        if p_å_terreng_overflate is not UNSET:
            field_dict["påTerrengOverflate"] = p_å_terreng_overflate
        if vurdering is not UNSET:
            field_dict["vurdering"] = vurdering
        if under_terreng_overflate is not UNSET:
            field_dict["underTerrengOverflate"] = under_terreng_overflate
        if ekstern_identifikasjon is not UNSET:
            field_dict["eksternIdentifikasjon"] = ekstern_identifikasjon
        if posisjon is not UNSET:
            field_dict["posisjon"] = posisjon
        if høyde is not UNSET:
            field_dict["høyde"] = høyde
        if h_ø_yde_referanse is not UNSET:
            field_dict["høydeReferanse"] = h_ø_yde_referanse

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ekstern_identifikasjon import EksternIdentifikasjon
        from ..models.point import Point

        d = dict(src_dict)
        tolket_lag_id = d.pop("tolketLagID", UNSET)

        _klassifisering_metode = d.pop("klassifiseringMetode", UNSET)
        klassifisering_metode: KlassifiseringsMetode | Unset
        if isinstance(_klassifisering_metode, Unset):
            klassifisering_metode = UNSET
        else:
            klassifisering_metode = KlassifiseringsMetode(_klassifisering_metode)

        _hoved_lag_klassifiserings_kode = d.pop("hovedLagKlassifiseringsKode", UNSET)
        hoved_lag_klassifiserings_kode: HovedLagKlassifisering | Unset
        if isinstance(_hoved_lag_klassifiserings_kode, Unset):
            hoved_lag_klassifiserings_kode = UNSET
        else:
            hoved_lag_klassifiserings_kode = HovedLagKlassifisering(_hoved_lag_klassifiserings_kode)

        lag_beskrivelse = d.pop("lagBeskrivelse", UNSET)

        tolket_av = d.pop("tolketAv", UNSET)

        _tolket_tidspunkt = d.pop("tolketTidspunkt", UNSET)
        tolket_tidspunkt: datetime.datetime | Unset
        if isinstance(_tolket_tidspunkt, Unset):
            tolket_tidspunkt = UNSET
        else:
            tolket_tidspunkt = isoparse(_tolket_tidspunkt)

        tolkning_merknad = d.pop("tolkningMerknad", UNSET)

        navn = d.pop("navn", UNSET)

        p_å_terreng_overflate = d.pop("påTerrengOverflate", UNSET)

        vurdering = d.pop("vurdering", UNSET)

        under_terreng_overflate = d.pop("underTerrengOverflate", UNSET)

        _ekstern_identifikasjon = d.pop("eksternIdentifikasjon", UNSET)
        ekstern_identifikasjon: EksternIdentifikasjon | Unset
        if isinstance(_ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = UNSET
        else:
            ekstern_identifikasjon = EksternIdentifikasjon.from_dict(_ekstern_identifikasjon)

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

        geoteknisk_tolket_lag = cls(
            tolket_lag_id=tolket_lag_id,
            klassifisering_metode=klassifisering_metode,
            hoved_lag_klassifiserings_kode=hoved_lag_klassifiserings_kode,
            lag_beskrivelse=lag_beskrivelse,
            tolket_av=tolket_av,
            tolket_tidspunkt=tolket_tidspunkt,
            tolkning_merknad=tolkning_merknad,
            navn=navn,
            p_å_terreng_overflate=p_å_terreng_overflate,
            vurdering=vurdering,
            under_terreng_overflate=under_terreng_overflate,
            ekstern_identifikasjon=ekstern_identifikasjon,
            posisjon=posisjon,
            høyde=høyde,
            h_ø_yde_referanse=h_ø_yde_referanse,
        )

        geoteknisk_tolket_lag.additional_properties = d
        return geoteknisk_tolket_lag

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
