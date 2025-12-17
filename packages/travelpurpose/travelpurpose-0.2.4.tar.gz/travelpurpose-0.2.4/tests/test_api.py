"""
Tests for the main API functions.
"""

from travelpurpose.classifier import get_ontology, load, predict_purpose, search


def test_load():
    """Test data loading."""
    load()
    # Should not raise any exceptions


def test_predict_purpose_basic():
    """Test basic purpose prediction."""
    # Test with a well-known city (use cache to avoid network calls in CI)
    result = predict_purpose("Paris", use_cache=True)

    assert isinstance(result, dict)
    assert "main" in result
    assert "sub" in result
    assert "confidence" in result

    assert isinstance(result["main"], list)
    assert isinstance(result["sub"], list)
    assert isinstance(result["confidence"], (int, float))
    assert 0 <= result["confidence"] <= 1

    # Paris should have results (either from cache or fallback)
    assert len(result["main"]) > 0


def test_predict_purpose_unknown_city():
    """Test prediction for unknown city."""
    result = predict_purpose("NonExistentCityXYZ123", use_cache=True)

    assert isinstance(result, dict)
    # Unknown city should have low/zero confidence
    assert result["confidence"] <= 0.3


def test_get_ontology():
    """Test ontology retrieval."""
    ontology = get_ontology()

    assert isinstance(ontology, dict)
    assert "main_categories" in ontology
    assert "subcategories" in ontology
    assert "tag_mappings" in ontology

    assert len(ontology["main_categories"]) > 0


def test_search():
    """Test city search."""
    results = search("paris")

    # May or may not find results depending on if data is available
    assert isinstance(results, list)


def test_predict_purpose_consistency():
    """Test that predictions are consistent."""
    # Same city should give same results
    result1 = predict_purpose("London", use_cache=True)
    result2 = predict_purpose("London", use_cache=True)

    assert result1["main"] == result2["main"]
    assert result1["sub"] == result2["sub"]
    assert result1["confidence"] == result2["confidence"]
