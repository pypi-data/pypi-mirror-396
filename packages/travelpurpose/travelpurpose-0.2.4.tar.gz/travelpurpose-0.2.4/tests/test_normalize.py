"""
Tests for normalization utilities.
"""

from travelpurpose.utils.normalize import (
    deduplicate_cities,
    extract_keywords,
    fuzzy_match_tag,
    normalize_city_name,
    normalize_tag,
    to_ascii,
)


def test_normalize_city_name():
    """Test city name normalization."""
    assert normalize_city_name("New York City") == "new york"
    assert normalize_city_name("Paris Metropolitan") == "paris"
    assert normalize_city_name("  London  ") == "london"
    assert normalize_city_name("İstanbul") == "i̇stanbul"


def test_to_ascii():
    """Test ASCII conversion."""
    assert to_ascii("café") == "cafe"
    assert to_ascii("naïve") == "naive"
    assert to_ascii("München") == "Munchen"
    assert to_ascii("São Paulo") == "Sao Paulo"


def test_normalize_tag():
    """Test tag normalization."""
    assert normalize_tag("Business-Friendly") == "business_friendly"
    assert normalize_tag("City Center") == "city_center"
    assert normalize_tag("  spa & wellness  ") == "spa_wellness"
    assert normalize_tag("beach/resort") == "beachresort"


def test_extract_keywords():
    """Test keyword extraction."""
    keywords = extract_keywords("This is a test of keyword extraction")

    assert "test" in keywords
    assert "keyword" in keywords
    assert "extraction" in keywords
    assert "the" not in keywords  # Stop word
    assert "a" not in keywords  # Stop word


def test_fuzzy_match_tag():
    """Test fuzzy tag matching."""
    keywords = ["business", "leisure", "cultural", "adventure"]

    assert fuzzy_match_tag("bussiness", keywords) == "business"
    assert fuzzy_match_tag("culture", keywords) == "cultural"
    assert fuzzy_match_tag("xyz", keywords, threshold=0.9) is None


def test_deduplicate_cities():
    """Test city deduplication."""
    cities = [
        {"name": "Paris", "country": "France", "wikidata_id": "Q90"},
        {"name": "Paris", "country": "France", "wikidata_id": "Q90"},
        {"name": "Paris", "country": "USA", "wikidata_id": "Q12345"},
        {"name": "London", "country": "UK"},
    ]

    unique = deduplicate_cities(cities)

    assert len(unique) == 3  # Should remove one Paris duplicate
    assert any(c["name"] == "Paris" and c["country"] == "France" for c in unique)
    assert any(c["name"] == "Paris" and c["country"] == "USA" for c in unique)
    assert any(c["name"] == "London" for c in unique)
