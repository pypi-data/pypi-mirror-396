"""
fetch_url_package - Professional web content fetching and extraction toolkit

This package provides robust tools for fetching web pages and extracting content
with configurable extraction methods, detailed error handling, and domain caching.
"""

from .fetch import (
    fetch,
    fetch_async,
    fetch_html,
    FetchResult,
    FetchConfig,
    ExtractionMethod,
)
from .extractor import (
    extract_content,
    SimpleExtractor,
    TrafilaturaExtractor,
)
from .cache import DomainCache

__version__ = "1.0.0"

__all__ = [
    "fetch",
    "fetch_async",
    "fetch_html",
    "FetchResult",
    "FetchConfig",
    "ExtractionMethod",
    "extract_content",
    "SimpleExtractor",
    "TrafilaturaExtractor",
    "DomainCache",
]
