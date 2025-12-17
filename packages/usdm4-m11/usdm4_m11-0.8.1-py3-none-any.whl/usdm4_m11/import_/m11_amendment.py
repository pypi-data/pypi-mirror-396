import re
from usdm4.builder.builder import Builder
from usdm4.api.subject_enrollment import SubjectEnrollment
from usdm4.api.geographic_scope import GeographicScope
from usdm4.api.quantity_range import Quantity
from raw_docx.raw_docx import RawDocx
from raw_docx.raw_table import RawTable
from raw_docx.raw_section import RawSection
from raw_docx.raw_paragraph import RawParagraph
from simple_error_log.errors import Errors
from usdm4_m11.import_.m11_utility import table_get_row, table_get_row_html, text_within


class M11IAmendment:
    OTHER_REASON = "No reason text found"

    def __init__(self, raw_docx: RawDocx, builder: Builder, errors: Errors):
        self._builder = builder
        self._errors = errors
        self._raw_docx = raw_docx
        other_code = self._builder.cdisc_code("C17649", "Other")
        self.enrollment = self._build_enrollment(0, "", 1)
        self.amendment_details = ""
        self.primary_reason = {"code": other_code, "other_reason": self.OTHER_REASON}
        self.secondary_reason = {"code": other_code, "other_reason": self.OTHER_REASON}
        self.summary = ""
        self.safety_impact = False
        self.safety_impact_reason = ""
        self.robustness_impact = False
        self.robustness_impact_reason = ""
        self.changes = []

    def process(self):
        section = self._raw_docx.target_document.section_by_ordinal(1)
        amend_item, amend_index = section.find_first_at_start("Amendment Details")
        table, table_index = self._amendment_table(section)
        if amend_item and table:
            self.amendment_details = section.to_html_between(amend_index, table_index)
        if table:
            self._enrollment(table)
            self._reasons(table)
            self.summary = table_get_row_html(table, "Amendment Summary")
            if self.summary:
                self._errors.info("Amendment summary found")
            self.safety_impact, self.safety_impact_reason = self._impact(
                table,
                "Is this amendment likely to have a substantial impact on the safety",
            )
            self.robustness_impact, self.robustness_impact_reason = self._impact(
                table,
                "Is this amendment likely to have a substantial impact on the reliability",
            )
            self._errors.info(
                f"Safety impact: {self.safety_impact}, {self.safety_impact_reason}"
            )
            self._errors.info(
                f"Robustness impact: {self.robustness_impact}, {self.robustness_impact}"
            )
        table = self._changes_table()
        if table:
            self.changes = self._changes(table)

    def extra(self):
        return {
            "amendment_details": self.amendment_details,
            "safety_impact": self.safety_impact,
            "safety_impact_reason": self.safety_impact_reason,
            "robustness_impact": self.robustness_impact,
            "robustness_impact_reason": self.robustness_impact_reason,
        }

    def _impact(self, table, text):
        impact = False
        reason = ""
        row, index = table.find_row(text)
        if row:
            cell = row.cells[1]
            impact = cell.text().upper().startswith("YES")
            if impact:
                reason = cell.to_html()
        return impact, reason

    def _reasons(self, table: RawTable):
        row, index = table.find_row("Reason(s) for Amendment:")
        if row:
            self.primary_reason = self._find_reason(row, "primary")
            self.secondary_reason = self._find_reason(row, "secondary")

    def _changes(self, table: RawTable):
        for index, row in enumerate(table.rows):
            if index == 0:
                continue
            self.changes.append(
                {
                    "description": row.cells[0].text(),
                    "rationale": row.cells[1].text(),
                    "section": row.cells[2].text(),
                }
            )

    def _amendment_table(self, section: RawSection):
        for index, item in enumerate(section.items):
            if isinstance(item, RawParagraph):
                if text_within(
                    "The table below describes the current amendment", item.text
                ):
                    table = section.next_table(index + 1)
                    self._errors.info(f"Amendment table {'' if table else 'not '}found")
                    return table, index
        return None, -1

    def _changes_table(self):
        section = self._raw_docx.target_document.section_by_ordinal(1)
        for index, item in enumerate(section.items):
            if isinstance(item, RawParagraph):
                if text_within(
                    "Overview of Changes in the Current Amendment", item.text
                ):
                    table = section.next_table(index + 1)
                    self._errors.info(f"Changes table {'' if table else 'not '}found")
                    return table
        return None

    def _find_reason(self, row, key):
        reason_map = [
            {"code": "C207612", "decode": "Regulatory Agency Request To Amend"},
            {"code": "C207608", "decode": "New Regulatory Guidance"},
            {"code": "C207605", "decode": "IRB/IEC Feedback"},
            {"code": "C207609", "decode": "New Safety Information Available"},
            {"code": "C207606", "decode": "Manufacturing Change"},
            {"code": "C207602", "decode": "IMP Addition"},
            {"code": "C207601", "decode": "Change In Strategy"},
            {"code": "C207600", "decode": "Change In Standard Of Care"},
            {
                "code": "C207607",
                "decode": "New Data Available (Other Than Safety Data)",
            },
            {"code": "C207604", "decode": "Investigator/Site Feedback"},
            {"code": "C207611", "decode": "Recruitment Difficulty"},
            {
                "code": "C207603",
                "decode": "Inconsistency And/Or Error In The Protocol",
            },
            {"code": "C207610", "decode": "Protocol Design Error"},
            {"code": "C17649", "decode": "Other"},
            {"code": "C48660", "decode": "Not Applicable"},
        ]
        # print(f"ROW: {row.to_html()}")
        cell = row.find_cell(key)
        if cell:
            reason = cell.text()
            parts = cell.text().split(" ")
            if len(parts) > 2:
                reason_text = parts[1]
                for reason in reason_map:
                    if reason_text in reason["decode"]:
                        self._errors.info(
                            f"Amednment reason '{reason_text}' decoded as '{reason['code']}', '{reason['decode']}'"
                        )
                        code = self._builder.cdisc_code(
                            reason["code"], reason["decode"]
                        )
                        return {"code": code, "other_reason": ""}
            self._errors.warning(f"Unable to decode amendment reason '{reason}'")
            code = self._builder.cdisc_code("C17649", "Other")
            return {"code": code, "other_reason": parts[1].strip()}
        self._errors.warning(f"Amendment reason '{key}' not decoded")
        code = self._builder.cdisc_code("C17649", "Other")
        return {"code": code, "other_reason": "No reason text found"}

    def _enrollment(self, table):
        text = table_get_row(table, "Enrolled at time ")
        number = re.findall("[0-9]+", text)
        value = int(number[0]) if number else 0
        unit = "%" if "%" in text else ""
        self.enrollment = self._build_enrollment(value, unit, 2)

    def _build_enrollment(self, value, unit, index):
        global_code = self._builder.cdisc_code("C68846", "Global")
        percent_code = self._builder.cdisc_code("C25613", "Percentage")
        unit_code = percent_code if unit == "%" else None
        unit_alias = self._builder.alias_code(unit_code) if unit_code else None
        quantity = self._builder.create(Quantity, {"value": value, "unit": unit_alias})
        params = {
            "type": global_code,
            "code": None,
        }
        geo_scope = self._builder.create(GeographicScope, params)
        params = {
            "name": f"ENROLLMENT {index}",
            "forGeographicScope": geo_scope,
            "quantity": quantity,
        }
        return self._builder.create(SubjectEnrollment, params)
