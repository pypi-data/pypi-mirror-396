from simple_error_log import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_cpt.import_.extract.soa_features.expand_table import expand_table


class ActivityRowFeature:
    MODULE = (
        "usdm4_cpt.import_.extract.soa_features.activity_row_feature.ActivityRowFeature"
    )

    def __init__(self, errors: Errors):
        self._errors = errors

    def process(self, html_content, ignore_last: bool = False):
        """
        Enhanced version that provides detailed analysis of the table structure.

        Args:
            html_content (str): HTML content containing table structure
            verbose (bool): If True, prints detailed information about each row

        Returns:
            dict: Analysis results including first_x_row, total_rows, and row_details
        """
        table = expand_table(html_content)
        if not table:
            self._errors.error(
                "No table detected", KlassMethodLocation(self.MODULE, "process")
            )
            return {"first_activity_row": -1, "total_rows": 0}
        rows = table.find_all("tr")
        result = {
            "first_activity_row": -1,
            "last_activity_row": -1,
            "total_rows": len(rows),
        }

        for row_index, row in enumerate(rows):
            cells = row.find_all(["td", "th"])
            if ignore_last:
                cells = cells[:-1]
            cell_contents = [cell.get_text(strip=True) for cell in cells]
            # print(f"ACTIVITY: {cell_contents[0]}")

            # Check for "X" cells
            x_cells = [content for content in cell_contents if content.upper() == "X"]
            # print(f"X CELLS: {row_index} = {x_cells}")
            has_x = len(x_cells) > 0

            # # Check for partial X row with merged cells using text rather than X
            # value = None
            # partial_row = False
            # for x in cell_contents[1:]:
            #     if value and x == value:
            #         partial_row = True
            #     else:
            #         value = x
            # # print(f"PARTIAL ROW: {row_index} = {partial_row}")

            # Check for a merged line, every cell will be the same
            merged_row = all(x == cell_contents[0] for x in cell_contents)
            # print(f"NON BLANK: {row_index} = {merged_row}")

            # Check for an "all cells" line, every cell will be the same from second column to the end
            all_row = all(x == cell_contents[1] for x in cell_contents[1:])
            # print(f"ALL ROW: {row_index} = {all_row}")

            # Set first_x_row if not already set and this row has single X
            if result["first_activity_row"] == -1 and (
                has_x or merged_row or all_row
            ):  # or partial_row):
                result["first_activity_row"] = row_index
            if has_x or merged_row or all_row:  # or partial_row:
                result["last_activity_row"] = row_index
        self._errors.info(
            f"Activity Row: {result}",
            KlassMethodLocation(self.MODULE, "process"),
        )
        # print(f"ACTIVITY ROW: {result}")
        return result
