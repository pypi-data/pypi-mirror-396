import re
from raw_docx.raw_docx import RawDocx, RawTable
from raw_docx.raw_table_cell import RawTableCell
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class LabTests:
    """
    Extract laboratory tests and parameters from Appendix 2 tables in clinical protocol documents.

    This class processes tables containing laboratory test information, extracting test names
    and their associated parameters into a structured dictionary format.
    """

    MODULE = "usdm4_cpt.import_.extract.lab_tests.LabTests"

    def __init__(self, raw_docx: RawDocx, errors: Errors):
        """
        Initialize the LabTests extractor.

        Args:
            raw_docx: RawDocx object containing the parsed document
            errors: Errors object for logging errors, warnings, and info messages
        """
        self._raw_docx = raw_docx
        self._sections = self._raw_docx.target_document.sections
        self._errors = errors

    def process(self) -> dict:
        """
        Process the document to extract laboratory tests and parameters.

        Returns:
            Dictionary keyed by lab test name with lists of parameters as values.
            Example: {"Hematology": ["RBC count", "platelet count", ...], ...}
        """
        location = KlassMethodLocation(self.MODULE, "process")

        # Find Appendix 2 section and lab test tables
        lab_tables = self._find_lab_test_tables()

        if not lab_tables:
            self._errors.warning(
                "No laboratory test tables found in Appendix 2", location=location
            )
            return {}

        # Extract lab tests and parameters from all found tables
        result = {}
        for table in lab_tables:
            extracted_tests = self._extract_lab_tests_from_table(table)
            result.update(extracted_tests)

        self._errors.info(
            f"Extracted {len(result)} laboratory test categories", location=location
        )

        return result

    def _find_lab_test_tables(self) -> list:
        """
        Find tables that contain laboratory test information.

        Searches all tables in the document for those with the characteristic
        "Laboratory test" and "Parameters" headers.

        Returns:
            List of RawTable objects containing lab test data
        """
        location = KlassMethodLocation(self.MODULE, "_find_lab_test_tables")
        lab_tables = []

        # Search through all sections and all tables
        for section in self._sections:
            for table in section.tables():
                if self._is_lab_test_table(table):
                    lab_tables.append(table)
                    self._errors.info("Found laboratory test table", location=location)

        return lab_tables

    def _get_cell_text(self, cell: RawTableCell) -> str:
        """
        Extract text from a table cell that may contain paragraphs or lists.

        Args:
            cell: RawTableCell to extract text from

        Returns:
            Text content of the cell
        """
        from raw_docx.raw_list import RawList
        from raw_docx.raw_paragraph import RawParagraph

        text_parts = []
        for item in cell.items:
            if isinstance(item, RawParagraph):
                text_parts.append(item.text)
            elif isinstance(item, RawList):
                text_parts.append(item.to_text())
            else:
                # Fallback for other types
                text_parts.append(str(item))

        return "\n".join(text_parts)

    def _is_lab_test_table(self, table: RawTable) -> bool:
        """
        Determine if a table contains laboratory test information.

        Args:
            table: RawTable to check

        Returns:
            True if the table appears to contain lab test data
        """
        if not table.rows or len(table.rows) < 2:
            return False

        # Check first row for expected headers
        first_row = table.rows[0]
        if len(first_row.cells) < 2:
            return False

        # Look for "Laboratory test" and "Parameters" headers
        first_cell_text = self._get_cell_text(first_row.cells[0]).strip().lower()
        second_cell_text = self._get_cell_text(first_row.cells[1]).strip().lower()

        has_lab_test_header = (
            "laboratory test" in first_cell_text or "laboratory" in first_cell_text
        )
        has_parameters_header = "parameter" in second_cell_text

        return has_lab_test_header and has_parameters_header

    def _extract_lab_tests_from_table(self, table: RawTable) -> dict:
        """
        Extract laboratory tests and parameters from a single table.

        Args:
            table: RawTable containing lab test data

        Returns:
            Dictionary of lab test names to parameter lists
        """
        location = KlassMethodLocation(self.MODULE, "_extract_lab_tests_from_table")
        result = {}

        # Skip header row, process data rows
        for i, row in enumerate(table.rows[1:], start=1):
            if len(row.cells) < 2:
                continue

            # Get test name from first column
            test_name_cell = row.cells[0]
            if not test_name_cell.is_text() or not test_name_cell.first:
                continue

            test_name = self._get_cell_text(test_name_cell).strip()
            if not test_name:
                continue

            # Get parameters from second column
            params_cell = row.cells[1]
            if not params_cell.first:
                continue

            parameters = self._extract_parameters(params_cell)

            if test_name and parameters:
                result[test_name] = parameters
                self._errors.info(
                    f"Extracted '{test_name}' with {len(parameters)} parameters",
                    location=location,
                )

        return result

    def _extract_parameters(self, cell: RawTableCell) -> list:
        """
        Extract and clean parameter names from a table cell.

        Args:
            cell: RawTableCell containing parameter information

        Returns:
            List of parameter names
        """
        parameters = []

        # Get text from cell (handles both paragraphs and lists)
        cell_text = self._get_cell_text(cell).strip()
        if not cell_text:
            return parameters

        # Split by common delimiters and clean up
        # Parameters can be separated by newlines, bullets, or other formatting
        lines = cell_text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove bullet points and other list markers
            line = re.sub(r"^[•\-\*]\s*", "", line)
            line = re.sub(r"^\d+[\.)]\s*", "", line)  # Remove numbered list markers

            # Split by common separators if on same line
            if ";" in line or "," in line:
                sub_params = re.split(r"[;,]", line)
                for param in sub_params:
                    param = param.strip()
                    if param:
                        # Clean each parameter
                        cleaned = self._clean_parameter(param)
                        if cleaned:
                            parameters.append(cleaned)
            else:
                # Handle special cases like "RBC indices:" followed by sub-items
                if line.endswith(":"):
                    # This is a category header, keep it
                    parameters.append(line)
                else:
                    # Clean the parameter
                    cleaned = self._clean_parameter(line)
                    if cleaned:
                        parameters.append(cleaned)

        # Clean up parameters list - remove empty strings and duplicates
        parameters = [p for p in parameters if p]

        # Final filtering: remove entries that don't look like lab tests
        parameters = [p for p in parameters if self._is_valid_parameter(p)]

        return parameters

    def _is_valid_parameter(self, param: str) -> bool:
        """
        Check if a parameter string appears to be a valid lab test/parameter.

        Filters out common non-test text fragments that may have slipped through cleaning.

        Args:
            param: Parameter string to validate

        Returns:
            True if the parameter appears valid, False otherwise
        """
        # Don't filter category headers (ending with :)
        if param.endswith(":"):
            return True

        # Remove parameters that are too short (less than 2 characters) except well-known ones
        if len(param) < 2:
            return False

        # List of invalid parameter patterns/phrases
        invalid_phrases = [
            "as necessary",
            "as needed",
            "as described",
            "section",
            "and",
            "or",
            "respectively",
            "refer to",
            "defined in",
            "if positive",
            "if blood",
            "if protein",
            "when elevated",
            "to determine",
            "at screening",
            "at other",
            "for all",
            "will be",
            "to be",
            "are reported",
            "is reported",
        ]

        param_lower = param.lower()

        # Check for exact matches or if the parameter consists only of these phrases
        for phrase in invalid_phrases:
            if (
                param_lower == phrase
                or param_lower.startswith(phrase + " ")
                or param_lower.endswith(" " + phrase)
            ):
                return False

        # Filter out entries that are just punctuation or conjunctions
        if re.match(r"^[,;.:()\[\]]+$", param):
            return False

        # Filter out lone conjunctions and articles
        if param_lower in [
            "and",
            "or",
            "the",
            "a",
            "an",
            "with",
            "by",
            "in",
            "on",
            "of",
            "to",
            "for",
            "as",
            "at",
            "from",
        ]:
            return False

        # Filter out section/reference markers
        if re.match(r"^(?:section|ec|refer|see)\s*[\d.]*\)?$", param_lower):
            return False

        # Filter out incomplete parenthetical expressions
        if param.endswith(")") and "(" not in param:
            return False

        return True

    def _clean_parameter(self, param: str) -> str:
        """
        Clean a parameter string to extract just the core lab test/parameter name.

        Removes descriptive text, timing information, and contextual details while
        preserving the actual test name.

        Args:
            param: Raw parameter string

        Returns:
            Cleaned parameter name
        """
        # Strip whitespace
        param = param.strip()

        # If it's very short (likely already clean) or ends with ':', return as-is
        if len(param) <= 3 or param.endswith(":"):
            return param

        # Remove common descriptive phrases
        # Pattern: "test_name to determine/at/for/if/when/as..."
        descriptive_patterns = [
            r"\s+to\s+determine\s+.*$",
            r"\s+at\s+screening.*$",
            r"\s+at\s+other.*$",
            r"\s+at\s+the\s+time.*$",
            r"\s+for\s+all\s+.*$",
            r"\s+as\s+needed.*$",
            r"\s+as\s+necessary.*$",
            r"\s+as\s+described.*$",
            r"\s+if\s+positive.*$",
            r"\s+if\s+blood.*$",
            r"\s+if\s+protein.*$",
            r"\s+if\s+the\s+.*$",
            r"\s+when\s+elevated.*$",
            r"\s+\(as\s+needed.*$",
            r"\s+\(if\s+.*$",
            r"\s+\(for\s+.*$",
            r"\s+\(refer.*$",
            r"\s+\(defined.*$",
            r"\s+refer\s+to\s+.*$",
            r"\s+defined\s+in\s+.*$",
        ]

        for pattern in descriptive_patterns:
            param = re.sub(pattern, "", param, flags=re.IGNORECASE)

        # Extract test name from phrases like "Highly sensitive serum hCG pregnancy test"
        # Look for common test abbreviations (2-6 uppercase letters possibly with numbers)
        test_abbrev_match = re.search(
            r"\b([A-Z][A-Za-z0-9]{1,5}(?:-[A-Z][A-Za-z0-9]{1,5})?)\b", param
        )
        if test_abbrev_match:
            # Check if this looks like a test abbreviation
            abbrev = test_abbrev_match.group(1)
            # Common patterns: hCG, FSH, ALT, AST, HBV, HCV, HIV, C3, C4, etc.
            if len(abbrev) <= 6 and (
                abbrev.isupper() or re.match(r"^[A-Z][a-z]*[A-Z0-9]+", abbrev)
            ):
                # Extract just this abbreviation if it's at the start or after "serum/urine/blood"
                if param.lower().startswith(abbrev.lower()) or re.search(
                    r"(serum|urine|blood|plasma)\s+" + re.escape(abbrev),
                    param,
                    re.IGNORECASE,
                ):
                    param = abbrev

        # Remove trailing parenthetical notes that weren't caught
        param = re.sub(r"\s*\([^)]*\)\s*$", "", param)

        # Remove section references
        param = re.sub(r"\s+Section\s*[\d.]*\s*$", "", param, flags=re.IGNORECASE)
        param = re.sub(r"\s+EC\s*\d*\s*$", "", param, flags=re.IGNORECASE)

        # Clean up any trailing conjunctions or prepositions
        param = re.sub(
            r"\s+(and|or|with|by|in|on|of)\s*$", "", param, flags=re.IGNORECASE
        )

        # Final cleanup
        param = param.strip()
        param = param.rstrip(",:;.")

        return param
