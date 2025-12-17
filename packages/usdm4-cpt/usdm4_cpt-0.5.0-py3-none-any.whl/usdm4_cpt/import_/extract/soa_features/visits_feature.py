import re
from typing import List
from simple_error_log import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_cpt.import_.extract.soa_features.expand_table import expand_table
from usdm4_cpt.import_.extract.soa_features.utility import cell_text, cell_references


class VisitsFeature:
    MODULE = "usdm4_cpt.import_.extract.soa_features.visits_feature.VisitsFeature"

    def __init__(self, errors: Errors):
        self._errors = errors

    def process(
        self, html_content: str, max_rows_to_analyze: int, last_column: int
    ) -> List[str]:
        """
        Extract visit names from Schedule of Activities (SoA) HTML table.

        This function analyzes the first few rows of an HTML table to find visit identifiers,
        typically study day numbers or visit codes like SCN, V1, V2, etc.

        Args:
            html_content (str): HTML content containing the SoA table
            max_rows_to_analyze (int): Maximum number of rows to analyze

        Returns:
            List[str]: Array of visit names/identifiers, excluding the first column.
                    Returns empty list if no valid visit row is found.

        Rules applied:
            1. Looks for visit names in rows 1-N (where N = max_rows_to_analyze)
            2. Visits typically named "SCR", "SCN", "V1", "V2", "V3", study days, etc.
            3. May have "Visit" or "Study Visit" in the first column
            4. Ignores rows with merged cells (colspan > 1)
            5. Falls back to "study day" rows if traditional visit names not found
            6. Excludes first column from output
        """

        # Parse HTML content
        results = {
            "found": False,
            "items": [],
        }
        try:
            table = expand_table(html_content)
            if not table:
                self._errors.error(
                    "No table detected", KlassMethodLocation(self.MODULE, "process")
                )
                return results

            # Get all table rows
            rows = table.find_all("tr")
            if not rows:
                self._errors.error(
                    "No table rows detected",
                    KlassMethodLocation(self.MODULE, "process"),
                )
                return results

            # Analyze specified number of rows
            best_visit_row = None
            best_visit_references = None
            best_score = -1
            visit_row = None

            for i in range(min(max_rows_to_analyze, len(rows))):
                row = rows[i]
                cells = row.find_all(["td", "th"])

                if not cells:
                    continue

                # Extract cell information
                cell_info = []
                cell_refs = []
                for j, cell in enumerate(cells):
                    cell_refs.append(cell_references(cell))
                    text = cell_text(cell)
                    cell_info.append({"index": j, "text": text})

                # Get first column text
                first_column_text = cell_info[0]["text"].lower() if cell_info else ""

                # Extract visit candidates (excluding first column)
                visit_candidates = [cell["text"] for cell in cell_info[1:]]
                cell_refs = cell_refs[1:]

                # Score this row based on visit patterns
                score = self._score_visit_row(visit_candidates, first_column_text)

                # self._errors.info(f"Visit score: {score} for row {i + 1}")
                if score > best_score:
                    self._errors.info(
                        f"Visit best score update, {best_score} -> {score}, in row {i + 1}"
                    )
                    self._errors.info(f"Visit row, {visit_candidates}")
                    best_score = score
                    best_visit_row = visit_candidates
                    best_visit_references = cell_refs
                    visit_row = i + 1

            # Return best result or empty list
            if best_visit_row is not None and best_score > 0:
                # Clean up empty strings at the end
                results["items"] = [
                    {
                        "text": x,
                        "index": index,
                        "references": best_visit_references[index],
                    }
                    for index, x in enumerate(best_visit_row[: last_column + 1])
                ]
                results["row"] = visit_row
                results["found"] = True
            self._errors.info(
                f"Visits '{results}'", KlassMethodLocation(self.MODULE, "process")
            )
            return results
        except Exception as e:
            self._errors.exception(
                "Exception raised processeding visits",
                e,
                KlassMethodLocation(self.MODULE, "process"),
            )
            return results

    def _score_visit_row(
        self, visit_candidates: List[str], first_column_text: str
    ) -> int:
        """
        Score a row based on how likely it contains visit information.

        Args:
            visit_candidates (List[str]): List of potential visit names
            first_column_text (str): Text from the first column (lowercased)

        Returns:
            int: Score indicating likelihood this row contains visits (higher = better)
        """
        score = 0
        # print(f"S0: {score}")

        # Check if first column indicates this is a visit row
        visit_indicators = ["visit", "study day", "day"]
        for indicator in visit_indicators:
            if indicator in first_column_text:
                score += 10
                break
        # print(f"S1: {score}")

        # Count how many cells match visit patterns
        visit_patterns = [
            (15, r"^(SCN|SCR).*$"),  # Screening visits
            (10, r"^(BL).*$"),  # Baseline visits
            (10, r"^(EoS|EDV).*$"),  # End of study, Early discontinuation visit
            (15, r"^V\d+.*$"),  # Visit numbers (V1, V2, etc.)
            (10, r"^Visit\s*\d+.*$"),  # Visit 1, Visit 2, etc.
            (5, r"^W\d+.*$"),  # Week numbers (W1, W2, etc.)
            (5, r"^-?\d+(\s*to\s*-?\d+)?.*$"),  # Study days (1, -1, -28 to -2, etc.)
            (2, r"^−\d+(\s*to\s*−\d+)?.*$"),  # Study days with Unicode minus
            (5, r"^Day\s*-?\d+.*$"),  # Day 1, Day -1, etc.
        ]

        for candidate in visit_candidates:
            if not candidate.strip():
                continue

            for pattern in visit_patterns:
                if re.match(pattern[1], candidate.strip(), re.IGNORECASE):
                    score += pattern[0]
                    break
        # print(f"S2: {score}")

        # Bonus for having many non-empty visit candidates
        non_empty_count = len([c for c in visit_candidates if c.strip()])
        if non_empty_count >= 5:
            score += 5
        elif non_empty_count >= 3:
            score += 2
        # print(f"S3: {score}")
        return score
