"""
Base harvesting utilities for compliant web data collection.

Provides rate limiting, caching, robots.txt compliance, and error handling.
"""

import logging
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
import requests_cache
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HarvestConfig:
    """Configuration for web harvesting."""

    def __init__(
        self,
        rate_limit: float = 1.0,
        timeout: int = 5,
        max_retries: int = 2,
        retry_backoff: float = 1.5,
        cache_ttl: int = 86400,  # 24 hours
        user_agent: str = "TravelPurpose/0.2.0 (https://github.com/teyfikoz/Travel_Purpose-City_Tags)",
        respect_robots_txt: bool = True,
    ):
        """
        Initialize harvest configuration.

        Args:
            rate_limit: Minimum seconds between requests per domain
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_backoff: Exponential backoff multiplier
            cache_ttl: Cache time-to-live in seconds
            user_agent: User agent string
            respect_robots_txt: Whether to respect robots.txt
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.cache_ttl = cache_ttl
        self.user_agent = user_agent
        self.respect_robots_txt = respect_robots_txt


class BaseHarvester:
    """Base class for web harvesters with rate limiting and caching."""

    def __init__(self, config: HarvestConfig | None = None):
        """
        Initialize harvester.

        Args:
            config: Harvest configuration
        """
        self.config = config or HarvestConfig()
        self.last_request_time: dict[str, float] = {}
        self.robots_cache: dict[str, RobotFileParser] = {}

        # Setup session with caching
        from travelpurpose.utils.io import get_cache_dir

        cache_file = str(get_cache_dir() / "http_cache")
        requests_cache.install_cache(
            cache_file,
            backend="sqlite",
            expire_after=self.config.cache_ttl,
        )

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.config.user_agent})

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        return urlparse(url).netloc

    def _rate_limit_wait(self, domain: str):
        """Enforce rate limiting per domain."""
        last_time = self.last_request_time.get(domain, 0)
        elapsed = time.time() - last_time

        if elapsed < self.config.rate_limit:
            wait_time = self.config.rate_limit - elapsed
            logger.debug(f"Rate limiting {domain}: waiting {wait_time:.2f}s")
            time.sleep(wait_time)

        self.last_request_time[domain] = time.time()

    def _check_robots_txt(self, url: str) -> bool:
        """
        Check if URL is allowed by robots.txt.

        Args:
            url: URL to check

        Returns:
            True if allowed, False otherwise
        """
        if not self.config.respect_robots_txt:
            return True

        parsed = urlparse(url)
        domain = parsed.netloc
        robots_url = f"{parsed.scheme}://{domain}/robots.txt"

        # Check cache
        if domain not in self.robots_cache:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
                self.robots_cache[domain] = rp
            except Exception as e:
                logger.warning(f"Failed to read robots.txt for {domain}: {e}")
                # If robots.txt can't be read, assume allowed
                return True

        rp = self.robots_cache[domain]
        allowed = rp.can_fetch(self.config.user_agent, url)

        if not allowed:
            logger.warning(f"URL blocked by robots.txt: {url}")

        return allowed

    def get(self, url: str, **kwargs) -> requests.Response | None:
        """
        Make GET request with rate limiting and retries.

        Args:
            url: URL to fetch
            **kwargs: Additional requests.get arguments

        Returns:
            Response object or None on failure
        """
        # Check robots.txt
        if not self._check_robots_txt(url):
            return None

        domain = self._get_domain(url)
        self._rate_limit_wait(domain)

        kwargs.setdefault("timeout", self.config.timeout)

        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(url, **kwargs)
                response.raise_for_status()
                return response

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Too Many Requests
                    wait_time = self.config.retry_backoff ** (attempt + 1)
                    logger.warning(f"Rate limited (429) on {url}, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                elif e.response.status_code >= 500:
                    wait_time = self.config.retry_backoff**attempt
                    logger.warning(
                        f"Server error {e.response.status_code} on {url}, retrying in {wait_time}s"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"HTTP error fetching {url}: {e}")
                    return None

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching {url}, attempt {attempt + 1}")
                continue

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error fetching {url}: {e}")
                return None

        logger.error(f"Failed to fetch {url} after {self.config.max_retries} attempts")
        return None

    def _make_request(self, url: str, params: dict | None = None) -> dict | None:
        """
        Make GET request and return JSON response.

        Args:
            url: URL to fetch
            params: Query parameters

        Returns:
            JSON response as dictionary or None on failure
        """
        response = self.get(url, params=params)

        if not response:
            return None

        try:
            return response.json()
        except ValueError as e:
            logger.error(f"Failed to parse JSON from {url}: {e}")
            return None

    def parse_html(self, html_content: str) -> BeautifulSoup | None:
        """
        Parse HTML content.

        Args:
            html_content: HTML string

        Returns:
            BeautifulSoup object or None
        """
        try:
            return BeautifulSoup(html_content, "lxml")
        except Exception as e:
            logger.error(f"Failed to parse HTML: {e}")
            return None

    def extract_tags_from_page(
        self, url: str, city: str, source: str
    ) -> list[dict[str, str]]:
        """
        Extract tags from a web page.

        Args:
            url: URL to fetch
            city: City name
            source: Source identifier

        Returns:
            List of tag dictionaries
        """
        response = self.get(url)
        if not response:
            return []

        soup = self.parse_html(response.text)
        if not soup:
            return []

        tags = []

        # Extract from JSON-LD
        from travelpurpose.utils.normalize import parse_json_ld

        json_ld_objects = parse_json_ld(response.text)
        for obj in json_ld_objects:
            if isinstance(obj, dict):
                # Extract relevant properties
                if "keywords" in obj:
                    keywords = obj["keywords"]
                    if isinstance(keywords, str):
                        keywords = [k.strip() for k in keywords.split(",")]
                    for kw in keywords:
                        tags.append(
                            {
                                "city": city,
                                "tag": kw,
                                "source": source,
                                "source_url": url,
                                "evidence_type": "jsonld",
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            }
                        )

        # Extract from meta tags
        from travelpurpose.utils.normalize import extract_meta_tags

        meta_tags = extract_meta_tags(response.text)
        for name, content in meta_tags.items():
            if "keyword" in name.lower() or "description" in name.lower():
                keywords = [k.strip() for k in content.split(",")]
                for kw in keywords:
                    if kw and len(kw) > 2:
                        tags.append(
                            {
                                "city": city,
                                "tag": kw,
                                "source": source,
                                "source_url": url,
                                "evidence_type": "meta",
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            }
                        )

        # Extract from headings
        from travelpurpose.utils.normalize import extract_headings

        headings = extract_headings(response.text)
        for heading in headings:
            # Extract keywords from headings
            from travelpurpose.utils.normalize import extract_keywords

            keywords = extract_keywords(heading)
            for kw in keywords:
                tags.append(
                    {
                        "city": city,
                        "tag": kw,
                        "source": source,
                        "source_url": url,
                        "evidence_type": "heading",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

        logger.info(f"Extracted {len(tags)} tags from {url}")
        return tags


def safe_harvest(func):
    """
    Decorator for safe harvesting with error handling.

    Catches exceptions and logs errors, returning empty list on failure.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Harvest error in {func.__name__}: {e}", exc_info=True)
            return []

    return wrapper
