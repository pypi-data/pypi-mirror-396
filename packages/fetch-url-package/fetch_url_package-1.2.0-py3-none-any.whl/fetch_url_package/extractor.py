"""
Simple HTML content extractor that removes HTML/XML tags without complex parsing.
"""

import re
from typing import Optional, Protocol
from html import unescape
import logging


logger = logging.getLogger(__name__)


class ContentExtractor(Protocol):
    """Protocol for content extractors."""
    
    def extract(self, html: str, **kwargs) -> Optional[str]:
        """Extract content from HTML."""
        ...


class SimpleExtractor:
    """
    Simple extractor that removes HTML/XML tags and cleans up the text.
    This is the default extraction method - fast and lightweight.
    """
    
    def extract(self, html: str, **kwargs) -> Optional[str]:
        """
        Extract text content by removing HTML tags.
        
        Args:
            html: HTML content to extract from
            **kwargs: Additional options (unused for simple extractor)
        
        Returns:
            Extracted text content or None if extraction fails
        """
        if not html or not html.strip():
            return None
        
        try:
            # Remove script and style elements with their content
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove comments
            text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
            
            # Remove all HTML/XML tags
            text = re.sub(r'<[^>]+>', '', text)
            
            # Unescape HTML entities
            text = unescape(text)
            
            # Clean up whitespace
            # Replace multiple spaces with single space
            text = re.sub(r'[ \t]+', ' ', text)
            
            # Replace multiple newlines with double newline (paragraph breaks)
            text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
            
            # Remove leading/trailing whitespace from each line
            lines = [line.strip() for line in text.split('\n')]
            text = '\n'.join(line for line in lines if line)
            
            # Final cleanup
            text = text.strip()
            
            if not text:
                return None
            
            return text
            
        except (ValueError, TypeError) as e:
            # Specific parsing errors
            logger.warning(f"HTML parsing error in SimpleExtractor: {e}")
            return None
        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error in SimpleExtractor: {type(e).__name__}: {e}")
            return None


class TrafilaturaExtractor:
    """
    Advanced extractor using trafilatura library for better content extraction.
    Requires trafilatura to be installed.
    """
    
    def __init__(self):
        """Initialize trafilatura extractor."""
        try:
            import trafilatura
            self.trafilatura = trafilatura
        except ImportError:
            raise ImportError(
                "trafilatura is required for TrafilaturaExtractor. "
                "Install it with: pip install trafilatura"
            )
    
    def extract(
        self, 
        html: str, 
        include_tables: bool = False,
        include_comments: bool = False,
        include_links: bool = False,
        **kwargs
    ) -> Optional[str]:
        """
        Extract text content using trafilatura.
        
        Args:
            html: HTML content to extract from
            include_tables: Whether to include table content
            include_comments: Whether to include comments
            include_links: Whether to include links
            **kwargs: Additional trafilatura options
        
        Returns:
            Extracted text content or None if extraction fails
        """
        if not html or not html.strip():
            return None
        
        try:
            text = self.trafilatura.extract(
                html,
                include_comments=include_comments,
                include_images=False,  # Always exclude images
                include_tables=include_tables,
                include_links=include_links,
                favor_recall=True,
                favor_precision=False,
                deduplicate=True,
                **kwargs
            )
            
            if not text or not text.strip():
                # Fallback: try with more lenient settings
                text = self.trafilatura.extract(
                    html,
                    include_comments=False,
                    include_images=False,
                    include_tables=True,
                    favor_recall=True,
                    no_fallback=False,
                )
            
            if text:
                text = text.strip()
                return text if text else None
            
            return None
            
        except ImportError as e:
            logger.error(f"Trafilatura not available: {e}")
            return None
        except (ValueError, TypeError) as e:
            logger.warning(f"Trafilatura extraction error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in TrafilaturaExtractor: {type(e).__name__}: {e}")
            return None


def extract_content(
    html: str,
    method: str = "simple",
    **kwargs
) -> Optional[str]:
    """
    Extract content from HTML using the specified method.
    
    Args:
        html: HTML content to extract from
        method: Extraction method - "simple" (default) or "trafilatura"
        **kwargs: Additional options passed to the extractor
    
    Returns:
        Extracted text content or None if extraction fails
    
    Examples:
        >>> html = "<html><body><p>Hello World</p></body></html>"
        >>> extract_content(html)
        'Hello World'
        
        >>> extract_content(html, method="trafilatura", include_tables=True)
        'Hello World'
    """
    if method == "simple":
        extractor = SimpleExtractor()
    elif method == "trafilatura":
        extractor = TrafilaturaExtractor()
    else:
        raise ValueError(f"Unknown extraction method: {method}")
    
    return extractor.extract(html, **kwargs)
