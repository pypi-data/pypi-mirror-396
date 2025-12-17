from usdm4.api.wrapper import Wrapper


class Elements:
    ELEMENT_METHODS = {
        "Sponsor Confidentiality Statement": "_confidentiality_statement",
        "Full Title": "_full_title",
        "Trial Acronym": "_trial_acronym",
        "Sponsor Protocol Identifier": "_protocol_identifier",
        "Original Protocol Indicator": "_original_protocol",
        "Version Number": "_version_number",
        "Version Date": "_not_defined",
        "Amendment Identifier": "_not_defined",
        "Amendment Scope": "_not_defined",
        "Country Identifier": "_not_defined",
        "Region Identifier": "_not_defined",
        "Site Identifier": "_not_defined",
        "Sponsors Investigational Product Codes": "_not_defined",
        "Nonproprietary Names": "_not_defined",
        "Proprietary Names": "_not_defined",
        "Trial Phase": "_not_defined",
        "Trial Short Title": "_not_defined",
        "Sponsor Name": "_not_defined",
        "Sponsor Legal Address": "_not_defined",
        "Co-Sponsor Name": "_not_defined",
        "Co-Sponsor Legal Address": "_not_defined",
        "Local Sponsor Name": "_not_defined",
        "Local Sponsor Legal Address": "_not_defined",
        "Device Manufacturer Name": "_not_defined",
        "Device Manufacturer Legal Address": "_not_defined",
        "EU CT Number": "_not_defined",
        "FDA IND Number": "_not_defined",
        "IDE Number": "_not_defined",
        "jRCT Number": "_not_defined",
        "NCT Number": "_not_defined",
        "NMPA IND Number": "_not_defined",
        "WHO-UTN Number": "_not_defined",
        "Other Regulatory or Clinical Trial Identifier": "_not_defined",
        "Sponsor Approval Date": "_not_defined",
        "State location where sponsor approval information can be found": "_not_defined",
    }

    def __init__(self, wrapper: Wrapper):
        self._wrapper: Wrapper = wrapper
        self._study = self._wrapper.study
        self._study_version = self._study.first_version()

    def get(self, name: str) -> str | None:
        if name in self.ELEMENT_METHODS:
            method = self.ELEMENT_METHODS[name]
            # print(f"METHOD: {method}")
            value = getattr(self, method)()
            # print(f"VALUE: {value}")
            return str(value)
        else:
            return None

    def _confidentiality_statement(self) -> str:
        return self._study_version.confidentiality_statement()

    def _full_title(self) -> str:
        return self._study_version.official_title_text()

    def _trial_acronym(self) -> str:
        return self._study_version.acronym_text()

    def _protocol_identifier(self) -> str:
        return self._study_version.sponsor_identifier_text()

    def _original_protocol(self) -> str:
        return "Yes" if self._study_version.original_version() else "No"

    def _version_number(self) -> str:
        return self._study_version.versionIdentifier

    def _not_defined(self) -> str:
        return ""
