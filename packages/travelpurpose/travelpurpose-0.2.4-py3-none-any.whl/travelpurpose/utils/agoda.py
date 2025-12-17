"""
Agoda harvester for city tags.

Uses public sitemaps and structured data only.
Respects robots.txt.
"""

import logging

from travelpurpose.utils.harvest import BaseHarvester, safe_harvest

logger = logging.getLogger(__name__)


class AgodaHarvester(BaseHarvester):
    """Harvester for Agoda public data."""

    BASE_URL = "https://www.agoda.com"

    @safe_harvest
    def get_city_tags(self, city_name: str, country: str = "") -> list[dict]:
        """
        Get tags for a city from Agoda public pages.

        Args:
            city_name: City name
            country: Optional country name

        Returns:
            List of tag dictionaries
        """
        tags = []

        # Construct city guide URL
        search_query = f"{city_name}-{country}".strip().replace(" ", "-").lower()
        url = f"{self.BASE_URL}/city/{search_query}"

        # Extract tags from page
        page_tags = self.extract_tags_from_page(url, city_name, "agoda")
        tags.extend(page_tags)

        # Common Agoda tag patterns
        agoda_tag_keywords = [
            "business",
            "family",
            "airport shuttle",
            "beach access",
            "wellness",
            "spa",
            "shopping",
            "nightlife",
            "cultural",
        ]

        # Filter tags
        filtered_tags = []
        for tag in tags:
            tag_lower = tag["tag"].lower()
            for keyword in agoda_tag_keywords:
                if keyword in tag_lower:
                    filtered_tags.append(tag)
                    break

        logger.info(f"Agoda: extracted {len(filtered_tags)} tags for {city_name}")
        return filtered_tags
