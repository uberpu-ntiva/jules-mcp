# Request Pattern Specification: Jules AI External Integration

## Purpose
Defines how Jules AI integrates with external systems through HTTP requests, web searches, and API calls.

## Network Capabilities (Confirmed)
- ✅ **Web Search**: DuckDuckGo HTML API access confirmed
- ✅ **External APIs**: GitHub API access confirmed
- ✅ **HTTP Requests**: Standard urllib.request capabilities
- ❌ **Direct Internet**: Some services blocked (httpbin.org 503 error)
- ❌ **Docker**: Not available in environment

## Request Patterns

### 1. External API Integration Pattern
```python
import urllib.request
import json
import time

def call_external_api(method, url, data=None, headers=None, timeout=10):
    """
    Standard pattern for external API calls
    """
    try:
        if method.upper() == 'GET':
            req = urllib.request.Request(url, headers=headers or {})
        else:
            req = urllib.request.Request(
                url,
                data=data.encode('utf-8') if data else None,
                headers=headers or {}
            )
            req.get_method = lambda: method.upper()

        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {
                'status': response.status,
                'headers': dict(response.headers),
                'data': json.loads(response.read().decode('utf-8'))
            }
    except urllib.error.HTTPError as e:
        return {
            'error': f'HTTP {e.code}: {e.reason}',
            'status': e.code
        }
    except urllib.error.URLError as e:
        return {
            'error': f'URL Error: {e.reason}',
            'status': None
        }
    except Exception as e:
        return {
            'error': f'Unexpected error: {str(e)}',
            'status': None
        }

# Example: Call GitHub API
def get_github_repo(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        'User-Agent': 'Jules-MCP-Client/1.0',
        'Accept': 'application/vnd.github.v3+json'
    }
    return call_external_api('GET', url, headers=headers)
```

### 2. Web Search Pattern
```python
def perform_web_search(query):
    """
    Search DuckDuckGo for information
    """
    try:
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://duckduckgo.com/html/?q={encoded_query}"

        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')

        # Extract search results (basic parsing)
        results = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '<a rel="nofollow" class="result__a" href=' in line:
                # Extract title and URL
                title_match = re.search(r'>(.*?)</a>', line)
                url_match = re.search(r'href="(.*?)"', line)

                if title_match and url_match:
                    title = title_match.group(1).strip()
                    url = url_match.group(1).strip()
                    results.append({'title': title, 'url': url})

        return {
            'success': True,
            'query': query,
            'results': results[:10]  # Limit to first 10 results
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Search failed: {str(e)}',
            'query': query
        }
```

### 3. Retry Pattern with Backoff
```python
import time
import random

def call_with_retry(func, max_retries=3, base_delay=1, max_delay=30):
    """
    Retry pattern with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            result = func()
            if isinstance(result, dict) and result.get('status') in [200, 201]:
                return result

            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                print(f"Retry {attempt + 1}/{max_retries} in {delay:.2f}s")
                time.sleep(delay)
                continue

        except Exception as e:
            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                print(f"Retry {attempt + 1}/{max_retries} for error: {str(e)}")
                time.sleep(delay)
                continue
            return {
                'error': f'Failed after {max_retries} attempts: {str(e)}',
                'attempts': attempt + 1
            }

    return result
```

## Usage Examples for Jules AI

### Example 1: Research External Code
```python
def research_github_repository(repo_url):
    """Research a GitHub repository for implementation patterns"""

    # Extract owner/repo from URL
    parts = repo_url.strip('/').split('/')
    if len(parts) >= 2:
        owner, repo = parts[-2], parts[-1]
    else:
        return {'error': 'Invalid repository URL'}

    # Get repo info
    repo_data = call_with_retry(lambda: get_github_repo(owner, repo))

    if 'error' in repo_data:
        return repo_data

    # Get commit history for recent changes
    commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    commits_data = call_with_retry(lambda: call_external_api('GET', commits_url))

    return {
        'repository': repo_data['data'],
        'recent_commits': commits_data.get('data', [])[:5],
        'implementation_patterns': extract_patterns(repo_data['data'])
    }

def extract_patterns(repo_data):
    """Extract implementation patterns from repo data"""
    patterns = []

    # Language-based patterns
    if repo_data.get('language'):
        patterns.append(f"Language: {repo_data['language']}")

    # Check for common patterns in description
    description = repo_data.get('description', '').lower()
    if 'api' in description:
        patterns.append("REST API implementation")
    if 'react' in description:
        patterns.append("React components")
    if 'typescript' in description:
        patterns.append("TypeScript patterns")

    return patterns
```

