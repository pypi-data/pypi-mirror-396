from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.representasjon_kvalitet import RepresentasjonKvalitet
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ekstern_identifikasjon import EksternIdentifikasjon
    from ..models.geoteknisk_borehull import GeotekniskBorehull
    from ..models.geoteknisk_dokument import GeotekniskDokument
    from ..models.geoteknisk_felt_unders import GeotekniskFeltUnders
    from ..models.geoteknisk_tolket_punkt import GeotekniskTolketPunkt
    from ..models.identifikasjon import Identifikasjon
    from ..models.multi_polygon import MultiPolygon
    from ..models.polygon import Polygon


T = TypeVar("T", bound="GeotekniskUnders")


@_attrs_define
class GeotekniskUnders:
    """geografisk område hvor det finnes eller er planlagt geotekniske borehull tilhørende et gitt prosjekt
    <engelsk>geographical area where there are or are planned geotechnical boreholes for a given project</engelsk>

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
            beskrivelse (str | Unset): beskrivelse av de geovitenskaplige undersøkelsene

                <engelsk>
                description of the geoscientific investigations
                </engelsk>
            område (Polygon | Unset):
            oppdragsgiver (str | Unset): identifikasjon av bestiller (kunde) og dennes organisasjon

                <engelsk>
                identifikation of the the customer organisation
                </engelsk>
            oppdragstaker (str | Unset): identifikasjon av utførende organisasjon

                <engelsk>
                identification of the the organisation responsible for carrying out the project
                </engelsk>
            prosjekt_navn (str | Unset): prosjekt navn og/eller nummer

                <engelsk>
                name or number of the project - e.g. projectnumber
                </engelsk>
            unders_ø_kelse_periode_fra (datetime.datetime | Unset): startdato for undersøkelsen

                <engelsk>
                starting date of the investigation
                </engelsk>
            sammensattområde (MultiPolygon | Unset):
            unders_ø_kelse_periode_til (datetime.datetime | Unset): sluttdato for undersøkelsen

                <engelsk>
                ending date of the investigation
                </engelsk>
            ekstern_identifikasjon (EksternIdentifikasjon | Unset): Identifikasjon av et objekt, ivaretatt av den ansvarlige
                leverandør inn til NADAG.
            representasjon_kvalitet (RepresentasjonKvalitet | Unset): Angir hva avgrensningen/polygonen for en geoteknisk
                undersøkelse fysisk representerer.
            opprettet_dato (datetime.datetime | Unset): Når objektet ble opprettet i database (Nadag)
            prosjekt_nr (str | Unset): Nummer på prosjekt benyttet for den geotekniske undersøkelsen
            opphav (str | Unset): referanse til opphavsmaterialet, kildematerialet, organisasjons/publiseringskilde
            unders_ø_kelse_å_r_antatt (int | Unset): Antatt år for gjennomføring av den geotekniske undersøkelsen. For
                største delen av de leverte dataene har det vært dårlig infomasjon i egenskapene for undersøkelseperiode og
                derfor utvides det med denne egenskapen. Årstallet her er hentet fra ulike kilder i leveransene og avhengig av
                hva for leveranser det er varierer usikkerheten på på det antatte årstallet.
            felt_unders (list[GeotekniskFeltUnders] | Unset):
            unders_pkt (list[GeotekniskBorehull] | Unset):
            har_tolkning (list[GeotekniskTolketPunkt] | Unset):
            har_dokument (list[GeotekniskDokument] | Unset):
    """

    identifikasjon: Identifikasjon | Unset = UNSET
    oppdateringsdato: datetime.datetime | Unset = UNSET
    beskrivelse: str | Unset = UNSET
    område: Polygon | Unset = UNSET
    oppdragsgiver: str | Unset = UNSET
    oppdragstaker: str | Unset = UNSET
    prosjekt_navn: str | Unset = UNSET
    unders_ø_kelse_periode_fra: datetime.datetime | Unset = UNSET
    sammensattområde: MultiPolygon | Unset = UNSET
    unders_ø_kelse_periode_til: datetime.datetime | Unset = UNSET
    ekstern_identifikasjon: EksternIdentifikasjon | Unset = UNSET
    representasjon_kvalitet: RepresentasjonKvalitet | Unset = UNSET
    opprettet_dato: datetime.datetime | Unset = UNSET
    prosjekt_nr: str | Unset = UNSET
    opphav: str | Unset = UNSET
    unders_ø_kelse_å_r_antatt: int | Unset = UNSET
    felt_unders: list[GeotekniskFeltUnders] | Unset = UNSET
    unders_pkt: list[GeotekniskBorehull] | Unset = UNSET
    har_tolkning: list[GeotekniskTolketPunkt] | Unset = UNSET
    har_dokument: list[GeotekniskDokument] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifikasjon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        oppdateringsdato: str | Unset = UNSET
        if not isinstance(self.oppdateringsdato, Unset):
            oppdateringsdato = self.oppdateringsdato.isoformat()

        beskrivelse = self.beskrivelse

        område: dict[str, Any] | Unset = UNSET
        if not isinstance(self.område, Unset):
            område = self.område.to_dict()

        oppdragsgiver = self.oppdragsgiver

        oppdragstaker = self.oppdragstaker

        prosjekt_navn = self.prosjekt_navn

        unders_ø_kelse_periode_fra: str | Unset = UNSET
        if not isinstance(self.unders_ø_kelse_periode_fra, Unset):
            unders_ø_kelse_periode_fra = self.unders_ø_kelse_periode_fra.isoformat()

        sammensattområde: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sammensattområde, Unset):
            sammensattområde = self.sammensattområde.to_dict()

        unders_ø_kelse_periode_til: str | Unset = UNSET
        if not isinstance(self.unders_ø_kelse_periode_til, Unset):
            unders_ø_kelse_periode_til = self.unders_ø_kelse_periode_til.isoformat()

        ekstern_identifikasjon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = self.ekstern_identifikasjon.to_dict()

        representasjon_kvalitet: str | Unset = UNSET
        if not isinstance(self.representasjon_kvalitet, Unset):
            representasjon_kvalitet = self.representasjon_kvalitet.value

        opprettet_dato: str | Unset = UNSET
        if not isinstance(self.opprettet_dato, Unset):
            opprettet_dato = self.opprettet_dato.isoformat()

        prosjekt_nr = self.prosjekt_nr

        opphav = self.opphav

        unders_ø_kelse_å_r_antatt = self.unders_ø_kelse_å_r_antatt

        felt_unders: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.felt_unders, Unset):
            felt_unders = []
            for felt_unders_item_data in self.felt_unders:
                felt_unders_item = felt_unders_item_data.to_dict()
                felt_unders.append(felt_unders_item)

        unders_pkt: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.unders_pkt, Unset):
            unders_pkt = []
            for unders_pkt_item_data in self.unders_pkt:
                unders_pkt_item = unders_pkt_item_data.to_dict()
                unders_pkt.append(unders_pkt_item)

        har_tolkning: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.har_tolkning, Unset):
            har_tolkning = []
            for har_tolkning_item_data in self.har_tolkning:
                har_tolkning_item = har_tolkning_item_data.to_dict()
                har_tolkning.append(har_tolkning_item)

        har_dokument: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.har_dokument, Unset):
            har_dokument = []
            for har_dokument_item_data in self.har_dokument:
                har_dokument_item = har_dokument_item_data.to_dict()
                har_dokument.append(har_dokument_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if identifikasjon is not UNSET:
            field_dict["identifikasjon"] = identifikasjon
        if oppdateringsdato is not UNSET:
            field_dict["oppdateringsdato"] = oppdateringsdato
        if beskrivelse is not UNSET:
            field_dict["beskrivelse"] = beskrivelse
        if område is not UNSET:
            field_dict["område"] = område
        if oppdragsgiver is not UNSET:
            field_dict["oppdragsgiver"] = oppdragsgiver
        if oppdragstaker is not UNSET:
            field_dict["oppdragstaker"] = oppdragstaker
        if prosjekt_navn is not UNSET:
            field_dict["prosjektNavn"] = prosjekt_navn
        if unders_ø_kelse_periode_fra is not UNSET:
            field_dict["undersøkelsePeriodeFra"] = unders_ø_kelse_periode_fra
        if sammensattområde is not UNSET:
            field_dict["sammensattområde"] = sammensattområde
        if unders_ø_kelse_periode_til is not UNSET:
            field_dict["undersøkelsePeriodeTil"] = unders_ø_kelse_periode_til
        if ekstern_identifikasjon is not UNSET:
            field_dict["eksternIdentifikasjon"] = ekstern_identifikasjon
        if representasjon_kvalitet is not UNSET:
            field_dict["representasjonKvalitet"] = representasjon_kvalitet
        if opprettet_dato is not UNSET:
            field_dict["opprettetDato"] = opprettet_dato
        if prosjekt_nr is not UNSET:
            field_dict["prosjektNr"] = prosjekt_nr
        if opphav is not UNSET:
            field_dict["opphav"] = opphav
        if unders_ø_kelse_å_r_antatt is not UNSET:
            field_dict["undersøkelseÅrAntatt"] = unders_ø_kelse_å_r_antatt
        if felt_unders is not UNSET:
            field_dict["feltUnders"] = felt_unders
        if unders_pkt is not UNSET:
            field_dict["undersPkt"] = unders_pkt
        if har_tolkning is not UNSET:
            field_dict["harTolkning"] = har_tolkning
        if har_dokument is not UNSET:
            field_dict["harDokument"] = har_dokument

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ekstern_identifikasjon import EksternIdentifikasjon
        from ..models.geoteknisk_borehull import GeotekniskBorehull
        from ..models.geoteknisk_dokument import GeotekniskDokument
        from ..models.geoteknisk_felt_unders import GeotekniskFeltUnders
        from ..models.geoteknisk_tolket_punkt import GeotekniskTolketPunkt
        from ..models.identifikasjon import Identifikasjon
        from ..models.multi_polygon import MultiPolygon
        from ..models.polygon import Polygon

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

        beskrivelse = d.pop("beskrivelse", UNSET)

        _område = d.pop("område", UNSET)
        område: Polygon | Unset
        if isinstance(_område, Unset):
            område = UNSET
        else:
            område = Polygon.from_dict(_område)

        oppdragsgiver = d.pop("oppdragsgiver", UNSET)

        oppdragstaker = d.pop("oppdragstaker", UNSET)

        prosjekt_navn = d.pop("prosjektNavn", UNSET)

        _unders_ø_kelse_periode_fra = d.pop("undersøkelsePeriodeFra", UNSET)
        unders_ø_kelse_periode_fra: datetime.datetime | Unset
        if isinstance(_unders_ø_kelse_periode_fra, Unset):
            unders_ø_kelse_periode_fra = UNSET
        else:
            unders_ø_kelse_periode_fra = isoparse(_unders_ø_kelse_periode_fra)

        _sammensattområde = d.pop("sammensattområde", UNSET)
        sammensattområde: MultiPolygon | Unset
        if isinstance(_sammensattområde, Unset):
            sammensattområde = UNSET
        else:
            sammensattområde = MultiPolygon.from_dict(_sammensattområde)

        _unders_ø_kelse_periode_til = d.pop("undersøkelsePeriodeTil", UNSET)
        unders_ø_kelse_periode_til: datetime.datetime | Unset
        if isinstance(_unders_ø_kelse_periode_til, Unset):
            unders_ø_kelse_periode_til = UNSET
        else:
            unders_ø_kelse_periode_til = isoparse(_unders_ø_kelse_periode_til)

        _ekstern_identifikasjon = d.pop("eksternIdentifikasjon", UNSET)
        ekstern_identifikasjon: EksternIdentifikasjon | Unset
        if isinstance(_ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = UNSET
        else:
            ekstern_identifikasjon = EksternIdentifikasjon.from_dict(_ekstern_identifikasjon)

        _representasjon_kvalitet = d.pop("representasjonKvalitet", UNSET)
        representasjon_kvalitet: RepresentasjonKvalitet | Unset
        if isinstance(_representasjon_kvalitet, Unset):
            representasjon_kvalitet = UNSET
        else:
            representasjon_kvalitet = RepresentasjonKvalitet(_representasjon_kvalitet)

        _opprettet_dato = d.pop("opprettetDato", UNSET)
        opprettet_dato: datetime.datetime | Unset
        if isinstance(_opprettet_dato, Unset):
            opprettet_dato = UNSET
        else:
            opprettet_dato = isoparse(_opprettet_dato)

        prosjekt_nr = d.pop("prosjektNr", UNSET)

        opphav = d.pop("opphav", UNSET)

        unders_ø_kelse_å_r_antatt = d.pop("undersøkelseÅrAntatt", UNSET)

        _felt_unders = d.pop("feltUnders", UNSET)
        felt_unders: list[GeotekniskFeltUnders] | Unset = UNSET
        if _felt_unders is not UNSET:
            felt_unders = []
            for felt_unders_item_data in _felt_unders:
                felt_unders_item = GeotekniskFeltUnders.from_dict(felt_unders_item_data)

                felt_unders.append(felt_unders_item)

        _unders_pkt = d.pop("undersPkt", UNSET)
        unders_pkt: list[GeotekniskBorehull] | Unset = UNSET
        if _unders_pkt is not UNSET:
            unders_pkt = []
            for unders_pkt_item_data in _unders_pkt:
                unders_pkt_item = GeotekniskBorehull.from_dict(unders_pkt_item_data)

                unders_pkt.append(unders_pkt_item)

        _har_tolkning = d.pop("harTolkning", UNSET)
        har_tolkning: list[GeotekniskTolketPunkt] | Unset = UNSET
        if _har_tolkning is not UNSET:
            har_tolkning = []
            for har_tolkning_item_data in _har_tolkning:
                har_tolkning_item = GeotekniskTolketPunkt.from_dict(har_tolkning_item_data)

                har_tolkning.append(har_tolkning_item)

        _har_dokument = d.pop("harDokument", UNSET)
        har_dokument: list[GeotekniskDokument] | Unset = UNSET
        if _har_dokument is not UNSET:
            har_dokument = []
            for har_dokument_item_data in _har_dokument:
                har_dokument_item = GeotekniskDokument.from_dict(har_dokument_item_data)

                har_dokument.append(har_dokument_item)

        geoteknisk_unders = cls(
            identifikasjon=identifikasjon,
            oppdateringsdato=oppdateringsdato,
            beskrivelse=beskrivelse,
            område=område,
            oppdragsgiver=oppdragsgiver,
            oppdragstaker=oppdragstaker,
            prosjekt_navn=prosjekt_navn,
            unders_ø_kelse_periode_fra=unders_ø_kelse_periode_fra,
            sammensattområde=sammensattområde,
            unders_ø_kelse_periode_til=unders_ø_kelse_periode_til,
            ekstern_identifikasjon=ekstern_identifikasjon,
            representasjon_kvalitet=representasjon_kvalitet,
            opprettet_dato=opprettet_dato,
            prosjekt_nr=prosjekt_nr,
            opphav=opphav,
            unders_ø_kelse_å_r_antatt=unders_ø_kelse_å_r_antatt,
            felt_unders=felt_unders,
            unders_pkt=unders_pkt,
            har_tolkning=har_tolkning,
            har_dokument=har_dokument,
        )

        geoteknisk_unders.additional_properties = d
        return geoteknisk_unders

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
