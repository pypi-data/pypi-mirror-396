"""
Input/Output utilities for loading configuration and data files.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

logger = logging.getLogger(__name__)


def get_package_dir() -> Path:
    """Get the package directory path."""
    return Path(__file__).parent.parent


def load_ontology() -> dict[str, Any]:
    """
    Load the ontology configuration.

    Returns:
        Ontology dictionary
    """
    ontology_path = get_package_dir() / "ontology" / "ontology.yaml"

    try:
        with open(ontology_path, encoding="utf-8") as f:
            ontology = yaml.safe_load(f)
        logger.info(f"Loaded ontology from {ontology_path}")
        return ontology
    except Exception as e:
        logger.error(f"Failed to load ontology: {e}")
        return {
            "main_categories": [],
            "subcategories": {},
            "tag_mappings": {},
        }


def load_nbd_mapping() -> dict[str, Any]:
    """
    Load NBD purpose mapping configuration.

    Returns:
        NBD mapping dictionary
    """
    mapping_path = get_package_dir() / "ontology" / "mapping_nbd.yaml"

    try:
        with open(mapping_path, encoding="utf-8") as f:
            mapping = yaml.safe_load(f)
        logger.info(f"Loaded NBD mapping from {mapping_path}")
        return mapping
    except Exception as e:
        logger.error(f"Failed to load NBD mapping: {e}")
        return {"nbd_to_main": {}}


def load_cities_data() -> pd.DataFrame | None:
    """
    Load the cities dataset.

    Returns:
        DataFrame with cities data or None if not available
    """
    data_dir = get_package_dir() / "data"

    # Try parquet first (more efficient)
    parquet_path = data_dir / "cities.parquet"
    if parquet_path.exists():
        try:
            df = pd.read_parquet(parquet_path)
            logger.info(f"Loaded {len(df)} cities from {parquet_path}")
            return df
        except Exception as e:
            logger.warning(f"Failed to load parquet: {e}")

    # Fall back to JSON
    json_path = data_dir / "cities.json"
    if json_path.exists():
        try:
            df = pd.read_json(json_path, orient="records")
            logger.info(f"Loaded {len(df)} cities from {json_path}")
            return df
        except Exception as e:
            logger.warning(f"Failed to load JSON: {e}")

    logger.warning("No cities data found. Run pipeline to generate.")
    return None


def save_cities_data(df: pd.DataFrame, output_dir: Path | None = None):
    """
    Save cities dataset to both parquet and JSON formats.

    Args:
        df: Cities DataFrame
        output_dir: Output directory (defaults to package data dir)
    """
    if output_dir is None:
        output_dir = get_package_dir() / "data"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save as parquet
    parquet_path = output_dir / "cities.parquet"
    try:
        df.to_parquet(parquet_path, index=False)
        logger.info(f"Saved {len(df)} cities to {parquet_path}")
    except Exception as e:
        logger.error(f"Failed to save parquet: {e}")

    # Save as JSON
    json_path = output_dir / "cities.json"
    try:
        df.to_json(json_path, orient="records", indent=2, force_ascii=False)
        logger.info(f"Saved {len(df)} cities to {json_path}")
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")


def load_nbd_excel(filepath: str) -> pd.DataFrame | None:
    """
    Load NBD.xlsx file.

    Args:
        filepath: Path to NBD.xlsx

    Returns:
        DataFrame or None if file not found
    """
    if not os.path.exists(filepath):
        logger.warning(f"NBD file not found: {filepath}")
        return None

    try:
        df = pd.read_excel(filepath)
        logger.info(f"Loaded NBD data: {len(df)} rows from {filepath}")
        return df
    except Exception as e:
        logger.error(f"Failed to load NBD file: {e}")
        return None


def load_json(filepath: str) -> Any | None:
    """
    Load JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Parsed JSON data or None
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Failed to load JSON from {filepath}: {e}")
        return None


def save_json(data: Any, filepath: str, indent: int = 2):
    """
    Save data to JSON file.

    Args:
        data: Data to save
        filepath: Output file path
        indent: JSON indentation
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logger.info(f"Saved JSON to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save JSON to {filepath}: {e}")


def load_yaml(filepath: str) -> dict | None:
    """
    Load YAML file.

    Args:
        filepath: Path to YAML file

    Returns:
        Parsed YAML data or None
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data
    except Exception as e:
        logger.error(f"Failed to load YAML from {filepath}: {e}")
        return None


def save_yaml(data: dict, filepath: str):
    """
    Save data to YAML file.

    Args:
        data: Data to save
        filepath: Output file path
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        logger.info(f"Saved YAML to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save YAML to {filepath}: {e}")


def ensure_data_dir() -> Path:
    """
    Ensure data directory exists.

    Returns:
        Path to data directory
    """
    data_dir = get_package_dir() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_cache_dir() -> Path:
    """
    Get cache directory path.

    Returns:
        Path to cache directory
    """
    cache_dir = Path.home() / ".cache" / "travelpurpose"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
