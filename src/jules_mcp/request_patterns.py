"""Request Pattern Implementation for Jules MCP Server

This module implements the Request Pattern Specification (RPS) for external API integration,
web search capabilities, and validated external service interactions as defined in
RPS_JULES_INTEGRATION.md
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import time
import re
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from collections import defaultdict
import random

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Standard API response structure"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    status: Optional[int] = None
    headers: Optional[Dict] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class SimpleRateLimiter:
    """Simple rate limiter for external API calls"""

    def __init__(self, max_calls: int = 60, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(list)

    def can_call(self, service: str) -> bool:
        """Check if we can make a call to the service"""
        now = time.time()
        calls = self.calls[service]

        # Remove old calls outside time window
        calls[:] = [call_time for call_time in calls if now - call_time < self.time_window]

        if len(calls) >= self.max_calls:
            return False

        calls.append(now)
        return True


class ExternalAPIManager:
    """Manages external API calls with retry logic and error handling"""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.rate_limiter = SimpleRateLimiter()

    def validate_url(self, url: str) -> bool:
        """Validate that URL is safe and properly formatted"""
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False

            # Only allow https for external calls
            if parsed.scheme not in ['https', 'http']:
                return False

            return True
        except Exception:
            return False

    async def call_external_api(
        self,
        method: str,
        url: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 10,
        service_name: str = "default"
    ) -> APIResponse:
        """Standard pattern for external API calls with retry logic"""

        if not self.validate_url(url):
            return APIResponse(
                success=False,
                error="Invalid URL format",
                status=None
            )

        if not self.rate_limiter.can_call(service_name):
            return APIResponse(
                success=False,
                error="Rate limit exceeded",
                status=429
            )

        async def make_request():
            try:
                if method.upper() == 'GET':
                    req = urllib.request.Request(url, headers=headers or {})
                else:
                    json_data = json.dumps(data).encode('utf-8') if data else None
                    req = urllib.request.Request(url, data=json_data, headers=headers or {})
                    req.get_method = lambda: method.upper()

                with urllib.request.urlopen(req, timeout=timeout) as response:
                    response_data = response.read().decode('utf-8')

                    try:
                        parsed_data = json.loads(response_data)
                    except json.JSONDecodeError:
                        parsed_data = {"raw_response": response_data}

                    return APIResponse(
                        success=True,
                        data=parsed_data,
                        status=response.status,
                        headers=dict(response.headers)
                    )

            except urllib.error.HTTPError as e:
                return APIResponse(
                    success=False,
                    error=f'HTTP {e.code}: {e.reason}',
                    status=e.code
                )
            except urllib.error.URLError as e:
                return APIResponse(
                    success=False,
                    error=f'URL Error: {e.reason}',
                    status=None
                )
            except Exception as e:
                return APIResponse(
                    success=False,
                    error=f'Unexpected error: {str(e)}',
                    status=None
                )

        # Retry logic with exponential backoff
        last_result = None
        for attempt in range(self.max_retries):
            try:
                result = await make_request()

                if result.success or (result.status and result.status < 500):
                    # Success or client error (don't retry 4xx)
                    return result

                if attempt < self.max_retries - 1:
                    delay = min(self.base_delay * (2 ** attempt) + random.uniform(0, 1), self.max_delay)
                    logger.info(f"Retry {attempt + 1}/{self.max_retries} in {delay:.2f}s for {url}")
                    await asyncio.sleep(delay)
                    continue

                last_result = result

            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = min(self.base_delay * (2 ** attempt) + random.uniform(0, 1), self.max_delay)
                    logger.info(f"Retry {attempt + 1}/{self.max_retries} for error: {str(e)}")
                    await asyncio.sleep(delay)
                    continue
                last_result = APIResponse(success=False, error=str(e))

        return last_result

    async def get_github_repo(self, owner: str, repo: str) -> APIResponse:
        """Get GitHub repository information"""
        url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {
            'User-Agent': 'Jules-MCP-Client/1.0',
            'Accept': 'application/vnd.github.v3+json'
        }
        return await self.call_external_api('GET', url, headers=headers, service_name="github_api")

    async def get_github_commits(self, owner: str, repo: str, limit: int = 5) -> APIResponse:
        """Get recent commits for a GitHub repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page={limit}"
        headers = {
            'User-Agent': 'Jules-MCP-Client/1.0',
            'Accept': 'application/vnd.github.v3+json'
        }
        return await self.call_external_api('GET', url, headers=headers, service_name="github_api")


