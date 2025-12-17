import re
import dateutil.parser as parser
from raw_docx.raw_docx import RawDocx
from usdm4.builder.builder import Builder
from usdm4_m11.import_.m11_utility import table_get_row
from simple_error_log.errors import Errors


class M11TitlePage:
    def __init__(self, raw_docx: RawDocx, builder: Builder, errors: Errors):
        self._builder = builder
        self._errors = errors
        self._raw_docx = raw_docx
        self._address_service = None  # Will need to be addressed
        self._sections = []
        self.sponosr_confidentiality = None
        self.acronym = None
        self.full_title = None
        self.sponsor_protocol_identifier = None
        self.original_protocol = None
        self.version_number = None
        self.version_date = None
        self.amendment_identifier = None
        self.amendment_scope = None
        self.amendment_details = None
        self.compound_codes = None
        self.compound_names = None
        self.trial_phase_raw = None
        self.trial_phase = None
        self.short_title = None
        self.sponsor_name_and_address = None
        self.sponsor_name = None
        self.sponsor_address = None
        self.regulatory_agency_identifiers = None
        self.sponsor_approval_date = None
        self.manufacturer_name_and_address = None
        self.sponsor_signatory = None
        self.medical_expert_contact = None
        self.sae_reporting_method = None

    async def process(self):
        table = self._title_table()
        if table:
            table.replace_class("ich-m11-table", "ich-m11-title-page-table")
            self.sponosr_confidentiality = table_get_row(
                table, "Sponsor Confidentiality"
            )
            self.full_title = table_get_row(table, "Full Title")
            self.acronym = table_get_row(table, "Acronym")
            self.sponsor_protocol_identifier = table_get_row(
                table, "Sponsor Protocol Identifier"
            )
            self.original_protocol = table_get_row(table, "Original Protocol")
            self.version_number = table_get_row(table, "Version Number")
            self.version_date = self._get_protocol_date(table)
            self.amendment_identifier = table_get_row(table, "Amendment Identifier")
            self.amendment_scope = table_get_row(table, "Amendment Scope")
            self.amendment_details = table_get_row(table, "Amendment Details")
            self.compound_codes = table_get_row(table, "Compound Code")
            self.compound_names = table_get_row(table, "Compound Name")
            self.trial_phase_raw = table_get_row(table, "Trial Phase")
            self.trial_phase = self._get_phase()
            self.short_title = table_get_row(table, "Short Title")
            self.sponsor_name_and_address = table_get_row(
                table, "Sponsor Name and Address"
            )
            # Simplified address handling since we don't have the address service
            self.sponsor_name, self.sponsor_address = (
                self._get_sponsor_name_and_address_simple()
            )
            self.regulatory_agency_identifiers = table_get_row(
                table, "Regulatory Agency Identifier Number(s)"
            )
            self.sponsor_approval_date = self._get_sponsor_approval_date(table)
            self.manufacturer_name_and_address = table_get_row(table, "Manufacturer")
            self.sponsor_signatory = table_get_row(table, "Sponsor Signatory")
            self.medical_expert_contact = table_get_row(table, "Medical Expert")
            self.sae_reporting_method = table_get_row(table, "SAE Reporting")
            self.study_name = self._get_study_name()

    def extra(self):
        return {
            "sponsor_confidentiality": self.sponosr_confidentiality,
            "compound_codes": self.compound_codes,
            "compound_names": self.compound_names,
            "amendment_identifier": self.amendment_identifier,
            "amendment_scope": self.amendment_scope,
            "amendment_details": self.amendment_details,
            "sponsor_name_and_address": self.sponsor_name_and_address,
            "original_protocol": self.original_protocol,
            "regulatory_agency_identifiers": self.regulatory_agency_identifiers,
            "manufacturer_name_and_address": self.manufacturer_name_and_address,
            "sponsor_signatory": self.sponsor_signatory,
            "medical_expert_contact": self.medical_expert_contact,
            "sae_reporting_method": self.sae_reporting_method,
            "sponsor_approval_date": self.sponsor_approval_date,
        }

    def _get_study_name(self):
        items = [self.acronym, self.sponsor_protocol_identifier, self.compound_codes]
        for item in items:
            if item:
                name = re.sub(r"[\W_]+", "", item.upper())
                self._errors.info(f"Study name set to '{name}'")
                return name
        return ""

    def _get_sponsor_name_and_address_simple(self):
        """Simplified version of _get_sponsor_name_and_address without using the address service"""
        name = "[Sponsor Name]"
        parts = (
            self.sponsor_name_and_address.split("\n")
            if self.sponsor_name_and_address
            else []
        )
        params = {
            "lines": [],
            "city": "",
            "district": "",
            "state": "",
            "postalCode": "",
            "country": None,
        }
        if len(parts) > 0:
            name = parts[0].strip()
            self._errors.info(f"Sponsor name set to '{name}'")
        if len(parts) > 1:
            # Simple address parsing - just store the address lines
            params["lines"] = [part.strip() for part in parts[1:]]
            # Try to extract country from the last line
            if len(parts) > 2:
                last_line = parts[-1].strip()
                country_code = self._builder.iso3166_code(last_line)
                if country_code:
                    params["country"] = country_code

        self._errors.info(f"Name and address result '{name}', '{params}'")
        return name, params

    async def _get_sponsor_name_and_address(self):
        """Original method kept for reference but not used"""
        name = "[Sponsor Name]"
        parts = self.sponsor_name_and_address.split("\n")
        params = {
            "lines": [],
            "city": "",
            "district": "",
            "state": "",
            "postalCode": "",
            "country": None,
        }
        if len(parts) > 0:
            name = parts[0].strip()
            self._errors.info(f"Sponsor name set to '{name}'")
        if len(parts) > 1:
            self._errors.info(f"Processing address {self.sponsor_name_and_address}")
            tmp_address = (" ").join([x.strip() for x in parts[1:]])
            # This would use the address service which we don't have
            # results = await self._address_service.parser(tmp_address)
            results = []  # Placeholder
            self._errors.info(
                f"Address service result '{tmp_address}' returned {results}"
            )
            if "error" in results:
                self._errors.error(f"Error with address server: {results['error']}")
            else:
                for result in results:
                    if result["label"] == "country":
                        value = self._preserve_original(parts[1:], result["value"])
                        params["country"] = self._builder.iso3166_code(value)
                    elif result["label"] == "postcode":
                        params["postalCode"] = self._preserve_original(
                            parts[1:], result["value"]
                        )
                    elif result["label"] in ["city", "state"]:
                        params[result["label"]] = self._preserve_original(
                            parts[1:], result["value"]
                        )
        self._errors.info(f"Name and address result '{name}', '{params}'")
        return name, params

    def _get_sponsor_approval_date(self, table):
        return self._get_date(table, "Sponsor Approval")

    def _get_protocol_date(self, table):
        return self._get_date(table, "Version Date")

    def _get_date(self, table, text):
        try:
            date_text = table_get_row(table, text)
            if date_text:
                date = parser.parse(date_text)
                return date
            else:
                return None
        except Exception as e:
            self._errors.exception(
                f"Exception raised during date processing for '{text}'", e
            )
            return None

    def _get_phase(self):
        phase_map = [
            (
                ["0", "PRE-CLINICAL", "PRE CLINICAL"],
                {"code": "C54721", "decode": "Phase 0 Trial"},
            ),
            (["1", "I"], {"code": "C15600", "decode": "Phase I Trial"}),
            (["1-2"], {"code": "C15693", "decode": "Phase I/II Trial"}),
            (["1/2"], {"code": "C15693", "decode": "Phase I/II Trial"}),
            (["1/2/3"], {"code": "C198366", "decode": "Phase I/II/III Trial"}),
            (["1/3"], {"code": "C198367", "decode": "Phase I/III Trial"}),
            (["1A", "IA"], {"code": "C199990", "decode": "Phase Ia Trial"}),
            (["1B", "IB"], {"code": "C199989", "decode": "Phase Ib Trial"}),
            (["2", "II"], {"code": "C15601", "decode": "Phase II Trial"}),
            (["2-3", "II-III"], {"code": "C15694", "decode": "Phase II/III Trial"}),
            (["2A", "IIA"], {"code": "C49686", "decode": "Phase IIa Trial"}),
            (["2B", "IIB"], {"code": "C49688", "decode": "Phase IIb Trial"}),
            (["3", "III"], {"code": "C15602", "decode": "Phase III Trial"}),
            (["3A", "IIIA"], {"code": "C49687", "decode": "Phase IIIa Trial"}),
            (["3B", "IIIB"], {"code": "C49689", "decode": "Phase IIIb Trial"}),
            (["4", "IV"], {"code": "C15603", "decode": "Phase IV Trial"}),
            (["5", "V"], {"code": "C47865", "decode": "Phase V Trial"}),
        ]
        phase = (
            self.trial_phase_raw.upper().replace("PHASE", "").strip()
            if self.trial_phase_raw
            else ""
        )
        # print(f"PHASE1: {phase}")
        for tuple in phase_map:
            # print(f"PHASE2: {tuple}")
            if phase in tuple[0]:
                entry = tuple[1]
                cdisc_phase_code = self._builder.cdisc_code(
                    entry["code"],
                    entry["decode"],
                )
                self._errors.info(
                    f"Trial phase '{phase}' decoded as '{entry['code']}', '{entry['decode']}'"
                )
                return self._builder.alias_code(cdisc_phase_code)
        cdisc_phase_code = self._builder.cdisc_code(
            "C48660",
            "[Trial Phase] Not Applicable",
        )
        self._errors.warning(f"Trial phase '{phase}' not decoded")
        return self._builder.alias_code(cdisc_phase_code)

    def _title_table(self):
        section = self._raw_docx.target_document.section_by_ordinal(1)
        for table in section.tables():
            title = table_get_row(table, "Full Title")
            if title:
                self._errors.debug("Found M11 title page table")
                return table
        self._errors.warning("Cannot locate M11 title page table!")
        return None

    def _preserve_original(self, original_parts, value):
        for part in original_parts:
            for item in re.split(r"[,\s]+", part):
                if item.upper() == value.upper():
                    return item
        return value
