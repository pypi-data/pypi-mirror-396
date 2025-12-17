from usdm4.builder.builder import Builder
from raw_docx.raw_docx import RawDocx
from simple_error_log.errors import Errors
from usdm4_m11.import_.m11_utility import table_get_row


class M11IEstimands:
    def __init__(self, raw_docx: RawDocx, builder: Builder, errors: Errors):
        self._builder = builder
        self._errors = errors
        self._raw_docx = raw_docx
        self.objectives = []

    def process(self):
        self.objectives = self._primary_objectives()

    def _primary_objectives(self):
        objectives = []
        main_section = self._raw_docx.target_document.section_by_number("3.1")
        if main_section:
            main_has_content = main_section.has_content()
            if main_has_content:
                self._errors.error(
                    "Invalid M11 document. Section 3.1 contains content when it should be empty."
                )
            else:
                sections = True
                section_number = 1
                while sections:
                    sub_section = self._raw_docx.target_document.section_by_number(
                        f"3.1.{section_number}"
                    )
                    if sub_section:
                        paras = sub_section.paragraphs()
                        if paras:
                            objective = {
                                "objective": sub_section.paragraphs()[0].to_html(),
                                "population": "",
                                "treatment": "",
                                "endpoint": "",
                                "population_summary": "",
                                "i_event": "",
                                "strategy": "",
                            }
                            tables = sub_section.tables()
                            if tables:
                                table = tables[0]
                                keys = {
                                    "population": "Population",
                                    "treatment": "Treatment",
                                    "endpoint": "Endpoint",
                                    "population_summary": "Population-Level Summary",
                                }
                                for key, text in keys.items():
                                    item = table_get_row(table, text)
                                    if item:
                                        objective[key] = item
                                        self._errors.info(
                                            f"Found estimands {key} -> {item}"
                                        )
                                item, index = table.find_row("Intercurrent Event")
                                if item:
                                    item, index = table.next(index)
                                    objective["i_event"] = item.cells[0].to_html()
                                    objective["strategy"] = item.cells[1].to_html()
                                    self._errors.info(
                                        "Found estimands event and strategy"
                                    )
                            objectives.append(objective)
                        section_number += 1
                    else:
                        sections = False
        else:
            self._errors.error("Invalid M11 document. Section 3.1 is not present.")
        return objectives