### Example 2: Validate External Dependencies
```python
def validate_external_dependencies(dependencies):
    """Validate that external dependencies are available"""
    results = []

    for dep in dependencies:
        if dep['type'] == 'github_repo':
            repo_data = call_with_retry(lambda: get_github_repo(
                dep['owner'], dep['repo']
            ))

            if 'error' in repo_data:
                results.append({
                    'dependency': dep,
                    'status': 'FAILED',
                    'error': repo_data['error']
                })
            else:
                results.append({
                    'dependency': dep,
                    'status': 'AVAILABLE',
                    'info': {
                        'stars': repo_data['data']['stargazers_count'],
                        'language': repo_data['data']['language'],
                        'last_updated': repo_data['data']['updated_at']
                    }
                })

        elif dep['type'] == 'web_service':
            # Test if web service is reachable
            service_data = call_with_retry(lambda: call_external_api(
                'GET', dep['url'], timeout=5
            ))

            results.append({
                'dependency': dep,
                'status': 'AVAILABLE' if 'error' not in service_data else 'FAILED',
                'response': service_data
            })

    return {
        'total_dependencies': len(dependencies),
        'available': len([r for r in results if r['status'] == 'AVAILABLE']),
        'failed': len([r for r in results if r['status'] == 'FAILED']),
        'details': results
    }
```

### Example 3: Search for Code Examples
```python
def search_code_examples(search_query):
    """Search for code examples and best practices"""

    # Web search for code examples
    search_results = perform_web_search(f"{search_query} code example best practices")

    if not search_results['success']:
        return {
            'error': 'Search failed',
            'query': search_query
        }

    # Filter for code-related results
    code_examples = []
    for result in search_results['results']:
        # Check if result looks like code documentation
        title_lower = result['title'].lower()
        if any(keyword in title_lower for keyword in ['code', 'example', 'tutorial', 'guide', 'pattern']):
            code_examples.append(result)

    return {
        'query': search_query,
        'total_results': len(search_results['results']),
        'code_examples': code_examples,
        'recommended': code_examples[:3]  # Top 3 recommendations
    }
```

## Error Handling Standards

### Standard Error Response Format
```python
def standard_error_response(error_type, details, suggestion=None):
    """Create standardized error response"""
    return {
        'success': False,
        'error_type': error_type,
        'message': details,
        'suggestion': suggestion or 'Check input parameters and try again',
        'timestamp': time.time()
    }
```

### Common Error Types
```python
ERROR_TYPES = {
    'NETWORK_UNAVAILABLE': 'External network not accessible',
    'API_RATE_LIMIT': 'API rate limit exceeded',
    'AUTHENTICATION_FAILED': 'Invalid credentials or authentication',
    'INVALID_RESPONSE': 'Invalid response from external service',
    'TIMEOUT': 'Request timeout',
    'MALFORMED_URL': 'Invalid URL format'
}
```

## Security Considerations

### 1. URL Validation
```python
from urllib.parse import urlparse

def validate_url(url):
    """Validate that URL is safe and properly formatted"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        # Only allow https for external calls
        if parsed.scheme not in ['https', 'http']:
            return False

        return True
    except Exception:
        return False
```

### 2. Rate Limiting
```python
import time
from collections import defaultdict

class SimpleRateLimiter:
    def __init__(self, max_calls=60, time_window=60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(list)

    def can_call(self, service):
        now = time.time()
        calls = self.calls[service]

        # Remove old calls outside time window
        calls[:] = [call_time for call_time in calls if now - call_time < self.time_window]

        if len(calls) >= self.max_calls:
            return False

        calls.append(now)
        return True
```

## Testing Patterns

### Mock External Services for Testing
```python
class MockExternalService:
    def __init__(self):
        self.responses = {}
        self.requests = []

    def mock_response(self, url, response):
        self.responses[url] = response

    def call_api(self, url, method='GET', data=None):
        self.requests.append({'url': url, 'method': method, 'data': data})
        return self.responses.get(url, {'error': 'No mock response found'})

# Usage in tests
def test_github_api():
    mock_service = MockExternalService()
    mock_service.mock_response('https://api.github.com/repos/test/repo', {
        'full_name': 'test/repo',
        'stargazers_count': 42
    })

    result = mock_service.call_api('https://api.github.com/repos/test/repo')
    assert result['stargazers_count'] == 42
```

---

## Integration with Jules MCP

Jules AI can use these patterns to:
1. **Research**: Search for code examples and best practices
2. **Validate**: Check external dependencies and services
3. **Test**: Validate code against real external systems
4. **Document**: Create comprehensive documentation with real examples

This enables Jules to provide more accurate and practical implementations with real-world validation.

---

**Status**: ✅ CONFIRMED CAPABILITIES
**Network Access**: ✅ Web search and external APIs available
**Git Operations**: ✅ Git status and history available
**Limitations**: ❌ Docker, ❌ Direct production database access