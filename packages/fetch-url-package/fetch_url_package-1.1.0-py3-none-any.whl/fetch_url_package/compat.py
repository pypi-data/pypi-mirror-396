"""
Backward compatibility wrapper for old fetch_url.py API.

This module provides a compatibility layer for code using the old fetch_url.py API.
"""

from typing import Tuple, Optional
from .fetch import fetch as _fetch, FetchConfig, ExtractionMethod


def fetch_and_extract(
    url: str,
    max_retries: int = 3,
    use_trafilatura: bool = False  # Changed default to False
) -> Tuple[Optional[str], Optional[str]]:
    """
    Backward compatible wrapper for fetch_and_extract.
    
    Args:
        url: URL to fetch
        max_retries: Maximum number of retry attempts
        use_trafilatura: Whether to use trafilatura (True) or simple extractor (False)
    
    Returns:
        Tuple of (content, error_message) where one of them will be None
    
    Examples:
        >>> content, error = fetch_and_extract("https://example.com")
        >>> if error:
        ...     print(f"Error: {error}")
        ... else:
        ...     print(content)
    """
    method = ExtractionMethod.TRAFILATURA if use_trafilatura else ExtractionMethod.SIMPLE
    config = FetchConfig(
        max_retries=max_retries,
        extraction_method=method
    )
    
    result = _fetch(url, config=config)
    
    if result.success:
        return result.content, None
    else:
        return None, result.error_message


def fetch_html(
    url: str,
    max_retries: int = 3
) -> Tuple[Optional[str], Optional[str]]:
    """
    Backward compatible wrapper for fetch_html.
    
    Args:
        url: URL to fetch
        max_retries: Maximum number of retry attempts
    
    Returns:
        Tuple of (html_content, error_message) where one of them will be None
    
    Examples:
        >>> html, error = fetch_html("https://example.com")
        >>> if error:
        ...     print(f"Error: {error}")
        ... else:
        ...     print(html)
    """
    from .fetch import fetch_html as _fetch_html
    
    config = FetchConfig(max_retries=max_retries)
    result = _fetch_html(url, config=config)
    
    if result.success:
        return result.html, None
    else:
        return None, result.error_message


def parse_html(
    html: str,
    include_tables: bool = False,
    use_trafilatura: bool = False  # Changed default to False
) -> Tuple[Optional[str], Optional[str]]:
    """
    Backward compatible wrapper for parse_html.
    
    Args:
        html: HTML content to parse
        include_tables: Whether to include table content
        use_trafilatura: Whether to use trafilatura (True) or simple extractor (False)
    
    Returns:
        Tuple of (text_content, error_message) where one of them will be None
    
    Examples:
        >>> html = "<html><body><p>Test</p></body></html>"
        >>> text, error = parse_html(html)
        >>> if error:
        ...     print(f"Error: {error}")
        ... else:
        ...     print(text)
    """
    from .extractor import extract_content
    
    if not html or not html.strip():
        return None, "Empty HTML content provided"
    
    try:
        method = "trafilatura" if use_trafilatura else "simple"
        kwargs = {"include_tables": include_tables} if use_trafilatura else {}
        
        content = extract_content(html, method=method, **kwargs)
        
        if content:
            return content, None
        else:
            return None, "Could not extract readable content from the page."
    except Exception as e:
        return None, f"Content extraction failed: {str(e)}"


# Keep the old module API for direct import
__all__ = [
    "fetch_and_extract",
    "fetch_html", 
    "parse_html",
]
