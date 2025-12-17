from bs4 import BeautifulSoup
from typing import Optional


def expand_table(html_content: str) -> Optional[BeautifulSoup]:
    """
    Expand an HTML table by removing all row and column spans, making every cell a single cell.

    This utility method processes the first table found in the HTML content and expands it
    by duplicating cell content across spanned rows and columns, then removing the span attributes.

    Args:
        html_content (str): HTML string containing the table to be expanded

    Returns:
        BeautifulSoup table object with all spans removed, or None if no table found

    Raises:
        ValueError: If the HTML content is empty or invalid
    """
    if not html_content or not html_content.strip():
        raise ValueError("HTML content cannot be empty")

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")

    if not table:
        return None

    # Get all rows in the table
    rows = table.find_all("tr")
    if not rows:
        return table

    # Create a matrix to track the expanded table structure
    # First, determine the maximum dimensions needed
    max_cols = 0
    row_data = []

    # Parse existing table structure and calculate required dimensions
    for row_idx, row in enumerate(rows):
        cells = row.find_all(["td", "th"])
        current_row_data = []
        col_offset = 0

        for cell in cells:
            # Skip columns that are already occupied by previous rowspans
            while (
                row_idx < len(row_data)
                and col_offset < len(row_data[row_idx])
                and row_data[row_idx][col_offset] is not None
            ):
                col_offset += 1

            # Get span attributes
            colspan = int(cell.get("colspan", 1))
            rowspan = int(cell.get("rowspan", 1))

            # Store cell information
            cell_info = {
                "element": cell,
                "colspan": colspan,
                "rowspan": rowspan,
                "content": cell.decode_contents(),  # Preserve HTML content
                "attributes": dict(cell.attrs),
            }

            # Remove span attributes from the stored attributes
            cell_info["attributes"].pop("colspan", None)
            cell_info["attributes"].pop("rowspan", None)

            current_row_data.append((col_offset, cell_info))
            col_offset += colspan
            max_cols = max(max_cols, col_offset)

        row_data.append(current_row_data)

    # Create expanded matrix
    expanded_matrix = []
    for row_idx in range(len(rows)):
        expanded_matrix.append([None] * max_cols)

    # Fill the expanded matrix
    for row_idx, row_cells in enumerate(row_data):
        col_idx = 0
        for col_offset, cell_info in row_cells:
            colspan = cell_info["colspan"]
            rowspan = cell_info["rowspan"]

            # Fill all positions covered by this cell
            col_idx = col_offset
            for r in range(row_idx, min(row_idx + rowspan, len(expanded_matrix))):
                while col_idx < max_cols and expanded_matrix[r][col_idx] is not None:
                    col_idx += 1
                for c in range(col_idx, min(col_idx + colspan, max_cols)):
                    expanded_matrix[r][c] = cell_info

    # Rebuild the table with expanded structure
    # Clear existing rows
    for row in rows:
        row.decompose()

    # Create new rows with expanded cells
    for row_idx, row_cells in enumerate(expanded_matrix):
        new_row = soup.new_tag("tr")

        for cell_info in row_cells:
            if cell_info is not None:
                # Create new cell
                tag_name = "th" if cell_info["element"].name == "th" else "td"
                new_cell = soup.new_tag(tag_name)

                # Set content (preserve HTML)
                if cell_info["content"]:
                    new_cell.append(BeautifulSoup(cell_info["content"], "html.parser"))
                else:
                    new_cell.string = ""

                # Set attributes (excluding span attributes)
                for attr, value in cell_info["attributes"].items():
                    new_cell[attr] = value

                new_row.append(new_cell)
            else:
                # Create empty cell for None positions (shouldn't happen in well-formed tables)
                new_cell = soup.new_tag("td")
                new_cell.string = ""
                new_row.append(new_cell)

        table.append(new_row)

    return table
