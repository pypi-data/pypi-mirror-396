from typing import List, Dict
from simple_error_log import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_cpt.import_.extract.soa_features.expand_table import expand_table
from usdm4_cpt.import_.extract.soa_features.utility import cell_text, cell_references


class ActivitiesFeature:
    MODULE = (
        "usdm4_cpt.import_.extract.soa_features.activities_feature.ActivitiesFeature"
    )

    def __init__(self, errors: Errors):
        self._errors = errors

    def process(
        self, html_content: str, assessments: dict, start_row: int, last_column: int
    ) -> List[Dict]:
        """
        Extract parent and child activities from a Schedule of Activities HTML table.

        Args:
            html_content (str): HTML content containing the table
            start_row (int): Row number to start processing activities from.
            ignore_last (bool): Ignore the last column in the table (contains notes etc) (default False)

        Returns:
            List of activity dictionaries, either standalone activities or parent activities with nested children
        """

        # Parse HTML with BeautifulSoup
        results = {
            "found": False,
            "items": [],
        }
        table = expand_table(html_content)
        if not table:
            self._errors.error(
                "No table detected", KlassMethodLocation(self.MODULE, "process")
            )
            return results

        # Extract all table rows
        rows = table.find_all("tr")

        # Convert rows to list of cell contents
        table_data = []
        table_references = []
        for row in rows:
            cells = row.find_all(["td", "th"])
            # print(f"ROW SOURCE: {len(cells)}")
            row_cells = []
            row_references = []
            for cell in cells[
                : last_column + 2
            ]:  # +2 becuase includes activity name column
                row_references.append(cell_references(cell))
                row_cells.append(cell_text(cell))
            # print(f"ROW: {len(row_cells)}")
            table_data.append(row_cells)
            table_references.append(row_references)
        if not table_data:
            raise ValueError("No data found in table")

        # Extract activities
        # print(f"START ROW: {start_row}")
        results["items"] = self._extract_activities(
            table_data, table_references, assessments, start_row
        )
        results["found"] = True
        return results

    def _extract_activities(
        self,
        table_data: List[List[str]],
        table_references: List[List[str]],
        assessments: dict,
        start_row: int,
    ) -> List[Dict]:
        """
        Extract parent and child activities from the table data.

        Args:
            table_data: List of rows
            table_references: List of row references
            start_row: Row to start processing from
            ignore_last: Ignore last column if true (usually notes or similar)

        Returns:
            List of activity dictionaries
        """
        activities = []
        current_parent = None

        # print(f"\n\nASSESSMENTS: {assessments}")

        for i in range(start_row, len(table_data)):
            row = table_data[i]
            references = table_references[i]
            if not row:
                continue
            activity_name = row[0].strip()

            # print(f"NAME: {activity_name}")

            if not activity_name:
                self._errors.warning("Missing activity name in row {i + 1}")
                continue
            if self._is_parent(row):
                current_parent = {"name": activity_name, "index": i, "children": []}
                activities.append(current_parent)
            else:
                # Check if this row has "X" markers (indicating it's a child activity)
                has_x_markers = self._has_x_markers(row)
                has_text_markers = self._has_text_markers(row)
                if has_x_markers or has_text_markers:
                    activity = {
                        "name": activity_name,
                        "index": i,
                        "visits": self._extract_visits_for_activity(row, references),
                        "references": references[0],
                        "actions": {
                            "bcs": self._include_assessments(
                                activity_name, assessments
                            ),
                            "procedures": [],
                            "timelines": [],
                        },
                    }
                    if current_parent:
                        current_parent["children"].append(activity)
                    else:
                        activities.append(activity)

        return activities

    def _include_assessments(self, activity_name: str, assessments: dict) -> list[str]:
        result = []
        name_upper: str = activity_name.upper()
        name: str
        tests: list
        for name, tests in assessments.items():
            if name.upper() in name_upper:
                result += tests
        return result

    def _has_x_markers(self, row: List[str]) -> bool:
        """
        Check if a row contains "X" markers indicating scheduled activities.

        Args:
            row: List of cell contents for the row

        Returns:
            True if row contains X markers
        """
        return any(cell.strip().upper() == "X" for cell in row if cell)

    def _has_text_markers(self, row: List[str]) -> bool:
        value = None
        for cell in row:
            if value and cell == value:
                # At least two cells with same text together
                return True
            else:
                value = cell
        return False

    def _is_parent(self, row: List[str]) -> bool:
        return all(x == row[0] for x in row)

    def _extract_visits_for_activity(
        self, row: list[str], references: list[str]
    ) -> list[str]:
        """
        Extract which visits an activity is scheduled for based on X markers.

        Args:
            row: Row data containing X markers
            visit_headers: List of visit identifiers

        Returns:
            List of visit names where activity is scheduled
        """
        visits = []
        # Check each cell for X markers, mapping to visit headers
        # print(f"FINDING X: {len(row)}")
        for j in range(1, len(row)):
            if row[j].strip().upper() == "X" or row[j].strip() != "":
                visits.append({"index": j - 1, "references": references[j]})
        return visits
