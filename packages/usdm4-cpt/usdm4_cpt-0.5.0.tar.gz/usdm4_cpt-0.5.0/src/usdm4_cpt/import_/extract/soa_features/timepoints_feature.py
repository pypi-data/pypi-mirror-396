import re
import unicodedata
from typing import List, Dict, Any
from simple_error_log import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_cpt.import_.extract.soa_features.expand_table import expand_table


class TimepointsFeature:
    MODULE = (
        "usdm4_cpt.import_.extract.soa_features.timepointss_feature.TimpointsFeature"
    )

    def __init__(self, errors: Errors):
        self._errors = errors

    def process(
        self, html_content: str, max_rows_to_analyze: int, ignore_last: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Alternative implementation using BeautifulSoup for more robust HTML parsing.

        Args:
            html_file_path (str): Path to the HTML file containing the SoA table
            max_rows_to_analyze (int): Maximum number of rows to analyze

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing timing values and units
        """
        results = {
            "found": False,
            "items": [],
        }
        try:
            # print(f"IGNORE LAST: {ignore_last}")
            table = expand_table(html_content)
            if not table:
                self._errors.error(
                    "No table detected", KlassMethodLocation(self.MODULE, "process")
                )
                return results

            # Analyze rows from all tables
            rows = table.find_all("tr")
            timing_row = None

            # Check first 5 rows without merged cells
            result = None
            current_score = 0
            for r_index, row in enumerate(rows[:max_rows_to_analyze]):
                cells = row.find_all(["td", "th"])
                # print(f"CELLS: {len(cells)}")
                # Skip rows with merged cells
                if any(cell.get("colspan") or cell.get("rowspan") for cell in cells):
                    continue

                if not cells:
                    continue

                first_cell_text = self._clean_text(cells[0].get_text())

                is_timing_row, score = self._is_timing_row_new(cells)
                if is_timing_row:
                    unit = self._get_time_unit(first_cell_text)
                    timing_data = []

                    # Process remaining cells (skip first column)
                    # print(f"UNIT: {unit}")
                    for index, cell in enumerate(cells[1:]):
                        # print(f"TP INDEX: {index}")

                        cell_text = self._clean_text(cell.get_text())
                        original_text = cell_text
                        if not cell_text:
                            timing_data.append(
                                {
                                    "text": original_text,
                                    "value": 0,
                                    "unit": "",
                                    "index": index,
                                }
                            )
                            continue

                        value, up_to_unit = self._decode_up_to_pattern(cell_text)
                        if value and up_to_unit:
                            timing_data.append(
                                {
                                    "text": original_text,
                                    "value": 0,
                                    "unit": "",
                                    "index": index,
                                }
                            )
                            continue

                        value = self._decode_visit_day_pattern(cell_text)
                        if value:
                            timing_data.append(
                                {
                                    "text": original_text,
                                    "value": value,
                                    "unit": "day",
                                    "index": index,
                                }
                            )
                            continue

                        value = self._decode_value_pattern(cell_text)
                        if value:
                            timing_data.append(
                                {
                                    "text": original_text,
                                    "value": value,
                                    "unit": unit,
                                    "index": index,
                                }
                            )
                            continue
                        else:
                            # print(f"  ELSE UNIT: {unit}")
                            timing_data.append(
                                {
                                    "text": original_text,
                                    "value": 0,
                                    "unit": unit,
                                    "index": index,
                                }
                            )
                    if score > current_score:
                        # print(f"BETTER SCORE: {current_score} -> {score}")
                        current_score = score
                        result = timing_data
                        timing_row = r_index + 1
            if result:
                result = result[:-1] if ignore_last else result
                results = {"found": True, "items": result, "row": timing_row}
                self._errors.info(
                    f"Timing: Row={timing_row}, Score={current_score}\n{result}"
                )
            self._errors.info(
                f"Timepoints '{results}'", KlassMethodLocation(self.MODULE, "process")
            )
            return results
        except Exception as e:
            self._errors.exception(
                "Exception raised extracting timepoints",
                e,
                KlassMethodLocation(self.MODULE, "process"),
            )
            return results

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""

        # Normalize unicode
        text = unicodedata.normalize("NFKD", text)

        # Convert unicode minus characters
        minus_chars = ["−", "‒", "–", "—", "âˆ'"]
        for minus_char in minus_chars:
            text = text.replace(minus_char, "-")

        # Handle other unicode
        text = text.replace("Â±", "±")
        text = text.replace("â‰¥", ">=")

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _is_timing_row(self, cell_text: str) -> bool:
        """Check if first cell indicates timing row."""
        if not cell_text:
            return False

        cell_lower = cell_text.lower()
        timing_keywords = [
            "study day",
            "study week",
            "target day",
            "week",
            "month",
            "day",
        ]

        # if "day" in cell_lower and "window" not in cell_lower:
        #     if any(kw in cell_lower for kw in ["study", "(+", "target"]):
        #         return True

        return any(cell_lower.startswith(kw) for kw in timing_keywords)

    def _is_timing_row_new(self, row_cells: List[str]) -> tuple[bool, int]:
        """
        Check if row matches timing criteria based on comprehensive analysis.

        Args:
            row_cells: List of cell text content from the row

        Returns:
            bool: True if row matches timing criteria, False otherwise
        """
        if not row_cells or len(row_cells) < 2:
            return False

        # Clean all cell texts
        cleaned_cells = [self._clean_text(cell.get_text()) for cell in row_cells]

        # Check first column for timing indicators
        first_cell = cleaned_cells[0].lower()
        first_column_matches = (
            "day" in first_cell
            or "week" in first_cell
            or "target day" in first_cell
            or "study day" in first_cell
        )

        # Check first few cells (<=3) for timing patterns
        timing_pattern_found = False
        for i in range(min(3, len(cleaned_cells))):
            cell_lower = cleaned_cells[i].lower()

            # Pattern: "n to m" days/weeks
            if re.search(r"\d+\s+to\s+\d+\s*(day|week)", cell_lower):
                timing_pattern_found = True
                break

            # Pattern: "Up to n" days/weeks - using the new decode method
            digits, time_unit = self._decode_up_to_pattern(cell_lower)
            if digits is not None and time_unit is not None:
                timing_pattern_found = True
                break

            # Pattern: other timing text
            if any(word in cell_lower for word in ["day", "week", "target"]):
                timing_pattern_found = True
                break

        # If neither first column nor timing patterns match, return False
        if not (first_column_matches or timing_pattern_found):
            return False, 0

        # Analyze remaining cells (after first 3 or from index 1 if no timing pattern in first 3)
        start_index = 1
        remaining_cells = cleaned_cells[start_index:]

        if not remaining_cells:
            return False, 0

        # Check if remaining cells match the criteria
        numeric_values = []
        valid_pattern_count = 0

        for cell in remaining_cells:
            cell_clean = cell.strip()
            # print(f"  CELL: {cell_clean}")
            # Skip empty cells
            if not cell_clean:
                continue

            # Handle NA or similar at the end
            if cell_clean.lower() in ["na", "n/a", "not applicable", "-"]:
                valid_pattern_count += 1
                # print(f"  VP: NA {cell_clean}")
                continue

            # Remove parenthetical content like (±3) or (+2) or (-1)
            cell_for_analysis = re.sub(r"\([±+\-]?\d+\)", "", cell_clean).strip()

            # Pattern 1: digits or minus sign with digits
            digit_match = re.match(r"^-?\d+$", cell_for_analysis)
            if digit_match:
                numeric_values.append(int(digit_match.group()))
                valid_pattern_count += 1
                # print(f"  VP: P1 {cell_clean}")
                continue

            # Pattern 3: V<digits>[/Text]<white space>D<digits>
            time_pattern_match = re.match(
                r"^V\d+\w*\/?\w*\s*D(\d+)", cell_for_analysis, re.IGNORECASE
            )
            if time_pattern_match:
                numeric_values.append(int(time_pattern_match.group(1)))
                valid_pattern_count += 1
                # print(f"  VP: P3 {cell_clean}")
                continue

            # Pattern 2: D<digit>, W<digit>, Day <digit>, Week <digit>
            time_pattern_match = re.match(
                r"^(D|W|Day\s+|Week\s+)(\d+)", cell_for_analysis, re.IGNORECASE
            )
            if time_pattern_match:
                numeric_values.append(int(time_pattern_match.group(2)))
                valid_pattern_count += 1
                # print(f"  VP: P2 {cell_clean}")
                continue

            # If cell doesn't match any valid pattern, this might not be a timing row
            # But allow some flexibility for mixed content

        # Must have at least some valid patterns
        if (
            valid_pattern_count < len(remaining_cells) * 0.5
        ):  # At least 50% should match
            # print("Not 50% matched")
            return False, 0

        # Check if numeric values are increasing (if we have enough numeric values)
        if len(numeric_values) >= 2:
            # Allow for some flexibility - values should generally increase
            increasing_count = 0
            for i in range(1, len(numeric_values)):
                if numeric_values[i] >= numeric_values[i - 1]:
                    increasing_count += 1

            # At least 70% should be increasing or equal
            if increasing_count < (len(numeric_values) - 1) * 0.7:
                # print("Not 70% increasing")
                return False, 0

        return True, valid_pattern_count + (1 if first_column_matches else 0) + (
            1 if timing_pattern_found else 0
        )

    def _decode_up_to_pattern(self, text: str) -> tuple:
        """
        Decode a string containing "Up to" pattern and extract digits and time unit.

        Args:
            text: Input string to decode

        Returns:
            tuple: (digits, time_unit) where digits is int and time_unit is str,
                   or (None, None) if pattern not found
        """
        # Regex pattern to match "Up to" (case insensitive) + digits + whitespace + day/week (singular/plural)
        pattern = r"(?i)up\s+to\s+(\d+)\s+(days?|weeks?)"

        match = re.search(pattern, text)
        if match:
            digits = int(match.group(1))
            time_unit = match.group(2).lower()
            # Normalize to singular form
            if time_unit.endswith("s"):
                time_unit = time_unit[:-1]
            return (digits, time_unit)

        return (None, None)

    def _decode_visit_day_pattern(self, text: str) -> int:
        """
        Decode visit day information using regex to extract digits from D<digits> pattern.

        Args:
            text: Input string to decode

        Returns:
            int: The extracted digits, or None if pattern not found
        """
        # Regex pattern to match any text (possibly empty), then optional sign, then D, then digits, followed by possible text
        pattern = r".*?([-+])?D(\d+).*?"
        # print(f"DVDP: {text}")
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            sign = match.group(1) if match.group(1) else ""
            result = int(sign + match.group(2))
            # print(f"DVDP R: {result}")
            return result
        return None

    def _decode_value_pattern(self, text: str) -> int:
        """
        Decode information using regex to extract digits from text.

        Args:
            text: Input string to decode

        Returns:
            int: The extracted digits, or None if pattern not found
        """
        # Regex pattern to match any text (possibly empty), then optional sign and digits, followed by possible text
        pattern = r".*?([-+]?\d+).*?"
        # print(f"DVP: {text}")
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result = int(match.group(1))
            # print(f"DVP R: {result}")
            return result
        return None

    def _get_time_unit(self, cell_text: str) -> str:
        """Determine time unit from first cell."""
        cell_lower = cell_text.lower()
        if "week" in cell_lower:
            return "week"
        elif "month" in cell_lower:
            return "month"
        return "day"
