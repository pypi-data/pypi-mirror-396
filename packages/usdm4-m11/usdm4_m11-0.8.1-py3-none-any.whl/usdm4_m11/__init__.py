from usdm4_m11.import_.m11_import import M11Import
from usdm4_m11.export.m11_export import M11Export
from usdm4_m11.data_view import DataView
from usdm4 import USDM4, Wrapper
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class USDM4M11:
    MODULE = "src.usdm4_m11.__init__.USDM4M11"

    def __init__(self):
        self._errors = Errors()
        self._wrapper = None
        self._to_file_path = None
        self._extra = None
        self._source = None
        self._source_no_sections = None

    def from_docx(self, filepath: str) -> Wrapper | None:
        try:
            m11_import = M11Import(filepath, self._errors)
            result = m11_import.process()
            self._extra = m11_import.extra
            self._source = m11_import.source
            self._source_no_sections = m11_import.source_no_sections
            return result
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "from_docx")
            self._errors.exception(
                f"Exception raised converting M11 '.docx' file '{filepath}'",
                e,
                location,
            )
            return None

    def to_html(self, file_path: str) -> str | None:
        try:
            m11_export: M11Export = M11Export(
                self._get_wrapper(file_path), self._errors
            )
            result = m11_export.process()
            self._wrapper = m11_export.wrapper
            return result
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "to_html")
            self._errors.exception(
                f"Exception raised exporting USDM to M11, file '{file_path}'",
                e,
                location,
            )
            return None

    def data_view(self, file_path: str) -> dict | None:
        try:
            self._m11_view = DataView(self._get_wrapper(file_path), self._errors)
            return self._m11_view.title_page()
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "data_view")
            self._errors.exception(
                f"Exception raised generating M11 data view, file '{file_path}'",
                e,
                location,
            )
            return None

    @property
    def extra(self) -> dict:
        return self._extra

    @property
    def source(self) -> dict:
        return self._source

    @property
    def source_no_sections(self) -> dict:
        return self._source_no_sections

    @property
    def wrapper(self):
        return self._wrapper

    @property
    def errors(self):
        return self._errors

    def _get_wrapper(self, file_path: str) -> Wrapper:
        if file_path == self._to_file_path and self.wrapper:
            return self._wrapper
        else:
            usdm = USDM4()
            self._to_file_path = file_path
            self._wrapper: Wrapper = usdm.load(self._to_file_path, self._errors)
            return self._wrapper
