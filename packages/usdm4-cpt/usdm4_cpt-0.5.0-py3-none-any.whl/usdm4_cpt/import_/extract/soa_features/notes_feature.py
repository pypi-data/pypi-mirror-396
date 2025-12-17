import re
from simple_error_log import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_cpt.import_.extract.soa_features.expand_table import expand_table
from typing import Dict, List, Any


class NotesFeature:
    MODULE = "usdm4_cpt.import_.extract.soa_features.notes_feature.NotesFeature"

    def __init__(self, errors: Errors):
        self._errors = errors

    def process(self, html_content: str) -> Dict[str, Any]:
        """
        Analyze the last column of a Schedule of Activities (SoA) table to determine
        if it contains comments, notes, or references to document sections.

        Args:
            html_content (str): HTML content containing the SoA table

        Returns:
            Dict[str, Any]: JSON structure with analysis results
        """
        result = {
            "found": False,
            "items": [],
        }
        table = expand_table(html_content)
        if not table:
            self._errors.error(
                "No table detected", KlassMethodLocation(self.MODULE, "process")
            )
            return result
        rows = table.find_all("tr")
        if not rows:
            self._errors.error(
                "No rows detected in table",
                KlassMethodLocation(self.MODULE, "process"),
            )
            return result
        last_column_content = []

        # Extract content from the last column of each row
        for index, row in enumerate(rows):
            cells = row.find_all(["td", "th"])

            if cells:
                # Get the last cell in the row
                last_cell = cells[-1]

                # Extract text content, handling nested <p> tags
                cell_text = ""
                paragraphs = last_cell.find_all("p")
                if paragraphs:
                    # Join text from all paragraphs in the cell
                    cell_text = " ".join([p.get_text(strip=True) for p in paragraphs])
                else:
                    cell_text = last_cell.get_text(strip=True)

                last_column_content.append({"text": cell_text, "index": index})
            else:
                # Empty row
                last_column_content.append({"text": "", "index": index})

        # Analyze the content to determine type and characteristics
        result = self._analyze_content_type(last_column_content)
        # print(f"LAST COLUMN: {result}")
        return result

    def _analyze_content_type(self, content_list: List[str]) -> Dict[str, Any]:
        """
        Analyze the content of the last column to determine its type and characteristics.

        Args:
            content_list (List[str]): List of strings from the last column

        Returns:
            Dict[str, Any]: Analysis results
        """

        # Remove empty strings for analysis
        non_empty_content = [
            x["text"].strip() for x in content_list if x["text"].strip()
        ]
        has_x = any(x.upper() == "X" for x in non_empty_content)

        # print(f"NON EMPTY: {non_empty_content}")
        # print(f"HAS X: {has_x}")

        if not non_empty_content:
            return {
                "has_references": False,
                "content_type": "Empty Column",
                "description": "The last column contains no content",
                "items": [],
            }
        if has_x:
            return {
                "has_references": False,
                "content_type": "'X' detected",
                "description": "The last column looks like it is part of the SoA",
                "items": [],
            }

        # Count different types of content
        section_references = 0
        protocol_references = 0
        notes_comments = 0
        other_content = 0

        # Patterns to identify different content types
        section_pattern = re.compile(r"section\s+\d+(\.\d+)*", re.IGNORECASE)
        protocol_pattern = re.compile(r"protocol|procedure|guideline", re.IGNORECASE)
        note_comment_patterns = [
            re.compile(r"note[:;]?", re.IGNORECASE),
            re.compile(r"comment[:;]?", re.IGNORECASE),
            re.compile(r"remark[:;]?", re.IGNORECASE),
            re.compile(r"see\s+", re.IGNORECASE),
            re.compile(r"refer\s+", re.IGNORECASE),
        ]

        for item in non_empty_content:
            item_lower = item.lower()

            if section_pattern.search(item):
                section_references += 1
            elif protocol_pattern.search(item):
                protocol_references += 1
            elif any(pattern.search(item) for pattern in note_comment_patterns):
                notes_comments += 1
            elif item_lower not in [
                "applicable protocol sections",
                "references",
                "notes",
                "comments",
            ]:
                # Skip common headers
                other_content += 1

        # Determine content type based on analysis
        total_analyzed = len(non_empty_content) - 1  # Exclude likely header

        if section_references > 0 and section_references >= total_analyzed * 0.5:
            return {
                "has_references": True,
                "content_type": "Protocol Section References",
                "description": "References to specific sections of the clinical trial protocol document that provide detailed information about each study activity",
                "items": content_list,
            }
        elif protocol_references > 0:
            return {
                "has_references": True,
                "content_type": "Protocol References",
                "description": "References to protocol documents or procedures",
                "items": content_list,
            }
        elif notes_comments > 0:
            return {
                "has_references": True,
                "content_type": "Notes and Comments",
                "description": "Additional notes, comments, or explanatory text for study activities",
                "items": content_list,
            }
        elif other_content > 0:
            return {
                "has_references": True,
                "content_type": "Mixed Content",
                "description": "Contains various types of supplementary information",
                "items": content_list,
            }
        else:
            return {
                "has_references": False,
                "content_type": "Header Only",
                "description": "Column appears to contain only header information",
                "items": content_list,
            }
