from usdm4 import Wrapper
from usdm4_m11.specification import Specification
from usdm4_m11.elements import Elements
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class DataView:
    MODULE = "usdm4_m11.data_view.data_view"

    def __init__(self, wrapper: Wrapper, errors: Errors) -> None:
        self._wrapper: Wrapper = wrapper
        self._errors: Errors = errors

    def title_page(self) -> dict | None:
        try:
            result = None
            if self._wrapper:
                elements = Elements(self._wrapper)
                specification = Specification()
                element_list: dict = specification.elements("title_page")
                result = {
                    element: elements.get(element) for element in element_list.keys()
                }
            return result
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "title_page")
            self._errors.exception(
                "Exception raised processing M11 view",
                e,
                location,
            )
            return None
