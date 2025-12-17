from usdm4.api.study_version import StudyVersion
from usdm4.api.study_definition_document import StudyDefinitionDocumentVersion
from usdm4.api.narrative_content import NarrativeContent, NarrativeContentItem
from simple_error_log.errors import Errors
# from simple_error_log.error_location import KlassMethodLocation


class DocumentViewBase:
    MODULE = "usdm4_cpt.document_view.document_view_base"

    def __init__(
        self,
        version: StudyVersion,
        document: StudyDefinitionDocumentVersion,
        errors: Errors,
        template: str,
    ) -> None:
        self._version: StudyVersion = version
        self._document: StudyDefinitionDocumentVersion = document
        self._errors: Errors = errors
        self._template = template

    def _schedule_of_activities(self, section_title: str) -> str:
        if self._document:
            nc: NarrativeContent = self._document.find_narrative_content_by_title(
                section_title
            )
            if nc:
                map = self._version.narrative_content_item_map()
                nci: NarrativeContentItem = nc.content_item(map)
                return nci.text if nci else ""
        return ""

    def document_by_template(
        self, documents: list[StudyDefinitionDocumentVersion]
    ) -> StudyDefinitionDocumentVersion:
        return ((x for x in documents if x.tem), None)


class DocumentView(DocumentViewBase):
    MODULE = "usdm4_cpt.document_view.document_view"
    TEMPLATE_NAME = "CPT"

    def __init__(
        self,
        version: StudyVersion,
        document: StudyDefinitionDocumentVersion,
        errors: Errors,
    ) -> None:
        super().__init__(version, document, errors, self.TEMPLATE_NAME)

    def schedule_of_activities(self) -> str:
        return self._schedule_of_activities("Schedule of Activities")
