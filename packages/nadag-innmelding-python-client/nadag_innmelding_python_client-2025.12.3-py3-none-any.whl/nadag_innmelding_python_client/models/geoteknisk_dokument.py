from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.nadag_dokument_type import NADAGDokumentType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ekstern_identifikasjon import EksternIdentifikasjon


T = TypeVar("T", bound="GeotekniskDokument")


@_attrs_define
class GeotekniskDokument:
    """dokument(er) tilhørende geotekniske undersøkelsesområder og borehull <engelsk>accompanying documents to geotechnical
    investigation areas and boreholes</engelsk>

        Attributes:
            dokument_id (str | Unset): Unik nøkkel for dokument.
            dokument_nø_kkel (str | Unset): Benyttes til å angi nøkkelverdi ved kall til Web-api.
            dokument_type (NADAGDokumentType | Unset): Typer av dokument brukt i NADAG forvaltningsløsning.
            dokument_filnavn (str | Unset): Filnavn på dokumentet.
            dokument_url (str | Unset): Komplett URL for dokument med id.
            innhold_type (str | Unset): Type dokumentformat, feks. Image/png, pdf
            beskrivelse (str | Unset): Kort informasjon om dokumentet
            ekstern_identifikasjon (EksternIdentifikasjon | Unset): Identifikasjon av et objekt, ivaretatt av den ansvarlige
                leverandør inn til NADAG.
            dokument_navn (str | Unset): Navn på dokument
            opprettet_dato (datetime.datetime | Unset): Når objektet ble opprettet i database (Nadag)
            dokument_nr (str | Unset): Feks. rapportNr.
            dokument_dato (datetime.datetime | Unset): Dato når dokument ble opprettet
    """

    dokument_id: str | Unset = UNSET
    dokument_nø_kkel: str | Unset = UNSET
    dokument_type: NADAGDokumentType | Unset = UNSET
    dokument_filnavn: str | Unset = UNSET
    dokument_url: str | Unset = UNSET
    innhold_type: str | Unset = UNSET
    beskrivelse: str | Unset = UNSET
    ekstern_identifikasjon: EksternIdentifikasjon | Unset = UNSET
    dokument_navn: str | Unset = UNSET
    opprettet_dato: datetime.datetime | Unset = UNSET
    dokument_nr: str | Unset = UNSET
    dokument_dato: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dokument_id = self.dokument_id

        dokument_nø_kkel = self.dokument_nø_kkel

        dokument_type: str | Unset = UNSET
        if not isinstance(self.dokument_type, Unset):
            dokument_type = self.dokument_type.value

        dokument_filnavn = self.dokument_filnavn

        dokument_url = self.dokument_url

        innhold_type = self.innhold_type

        beskrivelse = self.beskrivelse

        ekstern_identifikasjon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = self.ekstern_identifikasjon.to_dict()

        dokument_navn = self.dokument_navn

        opprettet_dato: str | Unset = UNSET
        if not isinstance(self.opprettet_dato, Unset):
            opprettet_dato = self.opprettet_dato.isoformat()

        dokument_nr = self.dokument_nr

        dokument_dato: str | Unset = UNSET
        if not isinstance(self.dokument_dato, Unset):
            dokument_dato = self.dokument_dato.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dokument_id is not UNSET:
            field_dict["dokumentID"] = dokument_id
        if dokument_nø_kkel is not UNSET:
            field_dict["dokumentNøkkel"] = dokument_nø_kkel
        if dokument_type is not UNSET:
            field_dict["dokumentType"] = dokument_type
        if dokument_filnavn is not UNSET:
            field_dict["dokumentFilnavn"] = dokument_filnavn
        if dokument_url is not UNSET:
            field_dict["dokumentURL"] = dokument_url
        if innhold_type is not UNSET:
            field_dict["innholdType"] = innhold_type
        if beskrivelse is not UNSET:
            field_dict["beskrivelse"] = beskrivelse
        if ekstern_identifikasjon is not UNSET:
            field_dict["eksternIdentifikasjon"] = ekstern_identifikasjon
        if dokument_navn is not UNSET:
            field_dict["dokumentNavn"] = dokument_navn
        if opprettet_dato is not UNSET:
            field_dict["opprettetDato"] = opprettet_dato
        if dokument_nr is not UNSET:
            field_dict["dokumentNr"] = dokument_nr
        if dokument_dato is not UNSET:
            field_dict["dokumentDato"] = dokument_dato

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ekstern_identifikasjon import EksternIdentifikasjon

        d = dict(src_dict)
        dokument_id = d.pop("dokumentID", UNSET)

        dokument_nø_kkel = d.pop("dokumentNøkkel", UNSET)

        _dokument_type = d.pop("dokumentType", UNSET)
        dokument_type: NADAGDokumentType | Unset
        if isinstance(_dokument_type, Unset):
            dokument_type = UNSET
        else:
            dokument_type = NADAGDokumentType(_dokument_type)

        dokument_filnavn = d.pop("dokumentFilnavn", UNSET)

        dokument_url = d.pop("dokumentURL", UNSET)

        innhold_type = d.pop("innholdType", UNSET)

        beskrivelse = d.pop("beskrivelse", UNSET)

        _ekstern_identifikasjon = d.pop("eksternIdentifikasjon", UNSET)
        ekstern_identifikasjon: EksternIdentifikasjon | Unset
        if isinstance(_ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = UNSET
        else:
            ekstern_identifikasjon = EksternIdentifikasjon.from_dict(_ekstern_identifikasjon)

        dokument_navn = d.pop("dokumentNavn", UNSET)

        _opprettet_dato = d.pop("opprettetDato", UNSET)
        opprettet_dato: datetime.datetime | Unset
        if isinstance(_opprettet_dato, Unset):
            opprettet_dato = UNSET
        else:
            opprettet_dato = isoparse(_opprettet_dato)

        dokument_nr = d.pop("dokumentNr", UNSET)

        _dokument_dato = d.pop("dokumentDato", UNSET)
        dokument_dato: datetime.datetime | Unset
        if isinstance(_dokument_dato, Unset):
            dokument_dato = UNSET
        else:
            dokument_dato = isoparse(_dokument_dato)

        geoteknisk_dokument = cls(
            dokument_id=dokument_id,
            dokument_nø_kkel=dokument_nø_kkel,
            dokument_type=dokument_type,
            dokument_filnavn=dokument_filnavn,
            dokument_url=dokument_url,
            innhold_type=innhold_type,
            beskrivelse=beskrivelse,
            ekstern_identifikasjon=ekstern_identifikasjon,
            dokument_navn=dokument_navn,
            opprettet_dato=opprettet_dato,
            dokument_nr=dokument_nr,
            dokument_dato=dokument_dato,
        )

        geoteknisk_dokument.additional_properties = d
        return geoteknisk_dokument

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
