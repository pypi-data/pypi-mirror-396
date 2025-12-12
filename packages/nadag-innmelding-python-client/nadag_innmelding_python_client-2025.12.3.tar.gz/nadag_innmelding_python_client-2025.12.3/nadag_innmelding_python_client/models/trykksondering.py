from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.nedpressings_kapasitet import NedpressingsKapasitet
from ..models.sonde_kvalitets_klasse import SondeKvalitetsKlasse
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dissipasjon_data import DissipasjonData
    from ..models.identifikasjon import Identifikasjon
    from ..models.poretrykk_data_insitu import PoretrykkDataInsitu
    from ..models.trykksondering_data import TrykksonderingData


T = TypeVar("T", bound="Trykksondering")


@_attrs_define
class Trykksondering:
    """penetrasjon av en trykksonde på enden av en serie med sylindriske trykksonderingsstenger ned i grunnen med konstant
    hastighet, brukes for å bestemme lagdeling og jordart i løsmasser, samt mekaniske egenskaper for
    jorden<engelsk>penetration of a probe at the end of a series with cylindrical rods into the ground at the constant
    rate of penetration, used to determine stratification and soil type, together with mechanical properties of the
    soil</engelsk>

        Attributes:
            json_type (Literal['Trykksondering'] | Unset):
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
            alpha (float | Unset): arealforhold for trykksonde for korreksjon av målt spissmotstand for
                poretrykkseffekter<engelsk>area ratio for CPT probe for correction of measured cone resistance for pore pressure
                effects</engelsk>
            cpt_korreksjons_faktor (float | Unset): øvrige faktorer for korreksjon av trykksonderingsdata, for eksempel
                korreksjon av målt sidefriksjon<engelsk>other factors for correction of CPT data, for example correction of
                measured sleeve friction</engelsk>
            filter_type (str | Unset): type filter for måling av poretrykk (porøst filter, ferdigmettet,
                spaltefilter)<engelsk>type of filter for measurement of pore pressure (porous filter, pre-saturated filter, slot
                filter)</engelsk>
            initiell_spissmotstand (float | Unset): referanseverdi for spissmotstand ved start av måling (eksempel ved start
                dissipasjonstest) [kPa] <engelsk>reference value cone resistance at the start of the test (e.g. at the start of
                a dissipation test)</engelsk>
            metnings_medium (str | Unset): medium som benyttes for metting av målesystem for poretrykk<engelsk>medium used
                for saturation of measuring system for pore pressure</engelsk>
            nedpressings_kapasitet (NedpressingsKapasitet | Unset): oversikt over lastkapasiteter for vanlige trykksonder i
                CPT/CPTU <engelsk>overview of load capacity for common CPT/CPTU probes</engelsk>
            nedpressnings_hastighet (float | Unset): nedpressingshastighet ved penetrasjon av trykksonderingsstenger (2 cm
                per sekund)<engelsk>rate of penetration for rod system (2 cm per second)</engelsk>
            nullpunkts_korreksjon (float | Unset): korreksjon for registrert nullpunktsavvik før og etter sondering [MPa]
                <engelsk>correction for recorded zero load drift before and after sounding</engelsk>
            r_ø_r_kappe_korreksjons_faktor (float | Unset): korreksjonsfaktor for bruk av friksjonsreduksjonsring
                <engelsk>correction factor for use of friction reducer</engelsk>
            sidefriksjon_korreksjon (float | Unset): korreksjon av målt sidefriksjon på grunn av
                poretrykkseffekter<engelsk>correction of measured sleeve friction due to pore pressure effects</engelsk>
            sonde_identifikasjon (str | Unset): identifikasjon av trykksonde ved hjelp av ID-nummer <engelsk>identification
                of probe by an ID-number</engelsk>
            sonde_kalibrering_dato (datetime.datetime | Unset): dato for kalibrering av trykksonde, oppgis på
                kalibreringssertifikat<engelsk>date for calibration of probe, given on the calibration certificate</engelsk>
            sonde_kvalitet_klasse (SondeKvalitetsKlasse | Unset): oversikt over aktuelle kvalitetsklasser
                (Anvendelsesklasser) for CPT/CPTU<engelsk>overview of possible Application classes for CPT/CPTU</engelsk>
            spiss_korreksjon_faktor (float | Unset): korreksjonsfaktor for trykksonde ved korreksjon av målt spissmotstand
                for poretrykkseffekter<engelsk>correction factor for measured cone resistance for pore pressure
                effects</engelsk>
            spiss_type (str | Unset): type trykksonde, avhengig av størrelse og instrumentering<engelsk>type of probe,
                depending on size and instrumentation</engelsk>
            atmosferisk_trykk_korreksjon (float | Unset): <engelsk>Gets or sets the atmospheric pressure correction [MPa].
                @value The atmospheric pressure correction.</engelsk>
            hylse_radie_korreksjon (float | Unset): <engelsk>Gets or sets the sleeve distance correction [m].
                @value The sleeve distance correction.</engelsk>
            in_situ_poretrykk_observasjon (list[PoretrykkDataInsitu] | Unset):
            trykksondering_observasjon (list[TrykksonderingData] | Unset):
            dissipasjon_observasjon (list[DissipasjonData] | Unset):
    """

    json_type: Literal["Trykksondering"] | Unset = UNSET
    identifikasjon: Identifikasjon | Unset = UNSET
    fra_borlengde: float | Unset = UNSET
    til_borlengde: float | Unset = UNSET
    insitu_test_start_tidspunkt: datetime.datetime | Unset = UNSET
    insitu_test_slutt_tidspunkt: datetime.datetime | Unset = UNSET
    alpha: float | Unset = UNSET
    cpt_korreksjons_faktor: float | Unset = UNSET
    filter_type: str | Unset = UNSET
    initiell_spissmotstand: float | Unset = UNSET
    metnings_medium: str | Unset = UNSET
    nedpressings_kapasitet: NedpressingsKapasitet | Unset = UNSET
    nedpressnings_hastighet: float | Unset = UNSET
    nullpunkts_korreksjon: float | Unset = UNSET
    r_ø_r_kappe_korreksjons_faktor: float | Unset = UNSET
    sidefriksjon_korreksjon: float | Unset = UNSET
    sonde_identifikasjon: str | Unset = UNSET
    sonde_kalibrering_dato: datetime.datetime | Unset = UNSET
    sonde_kvalitet_klasse: SondeKvalitetsKlasse | Unset = UNSET
    spiss_korreksjon_faktor: float | Unset = UNSET
    spiss_type: str | Unset = UNSET
    atmosferisk_trykk_korreksjon: float | Unset = UNSET
    hylse_radie_korreksjon: float | Unset = UNSET
    in_situ_poretrykk_observasjon: list[PoretrykkDataInsitu] | Unset = UNSET
    trykksondering_observasjon: list[TrykksonderingData] | Unset = UNSET
    dissipasjon_observasjon: list[DissipasjonData] | Unset = UNSET
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

        alpha = self.alpha

        cpt_korreksjons_faktor = self.cpt_korreksjons_faktor

        filter_type = self.filter_type

        initiell_spissmotstand = self.initiell_spissmotstand

        metnings_medium = self.metnings_medium

        nedpressings_kapasitet: str | Unset = UNSET
        if not isinstance(self.nedpressings_kapasitet, Unset):
            nedpressings_kapasitet = self.nedpressings_kapasitet.value

        nedpressnings_hastighet = self.nedpressnings_hastighet

        nullpunkts_korreksjon = self.nullpunkts_korreksjon

        r_ø_r_kappe_korreksjons_faktor = self.r_ø_r_kappe_korreksjons_faktor

        sidefriksjon_korreksjon = self.sidefriksjon_korreksjon

        sonde_identifikasjon = self.sonde_identifikasjon

        sonde_kalibrering_dato: str | Unset = UNSET
        if not isinstance(self.sonde_kalibrering_dato, Unset):
            sonde_kalibrering_dato = self.sonde_kalibrering_dato.isoformat()

        sonde_kvalitet_klasse: str | Unset = UNSET
        if not isinstance(self.sonde_kvalitet_klasse, Unset):
            sonde_kvalitet_klasse = self.sonde_kvalitet_klasse.value

        spiss_korreksjon_faktor = self.spiss_korreksjon_faktor

        spiss_type = self.spiss_type

        atmosferisk_trykk_korreksjon = self.atmosferisk_trykk_korreksjon

        hylse_radie_korreksjon = self.hylse_radie_korreksjon

        in_situ_poretrykk_observasjon: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.in_situ_poretrykk_observasjon, Unset):
            in_situ_poretrykk_observasjon = []
            for in_situ_poretrykk_observasjon_item_data in self.in_situ_poretrykk_observasjon:
                in_situ_poretrykk_observasjon_item = in_situ_poretrykk_observasjon_item_data.to_dict()
                in_situ_poretrykk_observasjon.append(in_situ_poretrykk_observasjon_item)

        trykksondering_observasjon: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.trykksondering_observasjon, Unset):
            trykksondering_observasjon = []
            for trykksondering_observasjon_item_data in self.trykksondering_observasjon:
                trykksondering_observasjon_item = trykksondering_observasjon_item_data.to_dict()
                trykksondering_observasjon.append(trykksondering_observasjon_item)

        dissipasjon_observasjon: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.dissipasjon_observasjon, Unset):
            dissipasjon_observasjon = []
            for dissipasjon_observasjon_item_data in self.dissipasjon_observasjon:
                dissipasjon_observasjon_item = dissipasjon_observasjon_item_data.to_dict()
                dissipasjon_observasjon.append(dissipasjon_observasjon_item)

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
        if alpha is not UNSET:
            field_dict["alpha"] = alpha
        if cpt_korreksjons_faktor is not UNSET:
            field_dict["cptKorreksjonsFaktor"] = cpt_korreksjons_faktor
        if filter_type is not UNSET:
            field_dict["filterType"] = filter_type
        if initiell_spissmotstand is not UNSET:
            field_dict["initiellSpissmotstand"] = initiell_spissmotstand
        if metnings_medium is not UNSET:
            field_dict["metningsMedium"] = metnings_medium
        if nedpressings_kapasitet is not UNSET:
            field_dict["nedpressingsKapasitet"] = nedpressings_kapasitet
        if nedpressnings_hastighet is not UNSET:
            field_dict["nedpressningsHastighet"] = nedpressnings_hastighet
        if nullpunkts_korreksjon is not UNSET:
            field_dict["nullpunktsKorreksjon"] = nullpunkts_korreksjon
        if r_ø_r_kappe_korreksjons_faktor is not UNSET:
            field_dict["rørKappeKorreksjonsFaktor"] = r_ø_r_kappe_korreksjons_faktor
        if sidefriksjon_korreksjon is not UNSET:
            field_dict["sidefriksjonKorreksjon"] = sidefriksjon_korreksjon
        if sonde_identifikasjon is not UNSET:
            field_dict["sondeIdentifikasjon"] = sonde_identifikasjon
        if sonde_kalibrering_dato is not UNSET:
            field_dict["sondeKalibreringDato"] = sonde_kalibrering_dato
        if sonde_kvalitet_klasse is not UNSET:
            field_dict["sondeKvalitetKlasse"] = sonde_kvalitet_klasse
        if spiss_korreksjon_faktor is not UNSET:
            field_dict["spissKorreksjonFaktor"] = spiss_korreksjon_faktor
        if spiss_type is not UNSET:
            field_dict["spissType"] = spiss_type
        if atmosferisk_trykk_korreksjon is not UNSET:
            field_dict["atmosferiskTrykkKorreksjon"] = atmosferisk_trykk_korreksjon
        if hylse_radie_korreksjon is not UNSET:
            field_dict["hylseRadieKorreksjon"] = hylse_radie_korreksjon
        if in_situ_poretrykk_observasjon is not UNSET:
            field_dict["inSituPoretrykkObservasjon"] = in_situ_poretrykk_observasjon
        if trykksondering_observasjon is not UNSET:
            field_dict["trykksonderingObservasjon"] = trykksondering_observasjon
        if dissipasjon_observasjon is not UNSET:
            field_dict["dissipasjonObservasjon"] = dissipasjon_observasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dissipasjon_data import DissipasjonData
        from ..models.identifikasjon import Identifikasjon
        from ..models.poretrykk_data_insitu import PoretrykkDataInsitu
        from ..models.trykksondering_data import TrykksonderingData

        d = dict(src_dict)
        json_type = cast(Literal["Trykksondering"] | Unset, d.pop("jsonType", UNSET))
        if json_type != "Trykksondering" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'Trykksondering', got '{json_type}'")

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

        alpha = d.pop("alpha", UNSET)

        cpt_korreksjons_faktor = d.pop("cptKorreksjonsFaktor", UNSET)

        filter_type = d.pop("filterType", UNSET)

        initiell_spissmotstand = d.pop("initiellSpissmotstand", UNSET)

        metnings_medium = d.pop("metningsMedium", UNSET)

        _nedpressings_kapasitet = d.pop("nedpressingsKapasitet", UNSET)
        nedpressings_kapasitet: NedpressingsKapasitet | Unset
        if isinstance(_nedpressings_kapasitet, Unset):
            nedpressings_kapasitet = UNSET
        else:
            nedpressings_kapasitet = NedpressingsKapasitet(_nedpressings_kapasitet)

        nedpressnings_hastighet = d.pop("nedpressningsHastighet", UNSET)

        nullpunkts_korreksjon = d.pop("nullpunktsKorreksjon", UNSET)

        r_ø_r_kappe_korreksjons_faktor = d.pop("rørKappeKorreksjonsFaktor", UNSET)

        sidefriksjon_korreksjon = d.pop("sidefriksjonKorreksjon", UNSET)

        sonde_identifikasjon = d.pop("sondeIdentifikasjon", UNSET)

        _sonde_kalibrering_dato = d.pop("sondeKalibreringDato", UNSET)
        sonde_kalibrering_dato: datetime.datetime | Unset
        if isinstance(_sonde_kalibrering_dato, Unset):
            sonde_kalibrering_dato = UNSET
        else:
            sonde_kalibrering_dato = isoparse(_sonde_kalibrering_dato)

        _sonde_kvalitet_klasse = d.pop("sondeKvalitetKlasse", UNSET)
        sonde_kvalitet_klasse: SondeKvalitetsKlasse | Unset
        if isinstance(_sonde_kvalitet_klasse, Unset):
            sonde_kvalitet_klasse = UNSET
        else:
            sonde_kvalitet_klasse = SondeKvalitetsKlasse(_sonde_kvalitet_klasse)

        spiss_korreksjon_faktor = d.pop("spissKorreksjonFaktor", UNSET)

        spiss_type = d.pop("spissType", UNSET)

        atmosferisk_trykk_korreksjon = d.pop("atmosferiskTrykkKorreksjon", UNSET)

        hylse_radie_korreksjon = d.pop("hylseRadieKorreksjon", UNSET)

        _in_situ_poretrykk_observasjon = d.pop("inSituPoretrykkObservasjon", UNSET)
        in_situ_poretrykk_observasjon: list[PoretrykkDataInsitu] | Unset = UNSET
        if _in_situ_poretrykk_observasjon is not UNSET:
            in_situ_poretrykk_observasjon = []
            for in_situ_poretrykk_observasjon_item_data in _in_situ_poretrykk_observasjon:
                in_situ_poretrykk_observasjon_item = PoretrykkDataInsitu.from_dict(
                    in_situ_poretrykk_observasjon_item_data
                )

                in_situ_poretrykk_observasjon.append(in_situ_poretrykk_observasjon_item)

        _trykksondering_observasjon = d.pop("trykksonderingObservasjon", UNSET)
        trykksondering_observasjon: list[TrykksonderingData] | Unset = UNSET
        if _trykksondering_observasjon is not UNSET:
            trykksondering_observasjon = []
            for trykksondering_observasjon_item_data in _trykksondering_observasjon:
                trykksondering_observasjon_item = TrykksonderingData.from_dict(trykksondering_observasjon_item_data)

                trykksondering_observasjon.append(trykksondering_observasjon_item)

        _dissipasjon_observasjon = d.pop("dissipasjonObservasjon", UNSET)
        dissipasjon_observasjon: list[DissipasjonData] | Unset = UNSET
        if _dissipasjon_observasjon is not UNSET:
            dissipasjon_observasjon = []
            for dissipasjon_observasjon_item_data in _dissipasjon_observasjon:
                dissipasjon_observasjon_item = DissipasjonData.from_dict(dissipasjon_observasjon_item_data)

                dissipasjon_observasjon.append(dissipasjon_observasjon_item)

        trykksondering = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            insitu_test_start_tidspunkt=insitu_test_start_tidspunkt,
            insitu_test_slutt_tidspunkt=insitu_test_slutt_tidspunkt,
            alpha=alpha,
            cpt_korreksjons_faktor=cpt_korreksjons_faktor,
            filter_type=filter_type,
            initiell_spissmotstand=initiell_spissmotstand,
            metnings_medium=metnings_medium,
            nedpressings_kapasitet=nedpressings_kapasitet,
            nedpressnings_hastighet=nedpressnings_hastighet,
            nullpunkts_korreksjon=nullpunkts_korreksjon,
            r_ø_r_kappe_korreksjons_faktor=r_ø_r_kappe_korreksjons_faktor,
            sidefriksjon_korreksjon=sidefriksjon_korreksjon,
            sonde_identifikasjon=sonde_identifikasjon,
            sonde_kalibrering_dato=sonde_kalibrering_dato,
            sonde_kvalitet_klasse=sonde_kvalitet_klasse,
            spiss_korreksjon_faktor=spiss_korreksjon_faktor,
            spiss_type=spiss_type,
            atmosferisk_trykk_korreksjon=atmosferisk_trykk_korreksjon,
            hylse_radie_korreksjon=hylse_radie_korreksjon,
            in_situ_poretrykk_observasjon=in_situ_poretrykk_observasjon,
            trykksondering_observasjon=trykksondering_observasjon,
            dissipasjon_observasjon=dissipasjon_observasjon,
        )

        trykksondering.additional_properties = d
        return trykksondering

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
