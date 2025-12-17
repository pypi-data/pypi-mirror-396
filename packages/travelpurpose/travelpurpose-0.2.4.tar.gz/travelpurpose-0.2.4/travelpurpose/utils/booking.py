"""
Booking.com harvester for city tags.

Uses public sitemaps and structured data (JSON-LD) only.
Absolutely NO login or private APIs.
"""

import logging

from travelpurpose.utils.harvest import BaseHarvester, safe_harvest

logger = logging.getLogger(__name__)


class BookingHarvester(BaseHarvester):
    """Harvester for Booking.com public data."""

    BASE_URL = "https://www.booking.com"

    @safe_harvest
    def get_city_tags(self, city_name: str, country: str = "") -> list[dict]:
        """
        Get tags for a city from Booking.com public pages.

        Args:
            city_name: City name
            country: Optional country name

        Returns:
            List of tag dictionaries
        """
        tags = []

        # Construct city search URL
        search_query = f"{city_name} {country}".strip().replace(" ", "-").lower()
        url = f"{self.BASE_URL}/city/{search_query}.html"

        # Extract tags from page
        page_tags = self.extract_tags_from_page(url, city_name, "booking")
        tags.extend(page_tags)

        # Common Booking.com tag patterns to look for
        booking_tag_keywords = [
            "business-friendly",
            "family-friendly",
            "pet-friendly",
            "beachfront",
            "city centre",
            "city center",
            "old town",
            "spa",
            "wellness",
            "ski-in ski-out",
            "convention center",
            "good for couples",
            "romantic",
            "luxury",
        ]

        # Filter and normalize tags
        filtered_tags = []
        for tag in tags:
            tag_lower = tag["tag"].lower()
            for keyword in booking_tag_keywords:
                if keyword in tag_lower:
                    filtered_tags.append(tag)
                    break

        logger.info(f"Booking.com: extracted {len(filtered_tags)} tags for {city_name}")
        return filtered_tags
