from usdm4.api.study_version import StudyVersion
from usdm4.api.study_definition_document_version import StudyDefinitionDocumentVersion
from simple_error_log import Errors
from usdm4_cpt.document_view.document_view import DocumentViewBase


class DocumentView(DocumentViewBase):
    MODULE = "usdm4_m11.document_view.document_view"
    TEMPLATE_NAME = "M11"

    def __init__(
        self,
        version: StudyVersion,
        document: StudyDefinitionDocumentVersion,
        errors: Errors,
    ) -> None:
        super().__init__(version, document, errors, self.TEMPLATE_NAME)

    def schedule_of_activities(self) -> str:
        return self._schedule_of_activities("Schedule of Activities")
