"""
Kayak harvester for city tags.

Uses public autocomplete and landing pages.
"""

import logging

from travelpurpose.utils.harvest import BaseHarvester, safe_harvest

logger = logging.getLogger(__name__)


class KayakHarvester(BaseHarvester):
    """Harvester for Kayak public data."""

    BASE_URL = "https://www.kayak.com"

    @safe_harvest
    def get_city_tags(self, city_name: str, country: str = "") -> list[dict]:
        """
        Get tags for a city from Kayak public pages.

        Args:
            city_name: City name
            country: Optional country name

        Returns:
            List of tag dictionaries
        """
        tags = []

        # Construct city guide URL
        search_query = f"{city_name}-{country}".strip().replace(" ", "-").lower()
        url = f"{self.BASE_URL}/guides/{search_query}"

        # Extract tags from page
        page_tags = self.extract_tags_from_page(url, city_name, "kayak")
        tags.extend(page_tags)

        # Common Kayak tag patterns
        kayak_tag_keywords = [
            "mice",
            "convention",
            "airport hub",
            "family travel",
            "nightlife",
            "business",
            "beach",
            "cultural",
            "adventure",
        ]

        # Filter tags
        filtered_tags = []
        for tag in tags:
            tag_lower = tag["tag"].lower()
            for keyword in kayak_tag_keywords:
                if keyword in tag_lower:
                    filtered_tags.append(tag)
                    break

        logger.info(f"Kayak: extracted {len(filtered_tags)} tags for {city_name}")
        return filtered_tags
