"""
TravelPurpose - City Travel Purpose Classification Library

A production-grade Python library for classifying world cities by travel purpose
using multi-source data from public travel platforms and knowledge bases.
"""

__version__ = "0.2.1"
__author__ = "Travel Purpose Contributors"

from travelpurpose.classifier import load, predict_purpose, search, tags

__all__ = ["predict_purpose", "tags", "search", "load", "__version__"]
