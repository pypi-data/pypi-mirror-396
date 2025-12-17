import re
from raw_docx.raw_docx import RawDocx, RawTable, RawSection
from usdm4_m11.import_.extract.utility import table_get_row, section_get_para
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class TitlePage:
    MODULE = "usdm4_m11.import_.title_page.TitlePage"

    def __init__(self, raw_docx: RawDocx, errors: Errors):
        self._raw_docx = raw_docx
        self._sections = self._raw_docx.target_document.sections
        self._errors = errors

    def process(self):
        try:
            # for i, x in enumerate(self._sections[0:5]):
            #     print(f"SECTION {i}: {x.to_html()}\n\n")
            if table := self._title_table():
                table.replace_class("raw-docx-table", "ich-m11-title-page-table")
                return self._process_item(table)
            elif section := self._title_section():
                return self._process_item(section)
            else:
                self._errors.error(
                    "Failed to find the M11 title page content in the document",
                    KlassMethodLocation(self.MODULE, "process"),
                )
                return None
        except Exception as e:
            self._errors.exception(
                "Exception raised during title page processing",
                e,
                KlassMethodLocation(self.MODULE, "process"),
            )
            return None

    def _process_item(self, item: RawTable | RawSection):
        name_and_address = self._get_field_value(item, "Sponsor Name")
        address = self._get_sponsor_address_simple(name_and_address)
        sponsor = self._get_sponsor_name(name_and_address)
        acronym = self._get_field_value(item, "Acronym")
        identifier = self._get_field_value(item, "Sponsor Protocol Identifier")
        # print(f"IDENTIFIER: {identifier}")
        compund_code = self._get_field_value(item, "Compound Code")
        reg_identifiers = self._get_field_value(
            item, "Regulatory Agency Identifier Number(s)"
        )
        result = {
            "identification": {
                "titles": {
                    "official": self._get_field_value(item, "Full Title"),
                    "acronym": acronym,
                    "brief": self._get_field_value(item, "Short Title"),
                },
                "identifiers": [
                    {
                        "identifier": identifier,
                        "scope": {
                            "non_standard": {
                                "type": "pharma",
                                "description": "The sponsor organization",
                                "label": sponsor,
                                "identifier": "UNKNOWN",
                                "identifierScheme": "UNKNOWN",
                                "legalAddress": address,
                            }
                        },
                    }
                ],
            },
            "compounds": {
                "compound_codes": compund_code,
                "compound_names": self._get_field_value(item, "Compound Name"),
            },
            "amendments_summary": {
                "amendment_identifier": self._get_field_value(
                    item, "Amendment Identifier"
                ),
                "amendment_scope": self._get_field_value(item, "Amendment Scope"),
                "amendment_details": self._get_field_value(item, "Amendment Details"),
            },
            "study_design": {
                "label": "Study Design 1",
                "rationale": "Not set",
                "trial_phase": self._get_field_value(item, "Trial Phase"),
            },
            "study": {
                "sponsor_approval_date": self._get_sponsor_approval_date(item),
                "version_date": self._get_protocol_date(item),
                "version": self._get_field_value(item, "Version Number"),
                "rationale": "Not set",
                "name": {
                    "acronym": acronym,
                    "identifier": identifier,
                    "compound_code": compund_code,
                },
                "confidentiality": self._get_field_value(
                    item, "Sponsor Confidentiality Statement"
                ),
                "original_protocol": self._get_field_value(item, "Original Protocol"),
            },
            "other": {
                # "confidentiality": self._get_field_value(
                #     item, "Sponsor Confidentiality Statement"
                # ),
                "regulatory_agency_identifiers": reg_identifiers,
            },
            # self.manufacturer_name_and_address = table_get_row(table, "Manufacturer")
            # self.sponsor_signatory = table_get_row(table, "Sponsor Signatory")
            # self.medical_expert_contact = table_get_row(table, "Medical Expert")
            # self.sae_reporting_method = table_get_row(table, "SAE Reporting")
        }
        extracted_reg_identifiers = self._get_regulatory_identifiers(reg_identifiers)
        if extracted_reg_identifiers["nct"]:
            identifier = {
                "identifier": extracted_reg_identifiers["nct"][0],
                "scope": {
                    "standard": "ct.gov",
                },
            }
            result["identification"]["identifiers"].append(identifier)
        if extracted_reg_identifiers["ind"]:
            identifier = {
                "identifier": extracted_reg_identifiers["ind"][0],
                "scope": {
                    "standard": "fda",
                },
            }
            result["identification"]["identifiers"].append(identifier)
        return result

    def _get_field_value(self, item: RawTable | RawSection, text: str) -> str:
        return (
            table_get_row(item, text)
            if isinstance(item, RawTable)
            else section_get_para(item, text)
        )

    def _get_sponsor_approval_date(self, item: RawTable | RawSection):
        return self._get_date(item, "Sponsor Approval")

    def _get_protocol_date(self, item: RawTable | RawSection):
        return self._get_date(item, "Version Date")

    def _get_date(self, item: RawSection | RawTable, text):
        try:
            date_text = (
                table_get_row(item, text)
                if isinstance(item, RawTable)
                else section_get_para(item, text)
            )
            if date_text:
                return date_text.strip()
            else:
                return None
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_get_date")
            self._errors.exception(
                f"Exception raised during date processing for '{text}'", e, location
            )
            return None

    def _get_regulatory_identifiers(self, text: str) -> dict:
        if not text:
            return {"nct": [], "ind": []}

        # Pattern for NCT identifiers: NCT followed by exactly 8 digits
        nct_pattern = r"\bNCT\d{8}\b"

        # Multiple patterns for IND identifiers:
        # 1. IND followed directly by 6 digits (original format)
        # 2. IND followed by whitespace then 6 digits
        # 3. Title containing "IND" followed by space/colon then 6 digits
        ind_patterns = [
            r"\bIND\d{6}\b",  # IND123456
            r"\bIND\s+(\d{6})\b",  # IND 123456
            r"IND\s*\w*[\s:]+(\d{6})\b",  # Title with IND: 123456 or IND Number: 123456
        ]

        # Find NCT matches
        nct_matches = re.findall(nct_pattern, text, re.IGNORECASE)
        nct_identifiers = [match.upper() for match in nct_matches]

        # Find IND matches using multiple patterns
        ind_identifiers = []

        # Pattern 1: IND followed directly by 6 digits
        direct_matches = re.findall(ind_patterns[0], text, re.IGNORECASE)
        for match in direct_matches:
            ind_identifiers.append(match.upper())

        # Pattern 2: IND followed by whitespace then 6 digits
        spaced_matches = re.findall(ind_patterns[1], text, re.IGNORECASE)
        for match in spaced_matches:
            ind_identifiers.append(match)  # match is just the digits

        # Pattern 3: Title containing "IND" followed by space/colon then 6 digits
        title_matches = re.findall(ind_patterns[2], text, re.IGNORECASE)
        for match in title_matches:
            ind_identifiers.append(match)  # match is just the digits

        # Remove duplicates while preserving order
        nct_identifiers = list(dict.fromkeys(nct_identifiers))
        ind_identifiers = list(dict.fromkeys(ind_identifiers))

        result = {"nct": nct_identifiers, "ind": ind_identifiers}

        # Log the results
        location = KlassMethodLocation(self.MODULE, "_get_regulatory_identifiers")
        if nct_identifiers or ind_identifiers:
            self._errors.info(
                f"Found regulatory identifiers: NCT={nct_identifiers}, IND={ind_identifiers}",
                location,
            )
        else:
            self._errors.info("No regulatory identifiers found", location)
        return result

    def _get_sponsor_name(self, text: str) -> str:
        parts = text.split("\n")
        name = parts[0].strip() if len(parts) > 0 else "Unknown Sponsor"
        self._errors.info(
            f"Sponsor name set to '{name}'",
            location=KlassMethodLocation(self.MODULE, "_get_sponsor_name"),
        )
        return name

    def _get_sponsor_address_simple(self, text: str) -> dict:
        """Simplified version of _get_sponsor_name_and_address without using the address service"""
        raw_parts = text.split("\n") if text else []
        params = {
            "lines": [],
            "city": "",
            "district": "",
            "state": "",
            "postalCode": "",
            "country": "",
        }
        parts = []
        for part in raw_parts:
            if not part.upper().startswith(("TEL", "FAX", "PHONE", "EMAIL")):
                parts.append(part)
        if len(parts) > 0:
            params["lines"] = [part.strip() for part in parts[1:]]
            if len(parts) > 2:
                params["country"] = parts[-1].strip()
        self._errors.info(
            f"Address result '{params}'",
            location=KlassMethodLocation(self.MODULE, "_get_sponsor_address_simple"),
        )
        return params

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

    def _title_table(self):
        # print("TITLE TABLE")
        for section in self._sections:
            for table in section.tables():
                title = table_get_row(table, "Full Title")
                if title:
                    self._errors.info(
                        "Found M11 title page table",
                        location=KlassMethodLocation(self.MODULE, "_title_table"),
                    )
                    return table
        return None

    def _title_section(self):
        # print("TITLE SECTION")
        section: RawSection
        for section in self._sections:
            # print("SECTION")
            for para in section.paragraphs():
                # print(f"PARA TEXT: {para.text}")
                if para.find_at_start("Full Title"):
                    self._errors.info(
                        "Found M11 title page paragraph",
                        location=KlassMethodLocation(self.MODULE, "_title_para"),
                    )
                    return section
        return None

    def _preserve_original(self, original_parts, value):
        for part in original_parts:
            for item in re.split(r"[,\s]+", part):
                if item.upper() == value.upper():
                    return item
        return value
