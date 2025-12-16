# fetch-url-package

Professional web content fetching and extraction toolkit with configurable extraction methods, detailed error handling, and domain caching.

## Features

- 🚀 **Configurable Extraction Methods**: Choose between simple HTML tag removal (default) or advanced trafilatura extraction
- 🔄 **Intelligent Retry Logic**: Automatic retry with exponential backoff and randomization
- 🛡️ **Anti-Detection Measures**: Rotating user agents, randomized headers, and browser-like behavior
- 📊 **Detailed Error Handling**: Comprehensive error types and messages for all failure scenarios
- 💾 **Domain Cache**: Cache failed domains to avoid repeated failures
- ⚙️ **Fully Configurable**: Customize timeouts, retries, headers, SSL settings, and more
- 🔒 **Thread-Safe**: Safe for concurrent use in multi-threaded applications
- 📦 **Lightweight**: Minimal dependencies with optional advanced features

## Installation

### Basic Installation

```bash
pip install fetch-url-package
```

### With Trafilatura Support

```bash
pip install fetch-url-package[trafilatura]
```

### Development Installation

```bash
pip install fetch-url-package[dev]
```

## Quick Start

### Simple Usage (Default Simple Extractor)

```python
from fetch_url_package import fetch

# Fetch and extract content with default settings
result = fetch("https://example.com")

if result.success:
    print("Content:", result.content)
else:
    print(f"Error ({result.error_type}): {result.error_message}")
```

### Using Trafilatura Extractor

```python
from fetch_url_package import fetch, FetchConfig, ExtractionMethod

config = FetchConfig(
    extraction_method=ExtractionMethod.TRAFILATURA,
    extraction_kwargs={"include_tables": True}
)

result = fetch("https://example.com", config=config)
if result.success:
    print(result.content)
```

### Fetch HTML Only (No Extraction)

```python
from fetch_url_package import fetch_html

result = fetch_html("https://example.com")
if result.success:
    print("HTML:", result.html)
```

### Advanced Configuration

```python
from fetch_url_package import fetch, FetchConfig, ExtractionMethod, DomainCache

# Create a custom cache
cache = DomainCache(
    cache_file="/tmp/fetch_cache.json",
    ttl=86400,  # 24 hours
    failure_threshold=3
)

# Configure fetch settings
config = FetchConfig(
    # Retry settings
    max_retries=5,
    retry_delay=2.0,
    
    # Timeout settings
    timeout=60.0,
    connect_timeout=15.0,
    
    # Extraction settings
    extraction_method=ExtractionMethod.SIMPLE,
    
    # Custom headers
    custom_headers={
        "X-Custom-Header": "value"
    },
    
    # Cache settings
    use_cache=True,
    cache=cache,
    
    # Return HTML along with extracted content
    return_html=True,
    
    # Blocked domains
    blocked_domains=["example-blocked.com"]
)

result = fetch("https://example.com", config=config)
```

## API Reference

### Main Functions

#### `fetch(url, config=None, extract=True)`

Fetch and optionally extract content from URL.

**Parameters:**
- `url` (str): URL to fetch
- `config` (FetchConfig, optional): Configuration object
- `extract` (bool): Whether to extract content (default: True)

**Returns:** `FetchResult` object

#### `fetch_html(url, config=None)`

Fetch HTML content only without extraction.

**Parameters:**
- `url` (str): URL to fetch
- `config` (FetchConfig, optional): Configuration object

**Returns:** `FetchResult` object

### Configuration Classes

#### `FetchConfig`

Configuration for fetch operations.

**Parameters:**
- `max_retries` (int): Maximum retry attempts (default: 3)
- `retry_delay` (float): Base delay between retries in seconds (default: 1.0)
- `timeout` (float): Request timeout in seconds (default: 30.0)
- `connect_timeout` (float): Connection timeout in seconds (default: 10.0)
- `follow_redirects` (bool): Follow HTTP redirects (default: True)
- `max_redirects` (int): Maximum number of redirects (default: 10)
- `http2` (bool): Use HTTP/2 (default: True)
- `verify_ssl` (bool): Verify SSL certificates (default: False)
- `user_agents` (List[str], optional): List of user agents to rotate
- `referers` (List[str], optional): List of referers to rotate
- `custom_headers` (Dict[str, str], optional): Custom HTTP headers
- `extraction_method` (ExtractionMethod): Extraction method (default: SIMPLE)
- `extraction_kwargs` (Dict): Additional arguments for extractor
- `filter_file_extensions` (bool): Filter file URLs (default: True)
- `blocked_domains` (List[str], optional): Domains to block
- `use_cache` (bool): Use domain cache (default: True)
- `cache` (DomainCache, optional): Cache instance
- `return_html` (bool): Include HTML in result (default: False)

