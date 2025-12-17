from raw_docx.raw_docx import RawDocx, RawParagraph, RawSection
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_cpt.import_.extract.soa_features.activity_row_feature import (
    ActivityRowFeature,
)
from usdm4_cpt.import_.extract.soa_features.notes_feature import NotesFeature
from usdm4_cpt.import_.extract.soa_features.epochs_feature import EpochsFeature
from usdm4_cpt.import_.extract.soa_features.visits_feature import VisitsFeature
from usdm4_cpt.import_.extract.soa_features.timepoints_feature import TimepointsFeature
from usdm4_cpt.import_.extract.soa_features.windows_feature import WindowsFeature
from usdm4_cpt.import_.extract.soa_features.activities_feature import ActivitiesFeature
from usdm4_cpt.import_.extract.soa_features.conditions_feature import ConditionsFeature


class SoA:
    MODULE = "usdm4_cpt.import_.soa.SoA"

    def __init__(self, raw_docx: RawDocx, errors: Errors):
        self._raw_docx = raw_docx
        self._errors = errors

    def process(self, assessments: dict) -> dict | None:
        try:
            self._assessments = assessments
            section = self._raw_docx.target_document.section_by_title(
                "Schedule of Activities"
            )
            if section:
                raw_result = self._decode_soa(section)
            else:
                self._errors.error(
                    "Failed to find the SoA section in the document",
                    KlassMethodLocation(self.MODULE, "process"),
                )
                raw_result = None
            return raw_result
        except Exception as e:
            self._errors.exception(
                "Error processing SoA", e, KlassMethodLocation(self.MODULE, "process")
            )
            return None

    def _decode_soa(self, section: RawSection) -> dict | None:
        if soa_tables := section.tables():
            result = {}
            html = soa_tables[0].to_html()
            soa_index = section.index(soa_tables[0])
            # print(f"TABLE INDEX: {soa_index}")
            result["activity_row"] = ActivityRowFeature(self._errors).process(html)
            activity_row = result["activity_row"]["first_activity_row"]
            last_header_row = activity_row + 1
            result["notes"] = NotesFeature(self._errors).process(html)
            ignore_last = result["notes"]["has_references"]
            result["timepoints"] = TimepointsFeature(self._errors).process(
                html, last_header_row, ignore_last
            )
            last_column = self._check_timepoints(result["timepoints"])
            result["epochs"] = EpochsFeature(self._errors).process(html, last_column)
            result["visits"] = VisitsFeature(self._errors).process(
                html, last_header_row, last_column
            )
            result["windows"] = WindowsFeature(self._errors).process(
                html, last_header_row, last_column
            )
            result["activities"] = ActivitiesFeature(self._errors).process(
                html, self._assessments, activity_row, last_column
            )
            result["conditions"] = ConditionsFeature(self._errors).process(
                self._extract_footnotes(section, soa_index)
            )
            return result
        else:
            self._errors.error(
                "No SoA found", KlassMethodLocation(self.MODULE, "_decode_soa")
            )
            return None

    def _check_timepoints(self, result: dict) -> int:
        # print(f"BREAK1: {result["items"]}")
        index = len(result["items"]) - 1
        # print(f"CHECK1: {index}")
        for item in reversed(result["items"]):
            if item["value"] > 0:
                # print(f"BREAK: {index}")
                break
            index -= 1
        if index >= 0:
            result["items"] = result["items"][: index + 1]
            # print(f"BREAK1: {result["items"]}")
            return index
        return len(result["items"]) - 1

    def _extract_footnotes(self, section: RawSection, soa_index: int) -> str:
        items = section.items_between(soa_index + 1, len(section.items))
        text = ""
        for item in items:
            if isinstance(item, RawParagraph):
                text += item.to_html()
            else:
                break
        return text
