def cell_text(cell) -> str:
    for anchor in cell.findAll("a"):
        anchor.replaceWith("")
    for anchor in cell.findAll("span"):
        anchor.replaceWith("")
    text = clean_text(cell.get_text(separator=" ", strip=True))
    return text.replace(
        " ,", ""
    )  # Fix space comma, indicates a reference followed by comma was present


def cell_references(cell) -> list[str]:
    result = [anchor["id"] for anchor in cell.findAll("span")]
    return result


def clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ")  # &nbsp;
    text = text.replace("±", "±")  # Fix encoding issues
    text = text.replace("−", "-")  # Fix minus signs
    text = " ".join(text.split())  # Normalize whitespace
    return text
