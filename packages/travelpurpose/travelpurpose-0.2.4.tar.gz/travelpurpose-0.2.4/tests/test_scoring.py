"""
Tests for scoring utilities.
"""

from travelpurpose.utils.scoring import (
    calculate_confidence,
    calculate_tag_weights,
    normalize_scores,
    select_top_labels,
)


def test_calculate_tag_weights():
    """Test tag weight calculation."""
    tags = [
        {"tag": "business", "source": "booking"},
        {"tag": "business", "source": "agoda"},
        {"tag": "leisure", "source": "trivago"},
    ]

    weights = calculate_tag_weights(tags)

    assert "business" in weights
    assert "leisure" in weights
    assert weights["business"] > weights["leisure"]  # Business appears twice


def test_calculate_tag_weights_with_evidence():
    """Test tag weights with evidence types."""
    tags = [
        {"tag": "hotel", "source": "booking", "evidence_type": "jsonld"},
        {"tag": "resort", "source": "booking", "evidence_type": "meta"},
        {"tag": "beach", "source": "booking", "evidence_type": "heading"},
    ]

    weights = calculate_tag_weights(tags)

    # JSON-LD should have highest weight
    assert weights["hotel"] > weights["resort"]
    assert weights["resort"] > weights["beach"]


def test_normalize_scores():
    """Test score normalization."""
    scores = {"business": 5.0, "leisure": 3.0, "culture": 2.0}

    normalized = normalize_scores(scores)

    # Should sum to 1 (approximately)
    total = sum(normalized.values())
    assert 0.99 < total < 1.01

    # Order should be preserved
    assert normalized["business"] > normalized["leisure"]
    assert normalized["leisure"] > normalized["culture"]


def test_normalize_scores_empty():
    """Test normalization with empty scores."""
    result = normalize_scores({})
    assert result == {}


def test_calculate_confidence():
    """Test confidence calculation."""
    main_scores = {"business": 0.8, "leisure": 0.2}
    sub_scores = {"finance_hub": 0.7, "shopping": 0.3}

    confidence = calculate_confidence(main_scores, sub_scores)

    assert 0 <= confidence <= 1
    assert confidence > 0.5  # Should be relatively high


def test_calculate_confidence_low():
    """Test confidence with low scores."""
    main_scores = {"business": 0.1}
    sub_scores = {}

    confidence = calculate_confidence(main_scores, sub_scores, min_confidence=0.2)

    assert confidence == 0.0  # Below threshold


def test_select_top_labels():
    """Test top label selection."""
    scores = {
        "business": 0.5,
        "leisure": 0.3,
        "culture": 0.15,
        "beach": 0.05,
    }

    top_labels = select_top_labels(scores, threshold=0.1, max_labels=3)

    assert len(top_labels) == 3
    assert top_labels[0][0] == "business"
    assert top_labels[1][0] == "leisure"
    assert top_labels[2][0] == "culture"
    assert "beach" not in [label for label, _ in top_labels]
