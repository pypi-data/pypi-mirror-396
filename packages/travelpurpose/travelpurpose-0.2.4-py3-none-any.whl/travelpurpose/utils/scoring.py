"""
Scoring and confidence calculation utilities for classification.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


def calculate_tag_weights(
    tags: list[dict], source_weights: dict[str, float] = None
) -> dict[str, float]:
    """
    Calculate weighted scores for each unique tag.

    Args:
        tags: List of tag dictionaries with 'tag' and 'source' fields
        source_weights: Optional weights per source (default: equal weights)

    Returns:
        Dictionary of tag -> weight
    """
    if source_weights is None:
        # Default source weights
        source_weights = {
            "wikidata": 1.5,
            "wikipedia": 1.3,
            "unesco": 2.0,
            "booking": 1.0,
            "agoda": 1.0,
            "trivago": 0.9,
            "kayak": 0.9,
            "tripdotcom": 0.9,
            "skyscanner": 0.8,
        }

    tag_weights = {}

    for tag_entry in tags:
        tag = tag_entry.get("tag", "").lower()
        source = tag_entry.get("source", "").lower()

        if not tag:
            continue

        weight = source_weights.get(source, 0.5)

        # Boost weight for certain evidence types
        evidence_type = tag_entry.get("evidence_type", "")
        if evidence_type == "jsonld":
            weight *= 1.2
        elif evidence_type == "meta":
            weight *= 1.0
        elif evidence_type == "heading":
            weight *= 0.8

        tag_weights[tag] = tag_weights.get(tag, 0.0) + weight

    return tag_weights


def normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    """
    Normalize scores to 0-1 range using softmax-like normalization.

    Args:
        scores: Dictionary of label -> score

    Returns:
        Dictionary of label -> normalized score
    """
    if not scores:
        return {}

    values = np.array(list(scores.values()))
    if len(values) == 0 or np.max(values) == 0:
        return {k: 0.0 for k in scores.keys()}

    # Use softmax for normalization
    exp_values = np.exp(values - np.max(values))
    softmax_values = exp_values / exp_values.sum()

    return {label: float(score) for label, score in zip(scores.keys(), softmax_values)}


def calculate_confidence(
    main_scores: dict[str, float],
    sub_scores: dict[str, float],
    min_confidence: float = 0.1,
) -> float:
    """
    Calculate overall confidence score for classification.

    Args:
        main_scores: Scores for main categories
        sub_scores: Scores for subcategories
        min_confidence: Minimum confidence threshold

    Returns:
        Confidence score between 0 and 1
    """
    if not main_scores and not sub_scores:
        return 0.0

    # Get top scores
    main_max = max(main_scores.values()) if main_scores else 0.0
    sub_max = max(sub_scores.values()) if sub_scores else 0.0

    # Weighted average (main categories are more important)
    confidence = 0.7 * main_max + 0.3 * sub_max

    # Apply minimum threshold
    if confidence < min_confidence:
        return 0.0

    return min(confidence, 1.0)


def select_top_labels(
    scores: dict[str, float],
    threshold: float = 0.15,
    max_labels: int = 5,
) -> list[tuple[str, float]]:
    """
    Select top labels based on threshold and max count.

    Args:
        scores: Dictionary of label -> score
        threshold: Minimum score threshold
        max_labels: Maximum number of labels to return

    Returns:
        List of (label, score) tuples sorted by score descending
    """
    # Filter by threshold
    filtered = [(label, score) for label, score in scores.items() if score >= threshold]

    # Sort by score descending
    filtered.sort(key=lambda x: x[1], reverse=True)

    # Limit to max_labels
    return filtered[:max_labels]


def aggregate_scores_by_category(
    tag_weights: dict[str, float],
    tag_mappings: dict[str, dict],
) -> tuple[dict[str, float], dict[str, float]]:
    """
    Aggregate tag weights into main and subcategory scores.

    Args:
        tag_weights: Dictionary of tag -> weight
        tag_mappings: Tag mapping configuration from ontology

    Returns:
        Tuple of (main_scores, sub_scores)
    """
    main_scores = {}
    sub_scores = {}

    for tag, weight in tag_weights.items():
        # Find matching mapping
        best_match = None
        best_score = 0.0

        for mapping_name, mapping_config in tag_mappings.items():
            keywords = mapping_config.get("keywords", [])

            for keyword in keywords:
                if keyword.lower() in tag.lower() or tag.lower() in keyword.lower():
                    # Calculate similarity score
                    score = len(keyword) / max(len(keyword), len(tag))
                    if score > best_score:
                        best_score = score
                        best_match = mapping_config

        if best_match:
            # Add to main category
            main_cat = best_match.get("main")
            if main_cat:
                main_scores[main_cat] = (
                    main_scores.get(main_cat, 0.0) + weight * best_score
                )

            # Add to subcategories
            sub_cats = best_match.get("sub", [])
            for sub_cat in sub_cats:
                sub_scores[sub_cat] = sub_scores.get(sub_cat, 0.0) + weight * best_score

    return main_scores, sub_scores


def merge_nbd_purposes(
    main_scores: dict[str, float],
    sub_scores: dict[str, float],
    nbd_purposes: list[str],
    nbd_mapping: dict[str, dict],
    nbd_weight: float = 2.0,
) -> tuple[dict[str, float], dict[str, float]]:
    """
    Merge NBD purposes into existing scores with high weight.

    Args:
        main_scores: Existing main category scores
        sub_scores: Existing subcategory scores
        nbd_purposes: List of NBD purpose strings
        nbd_mapping: NBD to ontology mapping
        nbd_weight: Weight multiplier for NBD data

    Returns:
        Updated (main_scores, sub_scores)
    """
    main_scores = main_scores.copy()
    sub_scores = sub_scores.copy()

    nbd_to_main = nbd_mapping.get("nbd_to_main", {})

    for purpose in nbd_purposes:
        mapping = nbd_to_main.get(purpose, nbd_to_main.get("DEFAULT", {}))

        main_cats = mapping.get("main", [])
        for main_cat in main_cats:
            main_scores[main_cat] = main_scores.get(main_cat, 0.0) + nbd_weight

        sub_cats = mapping.get("sub", [])
        for sub_cat in sub_cats:
            sub_scores[sub_cat] = sub_scores.get(sub_cat, 0.0) + nbd_weight

    return main_scores, sub_scores
