import aiohttp
import json
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode
from core.logger import logger

class WebSearchService:
    def __init__(self, searxng_instance_url: str = "https://searx.space"):
        """
        Initialize search service using SearXNG.
        
        Args:
            searxng_instance_url: URL of public SearXNG instance.
                                  Examples: "https://searx.space", 
                                            "https://searx.be",
                                            "https://search.ononoki.org"
        """
        self.instance_url = searxng_instance_url.rstrip('/')
        self.search_endpoint = f"{self.instance_url}/search"
        self.max_results = 8
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def search(
        self,
        query: str,
        safesearch: str = "1",      # 0=off, 1=moderate, 2=strict
        time_range: Optional[str] = None,  # "day", "week", "month", "year"
        language: str = "all",      # "all", "en", "ru", etc
        categories: str = "general", # "general", "news", "images", etc
        engines: Optional[str] = None  # Specific search engines to use
    ) -> str:
        """
        Perform search via SearXNG.
        
        Args:
            query: Search query
            safesearch: Safe search level (0, 1, 2)
            time_range: Time range limitation
            language: Language of results
            categories: Search categories
            engines: Specific search engines to use
            
        Returns:
            Formatted string with search results
        """
        try:
            # Prepare search parameters for SearXNG API
            params = {
                "q": query,
                "format": "json",
                "safesearch": safesearch,
                "language": language,
                "categories": categories,
            }
            
            if time_range:
                params["time_range"] = time_range
            
            if engines:
                params["engines"] = engines
                
            # Fetch search results
            results = await self._fetch_search_results(params)
            
            if not results:
                return "❌ No results found."
            
            # Format results
            formatted = self._format_results(results)
            
            # Create header
            header = f"🌐 Search results for: **{query}**"
            if time_range:
                time_map = {
                    "day": "day",
                    "week": "week", 
                    "month": "month",
                    "year": "year"
                }
                header += f" (last {time_map.get(time_range, time_range)})"
                
            return header + "\n\n" + "\n".join(formatted)
            
        except aiohttp.ClientError as e:
            logger.error(f"Network error during search: {e}")
            return f"❌ Network error: {str(e)}"
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return "❌ Error parsing search results."
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"❌ Search error: {str(e)}"
    
    async def _fetch_search_results(self, params: Dict[str, Any]) -> List[Dict]:
        """
        Execute HTTP request to SearXNG and retrieve results.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WebSearchService/1.0)",
            "Accept": "application/json",
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout, headers=headers) as session:
            try:
                async with session.get(self.search_endpoint, params=params) as response:
                    if response.status != 200:
                        logger.error(f"SearXNG returned status {response.status}")
                        # Try to get error details
                        try:
                            error_text = await response.text()
                            logger.error(f"Error response: {error_text[:200]}")
                        except:
                            pass
                        return []
                    
                    data = await response.json()
                    
                    # Check for results
                    if not data.get("results"):
                        # Check for suggestions
                        suggestions = data.get("suggestions", [])
                        if suggestions:
                            return [{
                                "title": "Did you mean:",
                                "content": ", ".join(suggestions[:3]),
                                "url": "",
                                "engine": "suggestion"
                            }]
                        return []
                    
                    # Return only the requested number of results
                    return data["results"][:self.max_results]
                    
            except aiohttp.ClientConnectorError:
                # Try fallback instances if current is unavailable
                return await self._try_fallback_search(params)
            except aiohttp.ServerTimeoutError:
                logger.error("Search request timed out")
                return []
    
    async def _try_fallback_search(self, params: Dict[str, Any]) -> List[Dict]:
        """
        Try alternative public SearXNG instances if primary is unavailable.
        """
        fallback_instances = [
            "https://searx.be",
            "https://search.ononoki.org",
            "https://searx.tuxcloud.net",
            "https://search.us.projectsegfau.lt"
        ]
        
        for instance in fallback_instances:
            if instance == self.instance_url:
                continue
                
            try:
                logger.info(f"Trying fallback instance: {instance}")
                temp_endpoint = f"{instance}/search"
                
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(temp_endpoint, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"Successfully used fallback instance: {instance}")
                            return data.get("results", [])[:self.max_results]
            except Exception as e:
                logger.debug(f"Fallback instance {instance} failed: {e}")
                continue
                
        logger.error("All SearXNG instances are unavailable")
        return []
    
    def _format_results(self, results: List[Dict]) -> List[str]:
        """
        Format search results into readable format.
        """
        formatted = []
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            content = result.get("content", result.get("body", "No description"))
            url = result.get("url", result.get("href", ""))
            engine = result.get("engine", "")
            
            # Truncate long descriptions
            if content and len(content) > 250:
                snippet = content[:247] + "..."
            else:
                snippet = content or "No description available"
            
            # Create formatted string
            result_text = f"**{i}.** {title}"
            
            if engine:
                result_text += f" (via {engine})"
                
            result_text += f"\n{snippet}"
            
            if url:
                # Shorten very long URLs for display
                display_url = url
                if len(url) > 60:
                    display_url = url[:57] + "..."
                result_text += f"\n🔗 {display_url}"
                
            formatted.append(result_text + "\n")
            
        return formatted
    
    async def get_available_engines(self) -> Dict[str, List[str]]:
        """
        Get list of available search engines in current instance.
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.instance_url}/info") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("engines", {})
                    else:
                        logger.error(f"Failed to fetch engines: HTTP {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"Error fetching engines: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """
        Check availability of SearXNG instance.
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.instance_url}/", timeout=5) as response:
                    return response.status == 200
        except Exception as e:
            logger.debug(f"Health check failed: {e}")
            return False
    
    async def search_with_retry(
        self,
        query: str,
        max_retries: int = 2,
        **kwargs
    ) -> str:
        """
        Perform search with retry logic.
        
        Args:
            query: Search query
            max_retries: Maximum number of retry attempts
            **kwargs: Additional search parameters
            
        Returns:
            Formatted search results or error message
        """
        for attempt in range(max_retries + 1):
            try:
                result = await self.search(query, **kwargs)
                if "❌" not in result or attempt == max_retries:
                    return result
                
                logger.info(f"Search attempt {attempt + 1} failed, retrying...")
                # Try a different instance on retry
                if attempt == 0:
                    await self._try_fallback_search({"q": query})
                    
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Search failed after {max_retries} attempts: {e}")
                    return f"❌ Search failed after multiple attempts: {str(e)}"
        
        return "❌ Unexpected error in search_with_retry"


# Utility class for convenience
class SearchHelper:
    @staticmethod
    def get_time_range_human_readable(time_range: Optional[str]) -> str:
        """Convert technical time range to human-readable format."""
        if not time_range:
            return "all time"
        
        ranges = {
            "day": "last day",
            "week": "last week",
            "month": "last month",
            "year": "last year"
        }
        return ranges.get(time_range, time_range)
    
    @staticmethod
    def get_safesearch_human_readable(level: str) -> str:
        """Convert safe search level to human-readable format."""
        levels = {
            "0": "off",
            "1": "moderate",
            "2": "strict"
        }
        return levels.get(level, "unknown")
    
    @staticmethod
    def build_search_url(query: str, instance_url: str = "https://searx.space") -> str:
        """Build a direct search URL for the given query."""
        base_url = instance_url.rstrip('/')
        encoded_query = urlencode({"q": query})
        return f"{base_url}/search?{encoded_query}"


# Example usage
async def example_usage():
    # Create service instance
    searcher = WebSearchService("https://searx.space")
    
    # Example search
    results = await searcher.search(
        query="artificial intelligence latest news",
        safesearch="1",
        time_range="week",
        language="en",
        categories="general"
    )
    
    print(results)
    
    # Health check
    is_healthy = await searcher.health_check()
    print(f"SearXNG available: {is_healthy}")
    
    # Get available engines
    engines = await searcher.get_available_engines()
    print(f"Available engines: {len(engines)}")
    
    # Search with retry
    results = await searcher.search_with_retry(
        query="python programming tutorials",
        max_retries=1
    )
    print(results)


# Configuration suggestions for different use cases
class SearchConfigs:
    """Pre-configured search settings for different use cases."""
    
    @staticmethod
    def news_search(query: str) -> dict:
        """Configuration for news searches."""
        return {
            "query": query,
            "categories": "news",
            "time_range": "week",
            "language": "en"
        }
    
    @staticmethod
    def technical_search(query: str) -> dict:
        """Configuration for technical/programming searches."""
        return {
            "query": query,
            "categories": "general",
            "engines": "google,bing,duckduckgo,wikipedia",
            "language": "en"
        }
    
    @staticmethod
    def safe_search(query: str) -> dict:
        """Configuration for family-safe searches."""
        return {
            "query": query,
            "safesearch": "2",
            "categories": "general"
        }