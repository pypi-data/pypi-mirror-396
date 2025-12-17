"""
Wikidata integration for canonical city data.

Fetches city information including names, coordinates, population, country, etc.
"""

import logging
import time

from SPARQLWrapper import JSON, SPARQLWrapper

logger = logging.getLogger(__name__)


class WikidataClient:
    """Client for querying Wikidata for city information."""

    SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
    USER_AGENT = (
        "TravelPurpose/0.1.0 (https://github.com/teyfikoz/Travel_Purpose-City_Tags)"
    )

    def __init__(self, rate_limit: float = 1.0):
        """
        Initialize Wikidata client.

        Args:
            rate_limit: Minimum seconds between requests (default 1.0)
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0.0
        self.sparql = SPARQLWrapper(self.SPARQL_ENDPOINT)
        self.sparql.setReturnFormat(JSON)
        self.sparql.addCustomHttpHeader("User-Agent", self.USER_AGENT)

    def _rate_limit_wait(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def query(self, sparql_query: str) -> list[dict]:
        """
        Execute a SPARQL query against Wikidata.

        Args:
            sparql_query: SPARQL query string

        Returns:
            List of result bindings
        """
        self._rate_limit_wait()

        try:
            self.sparql.setQuery(sparql_query)
            results = self.sparql.query().convert()
            return results.get("results", {}).get("bindings", [])
        except Exception as e:
            logger.error(f"Wikidata query failed: {e}")
            return []

    def get_cities_by_population(
        self, min_population: int = 100000, limit: int = 5000
    ) -> list[dict]:
        """
        Fetch cities with population above threshold.

        Args:
            min_population: Minimum population threshold
            limit: Maximum number of results

        Returns:
            List of city dictionaries with name, country, coordinates, population
        """
        query = f"""
        SELECT DISTINCT ?city ?cityLabel ?countryLabel ?population ?lat ?lon ?wikidataId
        WHERE {{
          ?city wdt:P31/wdt:P279* wd:Q515 .  # instance of city
          ?city wdt:P1082 ?population .       # has population
          ?city wdt:P17 ?country .             # in country
          ?city wdt:P625 ?coords .             # has coordinates

          FILTER (?population >= {min_population})

          BIND(geof:latitude(?coords) AS ?lat)
          BIND(geof:longitude(?coords) AS ?lon)
          BIND(REPLACE(STR(?city), "http://www.wikidata.org/entity/", "") AS ?wikidataId)

          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,fr,es,de,it,ar,tr,ru,zh,ja". }}
        }}
        ORDER BY DESC(?population)
        LIMIT {limit}
        """

        results = self.query(query)

        cities = []
        for result in results:
            try:
                city_data = {
                    "name": result["cityLabel"]["value"],
                    "country": result["countryLabel"]["value"],
                    "population": int(result["population"]["value"]),
                    "latitude": float(result["lat"]["value"]),
                    "longitude": float(result["lon"]["value"]),
                    "wikidata_id": result["wikidataId"]["value"],
                    "source": "wikidata",
                }
                cities.append(city_data)
            except (KeyError, ValueError) as e:
                logger.debug(f"Skipping incomplete city result: {e}")
                continue

        logger.info(f"Fetched {len(cities)} cities from Wikidata")
        return cities

    def get_city_by_name(
        self, city_name: str, country: str | None = None
    ) -> dict | None:
        """
        Search for a specific city by name.

        Args:
            city_name: City name to search for
            country: Optional country name to narrow search

        Returns:
            City dictionary or None if not found
        """
        country_filter = ""
        if country:
            country_filter = (
                f'?city wdt:P17 ?country . ?country rdfs:label "{country}"@en .'
            )

        query = f"""
        SELECT DISTINCT ?city ?cityLabel ?countryLabel ?population ?lat ?lon ?wikidataId
        WHERE {{
          ?city wdt:P31/wdt:P279* wd:Q515 .
          ?city rdfs:label "{city_name}"@en .
          {country_filter}
          OPTIONAL {{ ?city wdt:P1082 ?population . }}
          OPTIONAL {{
            ?city wdt:P625 ?coords .
            BIND(geof:latitude(?coords) AS ?lat)
            BIND(geof:longitude(?coords) AS ?lon)
          }}
          ?city wdt:P17 ?country .
          BIND(REPLACE(STR(?city), "http://www.wikidata.org/entity/", "") AS ?wikidataId)

          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 1
        """

        results = self.query(query)

        if not results:
            return None

        result = results[0]
        try:
            return {
                "name": result["cityLabel"]["value"],
                "country": result["countryLabel"]["value"],
                "population": int(result.get("population", {}).get("value", 0)),
                "latitude": float(result.get("lat", {}).get("value", 0.0)),
                "longitude": float(result.get("lon", {}).get("value", 0.0)),
                "wikidata_id": result["wikidataId"]["value"],
                "source": "wikidata",
            }
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse city data: {e}")
            return None

    def get_unesco_sites(self) -> list[dict]:
        """
        Fetch UNESCO World Heritage Sites and their cities.

        Returns:
            List of UNESCO sites with city associations
        """
        query = """
        SELECT DISTINCT ?site ?siteLabel ?cityLabel ?countryLabel ?wikidataId
        WHERE {
          ?site wdt:P1435 wd:Q9259 .  # UNESCO World Heritage Site
          ?site wdt:P131* ?city .      # located in city (including administrative divisions)
          ?city wdt:P31/wdt:P279* wd:Q515 .  # city
          ?city wdt:P17 ?country .     # country
          BIND(REPLACE(STR(?city), "http://www.wikidata.org/entity/", "") AS ?wikidataId)

          SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
        LIMIT 1000
        """

        results = self.query(query)

        sites = []
        for result in results:
            try:
                site_data = {
                    "site_name": result["siteLabel"]["value"],
                    "city": result["cityLabel"]["value"],
                    "country": result["countryLabel"]["value"],
                    "wikidata_id": result["wikidataId"]["value"],
                    "tag": "UNESCO_Site",
                    "source": "wikidata",
                }
                sites.append(site_data)
            except KeyError:
                continue

        logger.info(f"Fetched {len(sites)} UNESCO sites from Wikidata")
        return sites

    def get_city_categories(self, wikidata_id: str) -> list[str]:
        """
        Get Wikipedia categories for a city.

        Args:
            wikidata_id: Wikidata ID (e.g., "Q406")

        Returns:
            List of category names
        """
        query = f"""
        SELECT ?categoryLabel
        WHERE {{
          wd:{wikidata_id} wdt:P31/wdt:P279* wd:Q515 .
          wd:{wikidata_id} wdt:P910 ?category .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 100
        """

        results = self.query(query)
        categories = [
            r["categoryLabel"]["value"] for r in results if "categoryLabel" in r
        ]
        return categories


def fetch_canonical_cities(
    min_population: int = 100000, cache_file: str | None = None
) -> list[dict]:
    """
    Fetch canonical city list from Wikidata with caching.

    Args:
        min_population: Minimum population threshold
        cache_file: Optional path to cache file

    Returns:
        List of city dictionaries
    """
    import json
    import os

    # Try to load from cache first
    if cache_file and os.path.exists(cache_file):
        try:
            with open(cache_file, encoding="utf-8") as f:
                cities = json.load(f)
            logger.info(f"Loaded {len(cities)} cities from cache: {cache_file}")
            return cities
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")

    # Fetch from Wikidata
    client = WikidataClient()
    cities = client.get_cities_by_population(min_population=min_population)

    # Save to cache
    if cache_file and cities:
        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cities, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(cities)} cities to cache: {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    return cities
