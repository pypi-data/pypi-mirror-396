from usdm4.builder.builder import Builder
from raw_docx.raw_docx import RawDocx
from simple_error_log.errors import Errors


class M11InclusionExclusion:
    def __init__(self, raw_docx: RawDocx, builder: Builder, errors: Errors):
        self._builder = builder
        self._errors = errors
        self._raw_docx = raw_docx
        self.inclusion = []
        self.exclusion = []

    def process(self):
        section = self._raw_docx.target_document.section_by_number("5.2")
        if section:
            lists = section.lists()
            if lists:
                for item in lists[0].items:
                    self.inclusion.append(item.to_html())
            else:
                self._errors.error(
                    "Failed to find a list in section 5.2 in M11 document"
                )
        else:
            self._errors.error("Failed to find section 5.2 in M11 document")

        section = self._raw_docx.target_document.section_by_number("5.3")
        if section:
            lists = section.lists()
            if lists:
                for item in lists[0].items:
                    self.exclusion.append(item.to_html())
            else:
                self._errors.error(
                    "Failed to find a list in section 5.3 in M11 document"
                )
        else:
            self._errors.error("Failed to find section 5.3 in M11 document")
