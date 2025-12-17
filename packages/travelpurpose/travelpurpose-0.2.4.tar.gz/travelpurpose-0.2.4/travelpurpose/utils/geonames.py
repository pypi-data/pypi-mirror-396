"""
GeoNames API harvester for city geographic and tag data.

GeoNames provides:
- City coordinates and elevation
- Population data
- Administrative divisions
- Feature codes (tourism, culture, etc.)
"""

import logging

from travelpurpose.utils.harvest import BaseHarvester, HarvestConfig

logger = logging.getLogger(__name__)


class GeoNamesHarvester(BaseHarvester):
    """
    Harvester for GeoNames API.

    Note: Using free API (no key required) with rate limiting.
    For production, register for a username at geonames.org
    """

    BASE_URL = "http://api.geonames.org"

    def __init__(self, config: HarvestConfig, username: str = "demo"):
        """
        Initialize GeoNames harvester.

        Args:
            config: Harvest configuration
            username: GeoNames username (default: demo, rate limited)
        """
        super().__init__(config)
        self.username = username

    def get_city_tags(self, city_name: str, country: str = "") -> list[dict]:
        """
        Get tags from GeoNames for a city.

        Args:
            city_name: City name
            country: Country name

        Returns:
            List of tag dictionaries
        """
        tags = []

        try:
            # Search for city
            city_data = self._search_city(city_name, country)

            if not city_data:
                return tags

            # Extract feature code tags
            feature_code = city_data.get("fcode", "")
            feature_class = city_data.get("fclass", "")

            # Map feature codes to travel purpose tags
            if feature_code:
                feature_tags = self._map_feature_code(feature_code, feature_class)
                tags.extend(feature_tags)

            # Get nearby features (POIs, attractions)
            geoname_id = city_data.get("geonameId")
            if geoname_id:
                nearby_tags = self._get_nearby_features(geoname_id)
                tags.extend(nearby_tags)

            logger.debug(f"GeoNames: Found {len(tags)} tags for {city_name}")

        except Exception as e:
            logger.warning(f"GeoNames error for {city_name}: {e}")

        return tags

    def _search_city(self, city_name: str, country: str) -> dict | None:
        """Search for city in GeoNames."""
        params = {
            "q": city_name,
            "maxRows": 5,
            "featureClass": "P",  # Populated places
            "username": self.username,
            "type": "json",
        }

        if country:
            params["country"] = country[:2].upper()  # ISO country code

        response = self._make_request(f"{self.BASE_URL}/searchJSON", params=params)

        if response and "geonames" in response and len(response["geonames"]) > 0:
            # Return first result (usually most relevant)
            return response["geonames"][0]

        return None

    def _get_nearby_features(self, geoname_id: int) -> list[dict]:
        """Get nearby features (attractions, landmarks)."""
        tags = []

        try:
            params = {
                "geonameId": geoname_id,
                "radius": 20,  # 20km radius
                "maxRows": 50,
                "username": self.username,
            }

            response = self._make_request(
                f"{self.BASE_URL}/findNearbyJSON", params=params
            )

            if response and "geonames" in response:
                for feature in response["geonames"]:
                    fcode = feature.get("fcode", "")
                    fclass = feature.get("fclass", "")

                    feature_tags = self._map_feature_code(fcode, fclass)
                    tags.extend(feature_tags)

        except Exception as e:
            logger.debug(f"Failed to get nearby features: {e}")

        return tags

    def _map_feature_code(self, fcode: str, fclass: str) -> list[dict]:
        """
        Map GeoNames feature codes to travel purpose tags.

        Feature classes:
        - A: Administrative
        - H: Hydrographic (water)
        - L: Area
        - P: Populated place
        - R: Roads/Railways
        - S: Spots/Buildings
        - T: Terrain
        - U: Undersea
        - V: Vegetation
        """
        tags = []

        # Culture & Heritage
        if fcode in [
            "MUS",
            "MNMT",
            "ANS",
            "HSTS",
        ]:  # Museum, Monument, Ancient site, Historical site
            tags.append(
                {
                    "tag": "historic",
                    "source": "geonames",
                    "evidence_type": "feature_code",
                    "detail": fcode,
                }
            )
            tags.append(
                {
                    "tag": "cultural",
                    "source": "geonames",
                    "evidence_type": "feature_code",
                }
            )

        # Religious
        if fcode in ["MSQE", "CH", "TMPL", "SHRN"]:  # Mosque, Church, Temple, Shrine
            tags.append(
                {
                    "tag": "religious",
                    "source": "geonames",
                    "evidence_type": "feature_code",
                }
            )

        # Beach & Coast
        if fcode in ["BCH", "BCHS", "COVE"]:  # Beach
            tags.append(
                {"tag": "beach", "source": "geonames", "evidence_type": "feature_code"}
            )

        # Island
        if fcode in ["ISL", "ISLS", "ATOL"]:  # Island, Islands, Atoll
            tags.append(
                {"tag": "island", "source": "geonames", "evidence_type": "feature_code"}
            )

        # Mountain / Trekking
        if fcode in ["MT", "MTS", "PK"]:  # Mountain, Mountains, Peak
            tags.append(
                {
                    "tag": "mountain",
                    "source": "geonames",
                    "evidence_type": "feature_code",
                }
            )
            tags.append(
                {
                    "tag": "trekking",
                    "source": "geonames",
                    "evidence_type": "feature_code",
                }
            )

        # Ski Resort
        if fcode == "RESW":  # Winter resort
            tags.append(
                {"tag": "ski", "source": "geonames", "evidence_type": "feature_code"}
            )

        # Airport
        if fcode in ["AIRP", "AIRF"]:  # Airport
            tags.append(
                {
                    "tag": "airport",
                    "source": "geonames",
                    "evidence_type": "feature_code",
                }
            )

        # Port
        if fcode in ["PRT", "PRTF"]:  # Port, Free port
            tags.append(
                {"tag": "port", "source": "geonames", "evidence_type": "feature_code"}
            )

        # Casino
        if fcode == "CSNO":
            tags.append(
                {"tag": "casino", "source": "geonames", "evidence_type": "feature_code"}
            )

        # Hospital / Medical
        if fcode in ["HSP", "HSPC", "HSPD"]:  # Hospital
            tags.append(
                {
                    "tag": "medical",
                    "source": "geonames",
                    "evidence_type": "feature_code",
                }
            )

        # Theme Park / Zoo
        if fcode in ["AMTH", "ZOO"]:  # Amphitheater, Zoo
            tags.append(
                {"tag": "family", "source": "geonames", "evidence_type": "feature_code"}
            )

        # Resort
        if fcode in [
            "RESH",
            "REST",
            "RESV",
        ]:  # Health resort, Tourist resort, Vacation resort
            tags.append(
                {"tag": "resort", "source": "geonames", "evidence_type": "feature_code"}
            )

        # Spa
        if fcode in ["SPNT", "SPA"]:  # Hot spring, Spa
            tags.append(
                {"tag": "spa", "source": "geonames", "evidence_type": "feature_code"}
            )
            tags.append(
                {
                    "tag": "wellness",
                    "source": "geonames",
                    "evidence_type": "feature_code",
                }
            )

        return tags