#### `DomainCache`

Cache for tracking failed domains.

**Parameters:**
- `cache_file` (str, optional): Path to cache file for persistence
- `ttl` (int): Time-to-live for cache entries in seconds (default: 86400)
- `failure_threshold` (int): Failures before caching domain (default: 3)
- `max_size` (int): Maximum cache entries (default: 10000)

**Methods:**
- `should_skip(url)`: Check if URL should be skipped
- `record_failure(url, error_type)`: Record a failure
- `record_success(url)`: Record a success
- `clear()`: Clear all cache entries
- `get_stats()`: Get cache statistics

### Result Classes

#### `FetchResult`

Result object containing fetch outcome and data.

**Attributes:**
- `url` (str): Original URL
- `success` (bool): Whether fetch was successful
- `content` (str, optional): Extracted content
- `html` (str, optional): Raw HTML content
- `error_type` (ErrorType, optional): Type of error if failed
- `error_message` (str, optional): Error message if failed
- `status_code` (int, optional): HTTP status code
- `final_url` (str, optional): Final URL after redirects
- `metadata` (Dict): Additional metadata

### Extraction Methods

#### `ExtractionMethod.SIMPLE` (Default)

Simple and fast extraction that removes HTML/XML tags without complex parsing.

**Pros:**
- No external dependencies
- Fast performance
- Reliable for most web pages

**Cons:**
- Less sophisticated than trafilatura
- May include some unwanted content

#### `ExtractionMethod.TRAFILATURA`

Advanced extraction using the trafilatura library.

**Pros:**
- Better content extraction quality
- Filters out navigation, ads, etc.
- Handles complex page structures

**Cons:**
- Requires trafilatura dependency
- Slightly slower

## Error Types

The package provides detailed error types:

- `NOT_FOUND` (404): Page not found
- `FORBIDDEN` (403): Access denied
- `RATE_LIMITED` (429): Too many requests
- `SERVER_ERROR` (5xx): Server error
- `TIMEOUT`: Request timeout
- `NETWORK_ERROR`: Network/connection error
- `SSL_ERROR`: SSL/TLS error
- `FILTERED`: URL filtered by configuration
- `EMPTY_CONTENT`: Page returned empty content
- `EXTRACTION_FAILED`: Content extraction failed
- `CACHED_FAILURE`: Domain in failure cache
- `UNKNOWN`: Unknown error

## Best Practices & Recommendations

### 1. Bypassing Human Verification (CAPTCHA)

**Challenge:** Many websites use CAPTCHA or human verification to block automated requests.

**Recommendations:**

1. **Use Proxy Services**: Consider using services like:
   - Oxylabs (already referenced in your code)
   - ScraperAPI
   - Bright Data (formerly Luminati)

2. **Implement Delays**: Add random delays between requests
   ```python
   import time
   import random
   
   for url in urls:
       result = fetch(url)
       time.sleep(random.uniform(2, 5))  # 2-5 second delay
   ```

3. **Rotate User Agents**: Already built-in, but you can add more
   ```python
   config = FetchConfig(
       user_agents=[
           "Your custom user agent 1",
           "Your custom user agent 2",
       ]
   )
   ```

4. **Use Sessions**: For multiple requests to same domain
   ```python
   # Future enhancement - session management
   ```

5. **Selenium/Playwright**: For JavaScript-heavy sites (not included in this package)

### 2. Handling Redirects

The package automatically handles:
- HTTP redirects (301, 302, 307, 308)
- Meta refresh redirects
- JavaScript redirects (partial support)

**Configuration:**
```python
config = FetchConfig(
    follow_redirects=True,
    max_redirects=10  # Adjust as needed
)
```

**For Complex JavaScript Redirects:**
Consider using browser automation tools like Selenium or Playwright for pages that heavily rely on JavaScript.

### 3. Domain Caching Strategy

**Use Cases:**
- Large-scale scraping operations
- Batch URL processing
- Avoiding repeated failures

