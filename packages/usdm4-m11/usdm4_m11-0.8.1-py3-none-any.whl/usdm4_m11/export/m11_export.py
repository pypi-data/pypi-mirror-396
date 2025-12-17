from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.api.wrapper import Wrapper
from usdm4_m11.utility.soup import get_soup, BeautifulSoup
from usdm4_m11.elements.elements import Elements
from usdm4_m11.specification import Specification


class M11Export:
    MODULE = "usdm4_m11.import_.m11_import.M11Export"

    def __init__(self, wrapper: Wrapper, errors: Errors):
        self._wrapper = wrapper
        self._errors = errors
        self._study = None
        self._elements = None

    def process(self) -> str:
        try:
            text = '<div class="ich-m11-outer-div"><div class="ich-m11-document-div">'
            if self._wrapper:
                elements = Elements(self._wrapper)
                specification = Specification()
                for section in specification.section_list():
                    # print(f"SECTION: {section}")
                    template: str = specification.template(section["name"])
                    # print(f"TEMPLATE: {template}")
                    text += (
                        '<div class="ich-m11-section-div">'
                        + self._parse_elements(template, elements)
                        + "</div>"
                    )
            else:
                text += "<i>Wrapper is None</i>"
            text += "</div></div>"
            return text
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "process")
            self._errors.exception(
                "Exception raised processing M11 export of USDM",
                e,
                location,
            )
            return None

    @property
    def wrapper(self) -> Wrapper:
        return self._wrapper

    def _parse_elements(self, template: str, elements: Elements) -> str:
        soup = get_soup(template, self._errors)
        ref: BeautifulSoup
        for ref in soup(["m11:element"]):
            attributes = ref.attrs
            value = elements.get(attributes["name"])
            # print(f"ELEMENT: {value}")
            ref.replace_with(value)
        return str(soup)
