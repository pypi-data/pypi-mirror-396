"""
Skyscanner harvester for city data and tags.

Uses public autosuggest/locations endpoints within ToS.
"""

import logging

from travelpurpose.utils.harvest import BaseHarvester, safe_harvest

logger = logging.getLogger(__name__)


class SkyscannerHarvester(BaseHarvester):
    """Harvester for Skyscanner public endpoints."""

    AUTOSUGGEST_URL = "https://www.skyscanner.net/g/autosuggest-flights/api/v1/search"

    @safe_harvest
    def search_city(self, query: str) -> list[dict]:
        """
        Search for cities using autosuggest endpoint.

        Args:
            query: City name to search

        Returns:
            List of city results
        """
        params = {
            "query": query,
            "limit": 10,
            "isDestination": True,
        }

        response = self.get(self.AUTOSUGGEST_URL, params=params)
        if not response:
            return []

        try:
            data = response.json()
            cities = []

            for item in data.get("places", []):
                if item.get("type") in ["CITY", "PLACE"]:
                    city_data = {
                        "name": item.get("name"),
                        "country": item.get("countryName"),
                        "iata": item.get("iata"),
                        "city_id": item.get("cityId"),
                        "source": "skyscanner",
                    }
                    cities.append(city_data)

            logger.info(f"Skyscanner found {len(cities)} cities for query: {query}")
            return cities

        except Exception as e:
            logger.error(f"Failed to parse Skyscanner response: {e}")
            return []

    @safe_harvest
    def get_city_tags(self, city_name: str) -> list[dict]:
        """
        Get tags for a city (placeholder - Skyscanner has limited public tag data).

        Args:
            city_name: City name

        Returns:
            List of tag dictionaries
        """
        # Skyscanner's main value is in city name normalization and IATA codes
        # Limited tag data available from public endpoints
        tags = []

        city_results = self.search_city(city_name)
        if not city_results:
            return tags

        # Extract any implicit tags from city type
        for city in city_results:
            if city.get("iata"):
                tags.append(
                    {
                        "city": city["name"],
                        "tag": "airport",
                        "source": "skyscanner",
                        "source_url": self.AUTOSUGGEST_URL,
                        "evidence_type": "api",
                        "metadata": {"iata": city["iata"]},
                    }
                )

        return tags
