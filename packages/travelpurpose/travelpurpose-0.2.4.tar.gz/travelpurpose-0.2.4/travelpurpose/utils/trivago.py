"""
Trivago harvester for city tags.

Uses public landing pages and structured data.
Respects robots.txt.
"""

import logging

from travelpurpose.utils.harvest import BaseHarvester, safe_harvest

logger = logging.getLogger(__name__)


class TrivagoHarvester(BaseHarvester):
    """Harvester for Trivago public data."""

    BASE_URL = "https://www.trivago.com"

    @safe_harvest
    def get_city_tags(self, city_name: str, country: str = "") -> list[dict]:
        """
        Get tags for a city from Trivago public pages.

        Args:
            city_name: City name
            country: Optional country name

        Returns:
            List of tag dictionaries
        """
        tags = []

        # Construct city URL
        search_query = f"{city_name}-{country}".strip().replace(" ", "-").lower()
        url = f"{self.BASE_URL}/en-US/city/{search_query}"

        # Extract tags from page
        page_tags = self.extract_tags_from_page(url, city_name, "trivago")
        tags.extend(page_tags)

        # Common Trivago tag patterns
        trivago_tag_keywords = [
            "city center",
            "old town",
            "beach district",
            "ski region",
            "conference",
            "business district",
            "historic",
            "shopping",
        ]

        # Filter tags
        filtered_tags = []
        for tag in tags:
            tag_lower = tag["tag"].lower()
            for keyword in trivago_tag_keywords:
                if keyword in tag_lower:
                    filtered_tags.append(tag)
                    break

        logger.info(f"Trivago: extracted {len(filtered_tags)} tags for {city_name}")
        return filtered_tags
