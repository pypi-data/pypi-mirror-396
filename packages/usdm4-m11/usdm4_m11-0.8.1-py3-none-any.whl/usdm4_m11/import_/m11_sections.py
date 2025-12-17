from usdm4.builder.builder import Builder
from raw_docx.raw_docx import RawDocx
from simple_error_log.errors import Errors


class M11Sections:
    def __init__(self, raw_docx: RawDocx, builder: Builder, errors: Errors):
        self._builder = builder
        self._errors = errors
        self._raw_docx = raw_docx
        self.sections = []

    def process(self):
        for section in self._raw_docx.target_document.sections:
            self.sections.append(section)
