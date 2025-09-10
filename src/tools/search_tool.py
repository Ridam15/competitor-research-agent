from crewai.tools import BaseTool
from duckduckgo_search import DDGS
from src.utils.logger import logger
import time
import random
from typing import List, Dict, Any, Optional, ClassVar
from dataclasses import dataclass
from pydantic import Field

@dataclass
class SearchResult:
    """Structured search result data class"""
    title: str
    url: str
    snippet: str
    source: str = "DuckDuckGo"

class SearchTool(BaseTool):
    """Enhanced competitor search tool with intelligent query optimization and error handling"""
    
    name: str = "Enhanced Competitor Search Tool"
    description: str = """
    Advanced web search tool for competitor discovery and market research.
    Optimizes search queries, handles rate limits, and provides structured results.
    
    Input: Search query string (e.g., "competitors to OpenAI", "fintech companies")
    Output: Formatted search results with titles, URLs, and descriptions
    """

    # Define configuration as class variables to avoid Pydantic field conflicts
    MAX_RESULTS: ClassVar[int] = 8
    RETRY_COUNT: ClassVar[int] = 3
    BASE_DELAY: ClassVar[float] = 1.0
    
    def _optimize_query(self, query: str) -> List[str]:
        """Generate optimized search queries for better competitor discovery"""
        base_query = query.strip()
        
        # Generate multiple query variations for comprehensive results
        queries = [base_query]
        
        # Add specific competitor-focused variations
        if "competitor" not in base_query.lower():
            queries.extend([
                f"{base_query} competitors",
                f"{base_query} alternatives", 
                f"companies like {base_query}",
                f"top {base_query} market leaders"
            ])
        
        # Add market research variations
        if not any(term in base_query.lower() for term in ["market", "industry", "analysis"]):
            queries.extend([
                f"{base_query} market analysis",
                f"{base_query} industry leaders"
            ])
        
        return queries[:3]  # Return top 3 most relevant queries

    def _search_with_retry(self, query: str) -> List[SearchResult]:
        """Execute search with retry logic and rate limiting"""
        for attempt in range(self.RETRY_COUNT):
            try:
                logger.info(f"Searching for: '{query}' (attempt {attempt + 1}/{self.RETRY_COUNT})")
                
                with DDGS() as ddgs:
                    # Search with various parameters for better results
                    raw_results = list(ddgs.text(
                        query, 
                        max_results=self.MAX_RESULTS,
                        region='us-en',  # English results
                        safesearch='moderate',  # Balanced filtering
                        timelimit='y'  # Focus on recent results
                    ))
                
                # Convert to structured results
                results = []
                for result in raw_results:
                    try:
                        search_result = SearchResult(
                            title=result.get('title', 'No title'),
                            url=result.get('href', ''),
                            snippet=result.get('body', 'No description available')
                        )
                        results.append(search_result)
                    except Exception as e:
                        logger.warning(f"Failed to process search result: {e}")
                        continue
                
                logger.info(f"Successfully retrieved {len(results)} results for query: '{query}'")
                return results
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if attempt < self.RETRY_COUNT - 1:
                    # Calculate delay with exponential backoff and jitter
                    delay = self.BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Search attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All search attempts failed for query '{query}': {e}")
                    return [SearchResult(
                        title="Search Error",
                        url="",
                        snippet=f"Search failed after {self.RETRY_COUNT} attempts: {str(e)}"
                    )]
        
        return []

    def _format_results(self, results: List[SearchResult], query: str) -> str:
        """Format search results into a structured, readable format"""
        if not results:
            return f"No search results found for query: '{query}'"
        
        formatted_output = f"🔍 Search Results for: '{query}'\n"
        formatted_output += "=" * 60 + "\n\n"
        
        for i, result in enumerate(results, 1):
            formatted_output += f"📄 Result {i}:\n"
            formatted_output += f"   Title: {result.title}\n"
            formatted_output += f"   URL: {result.url}\n"
            formatted_output += f"   Description: {result.snippet[:200]}{'...' if len(result.snippet) > 200 else ''}\n"
            formatted_output += "-" * 40 + "\n"
        
        # Add metadata
        formatted_output += f"\n📊 Summary: Found {len(results)} results from {results[0].source if results else 'search engine'}\n"
        
        return formatted_output

    def _filter_and_rank_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Filter and rank results based on relevance and quality"""
        if not results:
            return results
        
        # Filter out low-quality results
        filtered_results = []
        
        for result in results:
            # Skip results with poor quality indicators
            if (len(result.title) < 10 or 
                'error' in result.title.lower() or
                'not found' in result.snippet.lower() or
                result.url.startswith('javascript:')):
                continue
            
            # Prioritize official company websites and reputable sources
            quality_score = 0
            
            # Higher score for official domains
            if any(domain in result.url.lower() for domain in ['.com/', '.org/', '.net/']):
                quality_score += 2
            
            # Higher score for business-related content
            if any(term in result.title.lower() for term in ['company', 'business', 'startup', 'enterprise']):
                quality_score += 1
            
            # Higher score for relevant content
            query_words = query.lower().split()
            title_words = result.title.lower().split()
            snippet_words = result.snippet.lower().split()
            
            relevance = (
                sum(1 for word in query_words if word in title_words) * 2 +  # Title matches weighted more
                sum(1 for word in query_words if word in snippet_words)
            )
            
            # Add quality_score as an attribute to the result
            setattr(result, 'quality_score', quality_score + relevance)
            filtered_results.append(result)
        
        # Sort by quality score (descending)
        filtered_results.sort(key=lambda x: getattr(x, 'quality_score', 0), reverse=True)
        
        # Return top results
        return filtered_results[:self.MAX_RESULTS]

    def _run(self, query: str) -> str:
        """
        Enhanced search execution with query optimization and comprehensive results
        
        Args:
            query: Search query string
            
        Returns:
            Formatted search results string
        """
        try:
            if not query or not query.strip():
                return "Error: Empty search query provided"
            
            logger.info(f"Starting enhanced search for: '{query}'")
            
            # Optimize search queries
            optimized_queries = self._optimize_query(query)
            
            all_results = []
            
            # Execute searches for each optimized query
            for opt_query in optimized_queries:
                results = self._search_with_retry(opt_query)
                all_results.extend(results)
                
                # Small delay between queries to be respectful
                if len(optimized_queries) > 1:
                    time.sleep(0.5)
            
            # Remove duplicates based on URL
            unique_results = {}
            for result in all_results:
                if result.url and result.url not in unique_results:
                    unique_results[result.url] = result
            
            final_results = list(unique_results.values())
            
            # Filter and rank results
            final_results = self._filter_and_rank_results(final_results, query)
            
            # Format and return results
            formatted_results = self._format_results(final_results, query)
            
            logger.info(f"Search completed successfully. Returning {len(final_results)} unique, filtered results.")
            
            return formatted_results
            
        except Exception as e:
            error_msg = f"Search tool failed with unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"Search Error: {error_msg}. Please try a different query or check your internet connection."