**Example:**
```python
from fetch_url_package import DomainCache, FetchConfig, fetch

# Persistent cache
cache = DomainCache(
    cache_file="/var/cache/fetch_domains.json",
    ttl=86400,  # 24 hours
    failure_threshold=3  # Cache after 3 failures
)

config = FetchConfig(use_cache=True, cache=cache)

# Fetch multiple URLs
urls = ["http://example1.com", "http://example2.com"]
for url in urls:
    result = fetch(url, config=config)
    if result.error_type == "cached_failure":
        print(f"Skipped cached domain: {url}")
```

**Cache Statistics:**
```python
stats = cache.get_stats()
print(f"Cached domains: {stats['total_entries']}")
print(f"Domains: {stats['domains']}")
```

### 4. Rate Limiting

**Implement Your Own Rate Limiting:**
```python
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_second=1):
        self.rps = requests_per_second
        self.last_request = defaultdict(float)
    
    def wait_if_needed(self, domain):
        now = time.time()
        elapsed = now - self.last_request[domain]
        if elapsed < (1.0 / self.rps):
            time.sleep((1.0 / self.rps) - elapsed)
        self.last_request[domain] = time.time()

# Usage
limiter = RateLimiter(requests_per_second=2)
for url in urls:
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    limiter.wait_if_needed(domain)
    result = fetch(url)
```

### 5. Concurrent Fetching

**Using ThreadPoolExecutor:**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from fetch_url_package import fetch, FetchConfig

def fetch_url(url):
    return fetch(url)

urls = ["http://example1.com", "http://example2.com", "http://example3.com"]

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(fetch_url, url): url for url in urls}
    
    for future in as_completed(futures):
        url = futures[future]
        try:
            result = future.result()
            if result.success:
                print(f"Success: {url}")
            else:
                print(f"Failed: {url} - {result.error_message}")
        except Exception as e:
            print(f"Exception: {url} - {e}")
```

### 6. Custom Proxy Support

**Using HTTP Proxy:**
```python
# Note: Current version doesn't have built-in proxy support
# Future enhancement or workaround using environment variables:

import os
os.environ['HTTP_PROXY'] = 'http://proxy:port'
os.environ['HTTPS_PROXY'] = 'https://proxy:port'

# Or modify the fetch.py to add proxy support in httpx.AsyncClient
```

### 7. Handling Different Content Types

**Check Response Content:**
```python
result = fetch_html("https://example.com")
if result.success and result.html:
    # Check if it's actually HTML
    if result.html.strip().startswith('<!DOCTYPE') or '<html' in result.html.lower():
        # Process HTML
        pass
```

## Examples

### Example 1: Simple Content Extraction

```python
from fetch_url_package import fetch

result = fetch("https://en.wikipedia.org/wiki/Python_(programming_language)")
if result.success:
    print(f"Extracted {len(result.content)} characters")
    print(result.content[:500])  # First 500 characters
else:
    print(f"Error: {result.error_message}")
```

### Example 2: Batch Processing with Cache

```python
from fetch_url_package import fetch, FetchConfig, DomainCache

cache = DomainCache(cache_file="batch_cache.json")
config = FetchConfig(use_cache=True, cache=cache)

urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
]

results = []
for url in urls:
    result = fetch(url, config=config)
    results.append(result)

# Check cache stats
print(cache.get_stats())
```

### Example 3: Custom Extraction

```python
from fetch_url_package import fetch, FetchConfig, ExtractionMethod

# Use trafilatura with custom options
config = FetchConfig(
    extraction_method=ExtractionMethod.TRAFILATURA,
    extraction_kwargs={
        "include_tables": True,
        "include_links": True,
        "include_comments": False,
    }
)

result = fetch("https://example.com", config=config)
```

## Migration from Old Code

If you're migrating from the old `fetch_url.py`:

### Old Code:
```python
from fetch_url import fetch_and_extract

content, error = fetch_and_extract(url)
if error:
    print(f"Error: {error}")
else:
    print(content)
```

### New Code:
```python
from fetch_url_package import fetch

result = fetch(url)
if result.success:
    print(result.content)
else:
    print(f"Error: {result.error_message}")
```

### Using Trafilatura (like old default):
```python
from fetch_url_package import fetch, FetchConfig, ExtractionMethod

config = FetchConfig(extraction_method=ExtractionMethod.TRAFILATURA)
result = fetch(url, config=config)
```

## Development

### Running Tests

```bash
pip install -e .[dev]
pytest tests/
```

### Code Formatting

```bash
black fetch_url_package/
flake8 fetch_url_package/
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the GitHub issue tracker.
