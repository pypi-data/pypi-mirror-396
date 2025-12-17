"""
Tag extraction and management module.

Provides functions for harvesting and retrieving tags for cities.
"""

import logging

import pandas as pd

from travelpurpose.utils.agoda import AgodaHarvester
from travelpurpose.utils.booking import BookingHarvester
from travelpurpose.utils.harvest import HarvestConfig
from travelpurpose.utils.io import load_cities_data
from travelpurpose.utils.kayak import KayakHarvester
from travelpurpose.utils.normalize import normalize_city_name
from travelpurpose.utils.skyscanner import SkyscannerHarvester
from travelpurpose.utils.tripdotcom import TripDotComHarvester
from travelpurpose.utils.trivago import TrivagoHarvester
from travelpurpose.utils.wikidata import WikidataClient

logger = logging.getLogger(__name__)

# Global cache
_TAGS_CACHE: pd.DataFrame | None = None


def get_tags_for_city(
    city_name: str,
    sources: list[str] | None = None,
    use_cache: bool = True,
) -> list[dict]:
    """
    Get all tags for a city from various sources.

    Args:
        city_name: City name to search for
        sources: List of source names to use (default: all)
        use_cache: Whether to use cached data first

    Returns:
        List of tag dictionaries with source information
    """
    global _TAGS_CACHE

    # Try cache first
    if use_cache and _TAGS_CACHE is not None:
        city_norm = normalize_city_name(city_name)
        matches = _TAGS_CACHE[
            _TAGS_CACHE["city"].str.lower().apply(normalize_city_name) == city_norm
        ]
        if len(matches) > 0:
            return matches.to_dict("records")

    # Default sources
    if sources is None:
        sources = [
            "wikidata",
            "booking",
            "agoda",
            "trivago",
            "kayak",
            "tripdotcom",
            "skyscanner",
        ]

    all_tags = []
    config = HarvestConfig(
        rate_limit=1.0, timeout=3, max_retries=1
    )  # Faster configuration

    # Harvest from each source
    if "wikidata" in sources:
        try:
            client = WikidataClient(rate_limit=1.5)
            city_data = client.get_city_by_name(city_name)
            if city_data:
                wikidata_id = city_data.get("wikidata_id")
                if wikidata_id:
                    categories = client.get_city_categories(wikidata_id)
                    for cat in categories:
                        all_tags.append(
                            {
                                "city": city_name,
                                "tag": cat,
                                "source": "wikidata",
                                "source_url": f"https://www.wikidata.org/wiki/{wikidata_id}",
                                "evidence_type": "category",
                            }
                        )
        except Exception as e:
            logger.warning(f"Wikidata harvest failed for {city_name}: {e}")

    if "booking" in sources:
        try:
            harvester = BookingHarvester(config)
            tags = harvester.get_city_tags(city_name)
            all_tags.extend(tags)
        except Exception as e:
            logger.warning(f"Booking harvest failed for {city_name}: {e}")

    if "agoda" in sources:
        try:
            harvester = AgodaHarvester(config)
            tags = harvester.get_city_tags(city_name)
            all_tags.extend(tags)
        except Exception as e:
            logger.warning(f"Agoda harvest failed for {city_name}: {e}")

    if "trivago" in sources:
        try:
            harvester = TrivagoHarvester(config)
            tags = harvester.get_city_tags(city_name)
            all_tags.extend(tags)
        except Exception as e:
            logger.warning(f"Trivago harvest failed for {city_name}: {e}")

    if "kayak" in sources:
        try:
            harvester = KayakHarvester(config)
            tags = harvester.get_city_tags(city_name)
            all_tags.extend(tags)
        except Exception as e:
            logger.warning(f"Kayak harvest failed for {city_name}: {e}")

    if "tripdotcom" in sources:
        try:
            harvester = TripDotComHarvester(config)
            tags = harvester.get_city_tags(city_name)
            all_tags.extend(tags)
        except Exception as e:
            logger.warning(f"Trip.com harvest failed for {city_name}: {e}")

    if "skyscanner" in sources:
        try:
            harvester = SkyscannerHarvester(config)
            tags = harvester.get_city_tags(city_name)
            all_tags.extend(tags)
        except Exception as e:
            logger.warning(f"Skyscanner harvest failed for {city_name}: {e}")

    logger.info(f"Harvested {len(all_tags)} total tags for {city_name}")
    return all_tags


def load_tags_cache():
    """Load tags from cached dataset."""
    global _TAGS_CACHE

    df = load_cities_data()
    if df is not None and "tags" in df.columns:
        # Expand tags if stored as list/dict
        tag_records = []
        for _, row in df.iterrows():
            city = row.get("name", "")
            tags = row.get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, dict):
                        tag_records.append({**tag, "city": city})
                    else:
                        tag_records.append(
                            {"city": city, "tag": str(tag), "source": "cached"}
                        )

        if tag_records:
            _TAGS_CACHE = pd.DataFrame(tag_records)
            logger.info(f"Loaded {len(_TAGS_CACHE)} tags from cache")
    else:
        logger.warning("No cached tags data available")
