"""
Trip.com harvester for city tags.

Uses public location search and landing pages.
"""

import logging

from travelpurpose.utils.harvest import BaseHarvester, safe_harvest

logger = logging.getLogger(__name__)


class TripDotComHarvester(BaseHarvester):
    """Harvester for Trip.com public data."""

    BASE_URL = "https://us.trip.com"

    @safe_harvest
    def get_city_tags(self, city_name: str, country: str = "") -> list[dict]:
        """
        Get tags for a city from Trip.com public pages.

        Args:
            city_name: City name
            country: Optional country name

        Returns:
            List of tag dictionaries
        """
        tags = []

        # Construct city URL
        search_query = f"{city_name}-{country}".strip().replace(" ", "-").lower()
        url = f"{self.BASE_URL}/things-to-do/{search_query}"

        # Extract tags from page
        page_tags = self.extract_tags_from_page(url, city_name, "tripdotcom")
        tags.extend(page_tags)

        # Common Trip.com tag patterns
        trip_tag_keywords = [
            "family",
            "business",
            "cultural",
            "historical",
            "beach",
            "shopping",
            "food",
            "nightlife",
            "adventure",
        ]

        # Filter tags
        filtered_tags = []
        for tag in tags:
            tag_lower = tag["tag"].lower()
            for keyword in trip_tag_keywords:
                if keyword in tag_lower:
                    filtered_tags.append(tag)
                    break

        logger.info(f"Trip.com: extracted {len(filtered_tags)} tags for {city_name}")
        return filtered_tags
