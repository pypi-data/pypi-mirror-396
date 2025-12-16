"""
Domain cache for storing and checking failed domains to avoid repeated failures.
"""

import json
import time
import logging
from typing import Dict, Optional, Set
from urllib.parse import urlparse
from pathlib import Path
from dataclasses import dataclass, asdict
from threading import Lock


logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entry in the domain cache."""
    domain: str
    failure_count: int
    last_failure_time: float
    error_type: str
    
    def is_expired(self, ttl: int) -> bool:
        """Check if the cache entry has expired."""
        return (time.time() - self.last_failure_time) > ttl


class DomainCache:
    """
    Cache for tracking failed domains to avoid repeated fetch attempts.
    
    Features:
    - Configurable TTL (time-to-live) for cache entries
    - Configurable failure threshold before domain is cached
    - Persistent storage to file (optional)
    - Thread-safe operations
    """
    
    def __init__(
        self,
        cache_file: Optional[str] = None,
        ttl: int = 86400,  # 24 hours default
        failure_threshold: int = 3,
        max_size: int = 10000,
    ):
        """
        Initialize domain cache.
        
        Args:
            cache_file: Path to cache file for persistence (None for memory-only)
            ttl: Time-to-live for cache entries in seconds (default: 24 hours)
            failure_threshold: Number of failures before caching domain (default: 3)
            max_size: Maximum number of entries in cache (default: 10000)
        """
        self.cache_file = cache_file
        self.ttl = ttl
        self.failure_threshold = failure_threshold
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        
        if cache_file:
            self._load_cache()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc or parsed.path
    
    def _load_cache(self) -> None:
        """Load cache from file."""
        if not self.cache_file or not Path(self.cache_file).exists():
            return
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for domain, entry_dict in data.items():
                    self._cache[domain] = CacheEntry(**entry_dict)
        except (IOError, PermissionError) as e:
            logger.warning(f"Failed to load cache from {self.cache_file}: {e}")
            self._cache = {}
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Cache file {self.cache_file} is corrupted: {e}")
            self._cache = {}
        except Exception as e:
            logger.error(f"Unexpected error loading cache: {e}")
            self._cache = {}
    
    def _save_cache(self) -> None:
        """Save cache to file."""
        if not self.cache_file:
            return
        
        try:
            # Clean expired entries before saving
            self._clean_expired()
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                data = {domain: asdict(entry) for domain, entry in self._cache.items()}
                json.dump(data, f, indent=2)
        except (IOError, PermissionError) as e:
            logger.warning(f"Failed to save cache to {self.cache_file}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving cache: {e}")
    
    def _clean_expired(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_domains = [
            domain for domain, entry in self._cache.items()
            if (current_time - entry.last_failure_time) > self.ttl
        ]
        for domain in expired_domains:
            del self._cache[domain]
    
    def _enforce_max_size(self) -> None:
        """Ensure cache doesn't exceed max size by removing oldest entries."""
        if len(self._cache) <= self.max_size:
            return
        
        # Sort by last failure time and remove oldest entries
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_failure_time
        )
        
        num_to_remove = len(self._cache) - self.max_size
        for domain, _ in sorted_entries[:num_to_remove]:
            del self._cache[domain]
    
    def should_skip(self, url: str) -> bool:
        """
        Check if URL should be skipped based on cached failures.
        
        Args:
            url: URL to check
        
        Returns:
            True if URL should be skipped, False otherwise
        """
        domain = self._extract_domain(url)
        
        with self._lock:
            if domain not in self._cache:
                return False
            
            entry = self._cache[domain]
            
            # Check if entry has expired
            if entry.is_expired(self.ttl):
                del self._cache[domain]
                return False
            
            # Check if failure count exceeds threshold
            return entry.failure_count >= self.failure_threshold
    
    def record_failure(
        self,
        url: str,
        error_type: str = "unknown"
    ) -> None:
        """
        Record a failure for a domain.
        
        Args:
            url: URL that failed
            error_type: Type of error (e.g., "404", "403", "timeout")
        """
        domain = self._extract_domain(url)
        current_time = time.time()
        
        with self._lock:
            if domain in self._cache:
                entry = self._cache[domain]
                
                # Check if entry has expired
                if entry.is_expired(self.ttl):
                    # Reset entry
                    entry.failure_count = 1
                    entry.last_failure_time = current_time
                    entry.error_type = error_type
                else:
                    # Increment failure count
                    entry.failure_count += 1
                    entry.last_failure_time = current_time
                    entry.error_type = error_type
            else:
                # Create new entry
                self._cache[domain] = CacheEntry(
                    domain=domain,
                    failure_count=1,
                    last_failure_time=current_time,
                    error_type=error_type
                )
            
            # Enforce max size
            self._enforce_max_size()
            
            # Save to file if configured
            if self.cache_file:
                self._save_cache()
    
    def record_success(self, url: str) -> None:
        """
        Record a success for a domain (removes it from cache).
        
        Args:
            url: URL that succeeded
        """
        domain = self._extract_domain(url)
        
        with self._lock:
            if domain in self._cache:
                del self._cache[domain]
                
                # Save to file if configured
                if self.cache_file:
                    self._save_cache()
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            if self.cache_file:
                self._save_cache()
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            return {
                "total_entries": len(self._cache),
                "domains": list(self._cache.keys()),
                "failure_counts": {
                    domain: entry.failure_count
                    for domain, entry in self._cache.items()
                }
            }
