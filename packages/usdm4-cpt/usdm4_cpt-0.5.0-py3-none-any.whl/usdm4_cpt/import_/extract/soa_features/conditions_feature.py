from bs4 import BeautifulSoup
from simple_error_log import Errors
from simple_error_log.error_location import KlassMethodLocation


class ConditionsFeature:
    MODULE = (
        "usdm4_cpt.import_.extract.soa_features.conditions_feature.ConditionsFeature"
    )

    def __init__(self, errors: Errors):
        self._errors = errors

    def process(self, html_content: str) -> list[dict]:
        results = {
            "found": False,
            "items": [],
        }
        try:
            soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
            para: BeautifulSoup
            for para in soup.findAll("p"):
                anchor: BeautifulSoup
                for anchor in para.findAll("a"):
                    # Remove the '#' from the href
                    results["items"].append(
                        {
                            "text": para.get_text(separator=" ", strip=True),
                            "reference": anchor["href"][1:],
                        }
                    )
            self._errors.info(
                f"Conditions '{results}'", KlassMethodLocation(self.MODULE, "process")
            )
            return results
        except Exception as e:
            self._errors.exception(
                "Exception raised processeding visits",
                e,
                KlassMethodLocation(self.MODULE, "process"),
            )
            return results
