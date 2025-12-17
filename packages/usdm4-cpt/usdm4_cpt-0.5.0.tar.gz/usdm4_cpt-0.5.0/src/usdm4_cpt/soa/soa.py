import copy
from itertools import groupby
from usdm4.api.study_version import StudyVersion
from usdm4.api.study_design import StudyDesign
from usdm4.api.schedule_timeline import ScheduleTimeline
from usdm4.api.scheduled_instance import (
    ScheduledDecisionInstance,
    ScheduledInstance,
)
from usdm4.api.activity import Activity
from usdm4.api.condition import Condition


class SoA:
    MODULE = "usdm4_cpt.soa.soa.SoA"

    def to_data(
        self,
        study_version: StudyVersion,
        study_design: StudyDesign,
        timeline: ScheduleTimeline,
    ) -> list[list[str]]:
        # Activities
        activity_order = study_design.activity_list()
        activity_ids = {}

        # Conditions
        condtitions = study_version.conditions

        # Epochs and Visits
        ai = []
        timepoint: ScheduledInstance
        timepoints = timeline.timepoint_list()
        for timepoint in timepoints:
            if isinstance(timepoint, ScheduledDecisionInstance):
                continue
            timing = timeline.find_timing_from(timepoint.id)
            encounter = study_design.find_encounter(timepoint.encounterId)
            epoch = study_design.find_epoch(timepoint.epochId)
            entry = {
                "instance": timepoint,
                "timing": timing,
                "epoch": epoch,
                "encounter": encounter,
                "conditions": [],
            }
            condition: Condition
            for condition in condtitions:
                if timepoint.id in condition.contextIds:
                    entry["conditions"].append(condition.id)
            ai.append(entry)
            for id in timepoint.activityIds:
                activity_ids[id] = True

        # Blank row
        blank_row = {"_": {"label": "", "conditions": []}}  # used for the first column
        for item in ai:
            blank_row[item["instance"].id] = {"label": "", "conditions": []}

        # Header Rows
        results = [
            self._blank_row_copy(blank_row),
            self._blank_row_copy(blank_row),
            self._blank_row_copy(blank_row),
            self._blank_row_copy(blank_row),
        ]
        for item in ai:
            id = item["instance"].id
            results[0][id]["label"] = item["epoch"].label if item["epoch"] else "&nbsp;"
            results[1][id]["label"] = (
                item["encounter"].label if item["encounter"] else item["instance"].label
            )
            results[2][id]["label"] = (
                item["instance"].label if item["instance"] else "&nbsp;"
            )
            results[3][id]["label"] = (
                item["timing"].windowLabel if item["timing"] else "&nbsp;"
            )

        # Activity Rows
        activity: Activity
        for activity in activity_order:
            if activity.id not in activity_ids:
                continue
            row = self._blank_row_copy(blank_row)
            row["_"]["label"] = activity.label_name()
            if not activity.childIds:
                timepoint: ScheduledInstance
                for timepoint in timepoints:
                    if isinstance(timepoint, ScheduledDecisionInstance):
                        continue
                    if activity.id in timepoint.activityIds:
                        row[timepoint.id]["label"] = "X"
                        condition: Condition
                        for condition in condtitions:
                            if (
                                timepoint.id in condition.contextIds
                                and activity.id in condition.appliesToIds
                            ):
                                row[timepoint.id]["conditions"].append(condition.id)

            condition: Condition
            for condition in condtitions:
                if activity.id in condition.contextIds:
                    row["_"]["conditions"].append(condition.id)
            # print(f"ROW: {row}")
            results.append(row)

        # Done!
        # for i in range(0,4):
        # print(f"\n\nSOA RESULTS: {[x["_"] for x in results]}")
        return results

    def to_html(
        self,
        study_version: StudyVersion,
        study_design: StudyDesign,
        timeline: ScheduleTimeline,
    ) -> str:
        # Get the data
        results = self.to_data(study_version, study_design, timeline)

        # Format as HTML
        footnote_index = 1
        footnotes = {}
        lines = []
        lines.append('<table class="soa-table table">')
        lines.append("<thead>")
        lines.append('<tr class="table-active">')
        labels = self._row_labels(results, 0)
        epochs = [[i, len([*group])] for i, group in groupby(labels)]
        text = '<td><p class="m-0 p-0"><small>&nbsp;</small></p></td>'
        for epoch in epochs[1:]:
            text += f'<td class="text-center" colspan="{epoch[1]}"><p class="m-0 p-0"><small>{epoch[0]}</small></p></td>'
        lines.append(text)
        lines.append("</tr>")
        for index in range(1, 4):
            labels = self._row_labels(results, index)
            conditions = self._row_conditions(results, index)
            lines.append('<tr class="table-active">')
            lines.append('<td><p class="m-0 p-0"><small>&nbsp;</small></p></td>')
            for c_index, label in enumerate(labels[1:]):
                refs_text = ""
                if index == 1:
                    refs_text, footnote_index = self._build_conditions(
                        conditions, c_index, footnotes, footnote_index
                    )
                lines.append(
                    f'<td class="text-center"><p class="m-0 p-0"><small>{label}{refs_text}</small></p></td>'
                )
            lines.append("</tr>")
        lines.append("</thead>")
        lines.append("<tbody>")
        for index in range(4, len(results)):
            labels = self._row_labels(results, index)
            conditions = self._row_conditions(results, index)
            lines.append("<tr>")
            if all(x == "" for x in labels[1:]):
                refs_text, footnote_index = self._build_conditions(
                    conditions, 0, footnotes, footnote_index
                )
                lines.append(
                    f'<td class="m-0 p-0"><p class="m-0 p-0 bg-light"><small><strong>{labels[0]}{refs_text}</strong></small></p></td>'
                )
                lines.append(
                    f'<td class="m-0 p-0 bg-light" colspan="{len(labels) - 1}">&nbsp;</td>'
                )
            else:
                refs_text, footnote_index = self._build_conditions(
                    conditions, 0, footnotes, footnote_index
                )
                lines.append(
                    f'<td class="m-0 p-0"><p class="m-0 p-0"><small>{labels[0]}{refs_text}</small></p></td>'
                )
                for c_index in range(1, len(labels)):
                    refs_text, footnote_index = self._build_conditions(
                        conditions, c_index, footnotes, footnote_index
                    )
                    lines.append(
                        f'<td class="m-0 p-0 text-center"><p class="m-0 p-0"><small>{labels[c_index]}{refs_text}</small></p></td>'
                    )
            lines.append("</tr>")
        lines.append("</tbody>")
        lines.append("</table>")

        lines.append("<table>")
        for k, v in footnotes.items():
            lines.append("<tr>")
            lines.append("<td>")
            lines.append(f"{v}")
            lines.append("</td>")
            lines.append("<td>")
            condition = study_version.condition(k)
            lines.append(f"{condition.text}")
            lines.append("</td>")
            lines.append("</tr>")
        lines.append("</table>")

        return ("\n").join(lines)

    def _row_labels(self, results: list[dict], row: int) -> list[str]:
        return [x["label"] for x in list(results[row].values())]

    def _row_conditions(self, results: list[dict], row: int) -> list[list[str]]:
        # print(f"\n\nROW CONDITION: {row}, {results[row].values()}")
        return [x["conditions"] for x in list(results[row].values())]

    def _cell(self, results: list[dict], row: int) -> list[str]:
        return [x["label"] for x in list(results[row].values())]

    def _blank_row_copy(self, blank_row: dict) -> dict:
        # print(f"BLANK: {blank_row}")
        return copy.deepcopy(blank_row)

    def _build_conditions(
        self,
        conditions: list[list[str]],
        index: int,
        footnotes: dict,
        footnote_index: int,
    ) -> str:
        refs = []
        # print(f"CONDITION: {conditions}")
        # print(f"FOOTNOTES: {footnotes}")
        for condition in conditions[index]:
            if condition not in footnotes:
                footnotes[condition] = footnote_index
                footnote_index += 1
            refs.append(f"<sub>{footnotes[condition]}</sub>")
        return (", ").join(refs), footnote_index
