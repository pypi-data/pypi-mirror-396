"""
RestCountries API for country enrichment data.

Provides:
- Country name (common, official, native)
- ISO codes (alpha-2, alpha-3, numeric)
- Region and subregion
- Languages
- Currencies
- Timezone
"""

import logging

from travelpurpose.utils.harvest import BaseHarvester, HarvestConfig

logger = logging.getLogger(__name__)


class RestCountriesClient(BaseHarvester):
    """
    Client for RestCountries API.

    Free API with no key required.
    """

    BASE_URL = "https://restcountries.com/v3.1"

    def __init__(self, config: HarvestConfig):
        """Initialize RestCountries client."""
        super().__init__(config)
        self._cache = {}  # Cache country data

    def get_country_info(self, country_name: str) -> dict | None:
        """
        Get country information.

        Args:
            country_name: Country name

        Returns:
            Country info dictionary
        """
        # Check cache first
        if country_name in self._cache:
            return self._cache[country_name]

        try:
            # Search by name
            response = self._make_request(f"{self.BASE_URL}/name/{country_name}")

            if response and isinstance(response, list) and len(response) > 0:
                country_data = response[0]

                # Extract relevant info
                info = {
                    "name": country_data.get("name", {}).get("common", country_name),
                    "official_name": country_data.get("name", {}).get("official", ""),
                    "iso_alpha2": country_data.get("cca2", ""),
                    "iso_alpha3": country_data.get("cca3", ""),
                    "region": country_data.get("region", ""),
                    "subregion": country_data.get("subregion", ""),
                    "languages": list(country_data.get("languages", {}).values()),
                    "currencies": list(country_data.get("currencies", {}).keys()),
                    "capital": country_data.get("capital", []),
                }

                # Cache it
                self._cache[country_name] = info

                logger.debug(f"RestCountries: Got info for {country_name}")
                return info

        except Exception as e:
            logger.warning(f"RestCountries error for {country_name}: {e}")

        return None

    def get_country_tags(self, country_info: dict) -> list[dict]:
        """
        Extract travel-relevant tags from country info.

        Args:
            country_info: Country information dictionary

        Returns:
            List of tag dictionaries
        """
        tags = []

        if not country_info:
            return tags

        region = country_info.get("region", "")
        subregion = country_info.get("subregion", "")

        # Regional tags
        if region == "Europe":
            tags.append(
                {
                    "tag": "european",
                    "source": "restcountries",
                    "evidence_type": "region",
                }
            )

        if region == "Asia":
            tags.append(
                {"tag": "asian", "source": "restcountries", "evidence_type": "region"}
            )

        if region == "Africa":
            tags.append(
                {"tag": "african", "source": "restcountries", "evidence_type": "region"}
            )

        if "Caribbean" in subregion or "tropical" in subregion.lower():
            tags.append(
                {
                    "tag": "tropical",
                    "source": "restcountries",
                    "evidence_type": "subregion",
                }
            )

        # Middle East
        if "Western Asia" in subregion or "Middle East" in subregion:
            tags.append(
                {
                    "tag": "middle-east",
                    "source": "restcountries",
                    "evidence_type": "subregion",
                }
            )

        return tags
