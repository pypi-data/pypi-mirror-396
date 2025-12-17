"""
OpenTripMap API harvester for tourist attractions and POIs.

OpenTripMap provides:
- Tourist attractions
- Landmarks
- Museums, galleries
- Natural features
- Entertainment venues
"""

import logging

from travelpurpose.utils.harvest import BaseHarvester, HarvestConfig

logger = logging.getLogger(__name__)


class OpenTripMapHarvester(BaseHarvester):
    """
    Harvester for OpenTripMap API.

    Free API key available at: https://opentripmap.io/
    """

    BASE_URL = "https://api.opentripmap.com/0.1/en/places"

    def __init__(self, config: HarvestConfig, api_key: str = ""):
        """
        Initialize OpenTripMap harvester.

        Args:
            config: Harvest configuration
            api_key: API key (required, get from opentripmap.io)
        """
        super().__init__(config)
        self.api_key = (
            api_key or "5ae2e3f221c38a28845f05b63c6dd2a1fe9b3f3e5d7e3b9e8b6d3f9e"
        )  # Demo key

    def get_city_tags(self, city_name: str, country: str = "") -> list[dict]:
        """
        Get tags from OpenTripMap for a city.

        Args:
            city_name: City name
            country: Country name

        Returns:
            List of tag dictionaries
        """
        tags = []

        try:
            # Get city coordinates first (using geoname)
            coords = self._get_city_coordinates(city_name)

            if not coords:
                return tags

            lat, lon = coords

            # Get POIs in radius
            pois = self._get_nearby_pois(lat, lon, radius=5000)  # 5km radius

            # Process POIs and extract tags
            for poi in pois:
                poi_tags = self._extract_tags_from_poi(poi)
                tags.extend(poi_tags)

            # Deduplicate tags
            seen = set()
            unique_tags = []
            for tag in tags:
                key = (tag["tag"], tag.get("evidence_type", ""))
                if key not in seen:
                    seen.add(key)
                    unique_tags.append(tag)

            logger.debug(f"OpenTripMap: Found {len(unique_tags)} tags for {city_name}")
            return unique_tags

        except Exception as e:
            logger.warning(f"OpenTripMap error for {city_name}: {e}")

        return tags

    def _get_city_coordinates(self, city_name: str) -> tuple | None:
        """Get city coordinates using geoname search."""
        try:
            params = {"name": city_name, "apikey": self.api_key}

            response = self._make_request(f"{self.BASE_URL}/geoname", params=params)

            if response and "lat" in response and "lon" in response:
                return (response["lat"], response["lon"])

        except Exception as e:
            logger.debug(f"Failed to get coordinates: {e}")

        return None

    def _get_nearby_pois(
        self, lat: float, lon: float, radius: int = 5000
    ) -> list[dict]:
        """Get POIs near coordinates."""
        pois = []

        try:
            params = {
                "radius": radius,
                "lon": lon,
                "lat": lat,
                "limit": 100,
                "apikey": self.api_key,
            }

            response = self._make_request(f"{self.BASE_URL}/radius", params=params)

            if response and isinstance(response, list):
                pois = response

        except Exception as e:
            logger.debug(f"Failed to get nearby POIs: {e}")

        return pois

    def _extract_tags_from_poi(self, poi: dict) -> list[dict]:
        """Extract travel purpose tags from POI data."""
        tags = []

        kinds = poi.get("kinds", "")
        if not kinds:
            return tags

        kind_list = kinds.split(",")

        for kind in kind_list:
            kind = kind.strip()

            # Museums & Culture
            if "museum" in kind or "galleries" in kind:
                tags.append(
                    {
                        "tag": "museum",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )
                tags.append(
                    {
                        "tag": "culture",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )

            # Architecture & Heritage
            if "architecture" in kind or "historic" in kind or "archaeology" in kind:
                tags.append(
                    {
                        "tag": "architecture",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )
                tags.append(
                    {
                        "tag": "heritage",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )

            # Religious
            if "religion" in kind or "churches" in kind or "mosques" in kind:
                tags.append(
                    {
                        "tag": "religious",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )

            # Nature
            if (
                "natural" in kind
                or "geological_formations" in kind
                or "nature_reserves" in kind
            ):
                tags.append(
                    {
                        "tag": "nature",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )

            # Beaches
            if "beaches" in kind or "coastal" in kind:
                tags.append(
                    {
                        "tag": "beach",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )

            # Sport & Adventure
            if "sport" in kind or "climbing" in kind or "diving" in kind:
                tags.append(
                    {
                        "tag": "adventure",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )

            # Amusement & Family
            if "amusements" in kind or "zoo" in kind or "aquarium" in kind:
                tags.append(
                    {
                        "tag": "family",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )

            # Entertainment & Nightlife
            if "entertainment" in kind or "theatres" in kind or "cinemas" in kind:
                tags.append(
                    {
                        "tag": "entertainment",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )

            # Shopping
            if "shops" in kind or "malls" in kind:
                tags.append(
                    {
                        "tag": "shopping",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )

            # Food
            if "foods" in kind or "restaurants" in kind:
                tags.append(
                    {
                        "tag": "gastronomy",
                        "source": "opentripmap",
                        "evidence_type": "poi_kind",
                    }
                )

        return tags
