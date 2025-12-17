from simple_error_log import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_cpt.import_.extract.soa_features.expand_table import expand_table


class EpochsFeature:
    MODULE = "usdm4_cpt.import_.extract.soa_features.epochs_feature.EpochsFeature"

    def __init__(self, errors: Errors):
        self._errors = errors

    def process(self, html_content: str, last_column: int) -> dict:
        """
        Extract clinical trial period information with detailed analysis.

        Args:
            html_table (str): HTML string containing the table
            ignore_last (bool): Ignore the last column in the table (contains notes etc) (default: False)

        Returns:
            dict: Detailed analysis including whether period info was found,
                the extracted columns, and analysis details
        """
        results = {
            "found": False,
            "items": None,
        }
        try:
            table = expand_table(html_content)
            if not table:
                self._errors.error(
                    "No table detected", KlassMethodLocation(self.MODULE, "process")
                )
                return results

            first_row = table.find("tr")
            if not first_row:
                self._errors.error(
                    "No first row detected in table",
                    KlassMethodLocation(self.MODULE, "process"),
                )
                return results

            # Get all cells in the first row
            cells = first_row.find_all(["td", "th"])

            # Define period-related terms
            period_terms = [
                "screening",
                "scn",
                "treatment",
                "follow-up",
                "follow up",
                "baseline",
                "washout",
                "run-in",
                "eos",
                "end of study",
                "edv",
                "early discontinuation",
            ]

            period_columns = []

            for i, cell in enumerate(cells):
                text = cell.get_text(strip=True)
                text_lower = text.lower()
                colspan = int(cell.get("colspan", 1))

                # Skip first column
                if i == 0:
                    continue

                # Skip columns after last column
                if i > (last_column + 1):
                    continue

                # Check for period information
                matching_terms = [term for term in period_terms if term in text_lower]
                is_period_cell = len(matching_terms) > 0

                if is_period_cell:
                    results["found"] = True

                # Add to result columns (expanding colspan)
                for index, _ in enumerate(range(colspan)):
                    period_columns.append({"text": text, "index": i + index - 1})

            # Build final result
            if results["found"]:
                results["items"] = period_columns
                results["row"] = 1  # Note, fixed as we want epochs in row 1
            self._errors.info(
                f"Epochs '{results}'", KlassMethodLocation(self.MODULE, "process")
            )
            return results
        except Exception as e:
            self._errors.exception(
                "Exception raised extracting epochs",
                e,
                KlassMethodLocation(self.MODULE, "process"),
            )
            return results
