from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.gjennomboret_medium import GjennomboretMedium
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.borlengde_til_berg import BorlengdeTilBerg
    from ..models.identifikasjon import Identifikasjon
    from ..models.point import Point
    from ..models.posisjonskvalitet_nadag import PosisjonskvalitetNADAG


T = TypeVar("T", bound="GeovitenskapligBorehull")


@_attrs_define
class GeovitenskapligBorehull:
    """område representert ved et punkt hvor det skal foretas en eller flere borehullundersøkelser - også kalt logisk
    borehull i motsetning til borhullundersøkelse som representerer hvert fysiske borehull

    Merknad: Det logiske borehullet har en posisjon som representerer de fysiske borhullundersøkelsene foretatt i
    området

    <engelsk>
    borehole consists of one or more physical borehole investigations. The borehole has a position, representing a
    collection of borehole investigations. The position of the borehole is often given the same position as one of the
    asscoated borehole investigations. The associated borehole investigations should be in a reasonable short distance
    (e.g. 0,5 m) from the position of the borehole.
    </engelsk>

        Attributes:
            datafangstdato (datetime.datetime | Unset): dato når objektet siste gang ble registrert/observert/målt i
                terrenget

                Merknad: I mange tilfeller er denne forskjellig fra Oppdateringsdato, da registrerte endringer kan bufres i en
                kortere eller lengre periode før disse legges inn i databasen.
                Ved førstegangsregistrering settes Datafangstdato lik førsteDatafangstdato.
            digitaliseringsmålestokk (int | Unset): kartmålestokk registreringene/ datene er hentet fra/ registrert på

                Eksempel: 1:50 000 = 50000.
            identifikasjon (Identifikasjon | Unset): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            kvalitet (PosisjonskvalitetNADAG | Unset): Posisjonskvalitet slik den brukes i NADAG (Nasjonal Database for
                Grunnundersøkelser).
                (En realisering av den generelle Posisjonskvalitet)
            oppdateringsdato (datetime.datetime | Unset): dato for siste endring på objektetdataene

                Merknad:
                Oppdateringsdato kan være forskjellig fra Datafangsdato ved at data som er registrert kan bufres en kortere
                eller lengre periode før disse legges inn i datasystemet (databasen).

                -Definition-
                Date and time at which this version of the spatial object was inserted or changed in the spatial data set.
            antall_borehull_unders_ø_kelser (int | Unset): antall borehullsundersøkeelser i borehullets område

                Merknad: Borhullet er et logisk borhull hvor det innen et lite område er foretatt flere fysiske
                borhullsundersøkelser som tilhører det samme borehull.

                <engelsk>
                Number of boreholeInvestigations (virtual boreholes) performed at the location of the borehole

                Note: A virtual borehole is a fictitious feature for all boreholes/soundings performed within an reasonable
                small area (e.g. <5 m or so)</engelsk>
            beskrivelse (str | Unset): forklaring til objektet og undersøkelser utført på lokaliteten

                <engelsk>
                a short description of the investigations at the location of the borehole</engelsk>
            boret_lengde_til_berg (BorlengdeTilBerg | Unset): dybde til fjell som ikke er målt men basert på tolkning

                <engelsk>
                depth to bedrock based on interpretation
                </engelsk>
            gjennomboret_medium (list[GjennomboretMedium] | Unset): material som er gjennomboret

                Merknad: spesifisert ved å bruke kodeliste GjennomboretMedium.

                <engelsk>
                material penetrated by the borehole

                Note: Specified by using codes from codelist: GjennomboretMedium
                </engelsk>
            posisjon (Point | Unset):
    """

    datafangstdato: datetime.datetime | Unset = UNSET
    digitaliseringsmålestokk: int | Unset = UNSET
    identifikasjon: Identifikasjon | Unset = UNSET
    kvalitet: PosisjonskvalitetNADAG | Unset = UNSET
    oppdateringsdato: datetime.datetime | Unset = UNSET
    antall_borehull_unders_ø_kelser: int | Unset = UNSET
    beskrivelse: str | Unset = UNSET
    boret_lengde_til_berg: BorlengdeTilBerg | Unset = UNSET
    gjennomboret_medium: list[GjennomboretMedium] | Unset = UNSET
    posisjon: Point | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        datafangstdato: str | Unset = UNSET
        if not isinstance(self.datafangstdato, Unset):
            datafangstdato = self.datafangstdato.isoformat()

        digitaliseringsmålestokk = self.digitaliseringsmålestokk

        identifikasjon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        kvalitet: dict[str, Any] | Unset = UNSET
        if not isinstance(self.kvalitet, Unset):
            kvalitet = self.kvalitet.to_dict()

        oppdateringsdato: str | Unset = UNSET
        if not isinstance(self.oppdateringsdato, Unset):
            oppdateringsdato = self.oppdateringsdato.isoformat()

        antall_borehull_unders_ø_kelser = self.antall_borehull_unders_ø_kelser

        beskrivelse = self.beskrivelse

        boret_lengde_til_berg: dict[str, Any] | Unset = UNSET
        if not isinstance(self.boret_lengde_til_berg, Unset):
            boret_lengde_til_berg = self.boret_lengde_til_berg.to_dict()

        gjennomboret_medium: list[str] | Unset = UNSET
        if not isinstance(self.gjennomboret_medium, Unset):
            gjennomboret_medium = []
            for gjennomboret_medium_item_data in self.gjennomboret_medium:
                gjennomboret_medium_item = gjennomboret_medium_item_data.value
                gjennomboret_medium.append(gjennomboret_medium_item)

        posisjon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.posisjon, Unset):
            posisjon = self.posisjon.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if datafangstdato is not UNSET:
            field_dict["datafangstdato"] = datafangstdato
        if digitaliseringsmålestokk is not UNSET:
            field_dict["digitaliseringsmålestokk"] = digitaliseringsmålestokk
        if identifikasjon is not UNSET:
            field_dict["identifikasjon"] = identifikasjon
        if kvalitet is not UNSET:
            field_dict["kvalitet"] = kvalitet
        if oppdateringsdato is not UNSET:
            field_dict["oppdateringsdato"] = oppdateringsdato
        if antall_borehull_unders_ø_kelser is not UNSET:
            field_dict["antallBorehullUndersøkelser"] = antall_borehull_unders_ø_kelser
        if beskrivelse is not UNSET:
            field_dict["beskrivelse"] = beskrivelse
        if boret_lengde_til_berg is not UNSET:
            field_dict["boretLengdeTilBerg"] = boret_lengde_til_berg
        if gjennomboret_medium is not UNSET:
            field_dict["gjennomboretMedium"] = gjennomboret_medium
        if posisjon is not UNSET:
            field_dict["posisjon"] = posisjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.borlengde_til_berg import BorlengdeTilBerg
        from ..models.identifikasjon import Identifikasjon
        from ..models.point import Point
        from ..models.posisjonskvalitet_nadag import PosisjonskvalitetNADAG

        d = dict(src_dict)
        _datafangstdato = d.pop("datafangstdato", UNSET)
        datafangstdato: datetime.datetime | Unset
        if isinstance(_datafangstdato, Unset):
            datafangstdato = UNSET
        else:
            datafangstdato = isoparse(_datafangstdato)

        digitaliseringsmålestokk = d.pop("digitaliseringsmålestokk", UNSET)

        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Identifikasjon | Unset
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        _kvalitet = d.pop("kvalitet", UNSET)
        kvalitet: PosisjonskvalitetNADAG | Unset
        if isinstance(_kvalitet, Unset):
            kvalitet = UNSET
        else:
            kvalitet = PosisjonskvalitetNADAG.from_dict(_kvalitet)

        _oppdateringsdato = d.pop("oppdateringsdato", UNSET)
        oppdateringsdato: datetime.datetime | Unset
        if isinstance(_oppdateringsdato, Unset):
            oppdateringsdato = UNSET
        else:
            oppdateringsdato = isoparse(_oppdateringsdato)

        antall_borehull_unders_ø_kelser = d.pop("antallBorehullUndersøkelser", UNSET)

        beskrivelse = d.pop("beskrivelse", UNSET)

        _boret_lengde_til_berg = d.pop("boretLengdeTilBerg", UNSET)
        boret_lengde_til_berg: BorlengdeTilBerg | Unset
        if isinstance(_boret_lengde_til_berg, Unset):
            boret_lengde_til_berg = UNSET
        else:
            boret_lengde_til_berg = BorlengdeTilBerg.from_dict(_boret_lengde_til_berg)

        _gjennomboret_medium = d.pop("gjennomboretMedium", UNSET)
        gjennomboret_medium: list[GjennomboretMedium] | Unset = UNSET
        if _gjennomboret_medium is not UNSET:
            gjennomboret_medium = []
            for gjennomboret_medium_item_data in _gjennomboret_medium:
                gjennomboret_medium_item = GjennomboretMedium(gjennomboret_medium_item_data)

                gjennomboret_medium.append(gjennomboret_medium_item)

        _posisjon = d.pop("posisjon", UNSET)
        posisjon: Point | Unset
        if isinstance(_posisjon, Unset):
            posisjon = UNSET
        else:
            posisjon = Point.from_dict(_posisjon)

        geovitenskaplig_borehull = cls(
            datafangstdato=datafangstdato,
            digitaliseringsmålestokk=digitaliseringsmålestokk,
            identifikasjon=identifikasjon,
            kvalitet=kvalitet,
            oppdateringsdato=oppdateringsdato,
            antall_borehull_unders_ø_kelser=antall_borehull_unders_ø_kelser,
            beskrivelse=beskrivelse,
            boret_lengde_til_berg=boret_lengde_til_berg,
            gjennomboret_medium=gjennomboret_medium,
            posisjon=posisjon,
        )

        geovitenskaplig_borehull.additional_properties = d
        return geovitenskaplig_borehull

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