class WebSearchManager:
    """Manages web search operations using DuckDuckGo"""

    def __init__(self, max_results: int = 10):
        self.max_results = max_results

    async def perform_web_search(self, query: str) -> APIResponse:
        """Search DuckDuckGo for information"""
        try:
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://duckduckgo.com/html/?q={encoded_query}"

            # Use a simple request for search
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
                        title = html.unescape(title_match.group(1).strip())
                        url = url_match.group(1).strip()

                        # Clean up URL
                        if url.startswith('/l/?uddg='):
                            url = url[7:]  # Remove DuckDuckGo redirect prefix

                        results.append({
                            'title': title,
                            'url': url
                        })

                        if len(results) >= self.max_results:
                            break

            return APIResponse(
                success=True,
                data={
                    'query': query,
                    'results': results,
                    'count': len(results)
                }
            )

        except Exception as e:
            return APIResponse(
                success=False,
                error=f'Search failed: {str(e)}',
                data={'query': query}
            )

    async def search_code_examples(self, search_query: str) -> APIResponse:
        """Search for code examples and best practices"""
        # Web search for code examples
        search_result = await self.perform_web_search(f"{search_query} code example best practices")

        if not search_result.success:
            return search_result

        # Filter for code-related results
        code_examples = []
        for result in search_result.data.get('results', []):
            # Check if result looks like code documentation
            title_lower = result['title'].lower()
            if any(keyword in title_lower for keyword in ['code', 'example', 'tutorial', 'guide', 'pattern']):
                code_examples.append(result)

        return APIResponse(
            success=True,
            data={
                'query': search_query,
                'total_results': search_result.data.get('count', 0),
                'code_examples': code_examples,
                'recommended': code_examples[:3]  # Top 3 recommendations
            }
        )


import html


class RequestPatternManager:
    """Main manager for all request pattern operations"""

    def __init__(self):
        self.api_manager = ExternalAPIManager()
        self.search_manager = WebSearchManager()

    async def research_github_repository(self, repo_url: str) -> APIResponse:
        """Research a GitHub repository for implementation patterns"""
        try:
            # Extract owner/repo from URL
            parts = repo_url.strip('/').split('/')
            if len(parts) >= 2:
                owner, repo = parts[-2], parts[-1]
            else:
                return APIResponse(
                    success=False,
                    error='Invalid repository URL format'
                )

            # Get repo info
            repo_data = await self.api_manager.get_github_repo(owner, repo)

            if not repo_data.success:
                return repo_data

            # Get commit history for recent changes
            commits_data = await self.api_manager.get_github_commits(owner, repo, 5)

            implementation_patterns = self._extract_patterns(repo_data.data)

            return APIResponse(
                success=True,
                data={
                    'repository': repo_data.data,
                    'recent_commits': commits_data.data if commits_data.success else [],
                    'implementation_patterns': implementation_patterns,
                    'repo_url': repo_url
                }
            )

        except Exception as e:
            return APIResponse(
                success=False,
                error=f'Research failed: {str(e)}'
            )

    def _extract_patterns(self, repo_data: Dict) -> List[str]:
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
        if 'python' in description:
            patterns.append("Python patterns")
        if 'docker' in description:
            patterns.append("Docker containerization")
        if 'kubernetes' in description:
            patterns.append("Kubernetes deployment")

        return patterns

    async def validate_external_dependencies(self, dependencies: List[Dict]) -> APIResponse:
        """Validate that external dependencies are available"""
        results = []

        for dep in dependencies:
            if dep['type'] == 'github_repo':
                repo_data = await self.api_manager.get_github_repo(
                    dep['owner'], dep['repo']
                )

                if repo_data.success:
                    results.append({
                        'dependency': dep,
                        'status': 'AVAILABLE',
                        'info': {
                            'stars': repo_data.data.get('stargazers_count', 0),
                            'language': repo_data.data.get('language'),
                            'last_updated': repo_data.data.get('updated_at')
                        }
                    })
                else:
                    results.append({
                        'dependency': dep,
                        'status': 'FAILED',
                        'error': repo_data.error
                    })

            elif dep['type'] == 'web_service':
                # Test if web service is reachable
                service_data = await self.api_manager.call_external_api(
                    'GET', dep['url'], timeout=5
                )

                results.append({
                    'dependency': dep,
                    'status': 'AVAILABLE' if service_data.success else 'FAILED',
                    'response': service_data.__dict__
                })

        return APIResponse(
            success=True,
            data={
                'total_dependencies': len(dependencies),
                'available': len([r for r in results if r['status'] == 'AVAILABLE']),
                'failed': len([r for r in results if r['status'] == 'FAILED']),
                'details': results
            }
        )

    async def search_best_practices(self, topic: str) -> APIResponse:
        """Search for best practices and implementation patterns"""
        return await self.search_manager.search_code_examples(topic)


# Global instance for use across the application
request_manager = RequestPatternManager()