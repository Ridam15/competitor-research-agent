from crewai.tools import BaseTool
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from src.utils.logger import logger
import asyncio
import time
import random
from typing import Dict, List, Optional, Union, ClassVar
from urllib.parse import urlparse, urljoin
import re

class EnhancedScrapeTool(BaseTool):
    """Enhanced website scraper with intelligent content extraction and error handling"""
    
    name: str = "Enhanced Website Scraper Tool"
    description: str = """
    Advanced web scraping tool with intelligent content extraction capabilities.
    
    Features:
    - JavaScript execution and dynamic content handling
    - Intelligent selector detection for various website types
    - Robust error handling and retry logic
    - Respectful scraping with rate limiting
    
    Input: Website URL to scrape
    Output: Structured content including title, description, features, pricing, and key information
    """

    # Class variables to avoid Pydantic field conflicts
    TIMEOUT: ClassVar[int] = 30000  # 30 seconds
    RETRY_COUNT: ClassVar[int] = 3
    USER_AGENT: ClassVar[str] = "CompetitorResearchAgent/2.0 (Educational/Research Purpose)"
    
    # Common selectors for different types of content
    CONTENT_SELECTORS: ClassVar[Dict[str, List[str]]] = {
        'title': ['h1', 'title', '[data-testid="title"]', '.title', '#title'],
        'description': [
            '[data-testid="description"]', '.description', '#description',
            '.hero-text', '.subtitle', '.lead', '.intro', 'meta[name="description"]',
            '.company-description', '.about-text'
        ],
        'features': [
            '.feature', '.features li', '[data-testid="feature"]',
            '.benefits li', '.capabilities li', '.services li',
            '.product-features li', '.feature-list li'
        ],
        'pricing': [
            '.pricing', '.price', '[data-testid="price"]', '.cost',
            '.pricing-card', '.plan', '.subscription', '.tariff'
        ],
            'about': [
                '.about', '#about', '[data-testid="about"]',
                '.company-info', '.overview', '.summary'
            ],
            'contact': [
                '.contact', '#contact', '.contact-info',
                '[href*="mailto"]', '[href*="tel:"]'
            ]
        }

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and basic safety checks"""
        try:
            parsed = urlparse(url)
            # Check for valid scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Security: Block local/private URLs
            if parsed.netloc.lower() in ['localhost', '127.0.0.1', '0.0.0.0']:
                return False
            
            # Block file:// and other non-web schemes
            if parsed.scheme.lower() not in ['http', 'https']:
                return False
                
            return True
        except Exception:
            return False

    def _extract_with_selectors(self, page, selectors: List[str]) -> str:
        """Extract content using multiple selector strategies"""
        for selector in selectors:
            try:
                if selector.startswith('meta['):
                    # Handle meta tags
                    element = page.query_selector(selector)
                    if element:
                        return element.get_attribute('content') or ''
                else:
                    # Handle regular selectors
                    elements = page.query_selector_all(selector)
                    if elements:
                        # Join multiple elements with newlines
                        content = []
                        for elem in elements[:5]:  # Limit to first 5 elements
                            text = elem.inner_text().strip()
                            if text and len(text) > 10:  # Filter out very short text
                                content.append(text)
                        if content:
                            return '\n'.join(content)
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        return ""

    def _extract_structured_content(self, page) -> Dict[str, str]:
        """Extract structured content from the page"""
        content = {}
        
        try:
            # Extract title
            title = self._extract_with_selectors(page, self.CONTENT_SELECTORS['title'])
            if not title:
                title = page.title() or "No title found"
            content['title'] = title[:200]  # Limit length
            
            # Extract description/about
            description = self._extract_with_selectors(page, self.CONTENT_SELECTORS['description'])
            if not description and 'about' in self.CONTENT_SELECTORS:
                description = self._extract_with_selectors(page, self.CONTENT_SELECTORS['about'])
            content['description'] = description[:500] if description else "No description available"
            
            # Extract features
            features = self._extract_with_selectors(page, self.CONTENT_SELECTORS['features'])
            content['features'] = features[:300] if features else "No features information found"
            
            # Extract pricing
            pricing = self._extract_with_selectors(page, self.CONTENT_SELECTORS['pricing'])
            content['pricing'] = pricing[:200] if pricing else "No pricing information available"
            
            # Extract contact information
            contact = self._extract_with_selectors(page, self.CONTENT_SELECTORS['contact'])
            content['contact'] = contact[:200] if contact else "No contact information found"
            
            # Extract general page text as fallback
            try:
                # Get the main content area
                main_content = page.query_selector('main') or page.query_selector('body')
                if main_content:
                    full_text = main_content.inner_text()
                    # Clean and limit text
                    clean_text = re.sub(r'\s+', ' ', full_text).strip()
                    content['full_text_preview'] = clean_text[:300] + "..." if len(clean_text) > 300 else clean_text
            except Exception:
                content['full_text_preview'] = "Could not extract page text"
                
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            content = {
                'title': 'Extraction Error',
                'description': f'Failed to extract content: {str(e)}',
                'features': 'N/A',
                'pricing': 'N/A',
                'contact': 'N/A',
                'full_text_preview': 'N/A'
            }
        
        return content

    def _scrape_with_playwright(self, url: str) -> Dict[str, str]:
        """Scrape website using Playwright with comprehensive error handling"""
        
        for attempt in range(self.RETRY_COUNT):
            try:
                logger.info(f"Scraping {url} (attempt {attempt + 1}/{self.RETRY_COUNT})")
                
                with sync_playwright() as p:
                    # Launch browser with configuration
                    browser = p.chromium.launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-blink-features=AutomationControlled',
                            '--disable-extensions'
                        ]
                    )
                    
                    # Create context with realistic settings
                    context = browser.new_context(
                        user_agent=self.USER_AGENT,
                        viewport={'width': 1920, 'height': 1080},
                        locale='en-US',
                        timezone_id='America/New_York'
                    )
                    
                    page = context.new_page()
                    
                    # Set timeout and navigate
                    page.set_default_timeout(self.TIMEOUT)
                    
                    try:
                        # Navigate to page
                        response = page.goto(
                            url, 
                            wait_until="domcontentloaded",
                            timeout=self.TIMEOUT
                        )
                        
                        if not response:
                            raise Exception("Failed to load page - no response")
                        
                        if response.status >= 400:
                            raise Exception(f"HTTP {response.status}: {response.status_text}")
                        
                        # Wait for dynamic content to load
                        try:
                            page.wait_for_load_state("networkidle", timeout=10000)
                        except Exception:
                            # Continue if networkidle timeout - some sites keep loading
                            logger.debug("Network idle timeout - continuing with available content")
                        
                        # Extract structured content
                        content = self._extract_structured_content(page)
                        content['url'] = url
                        content['status'] = 'success'
                        content['scrape_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        
                        logger.info(f"Successfully scraped {url}")
                        return content
                        
                    finally:
                        browser.close()
                        
            except Exception as e:
                error_msg = str(e).lower()
                logger.warning(f"Scraping attempt {attempt + 1} failed for {url}: {e}")
                
                # Categorize errors for better handling
                if "timeout" in error_msg:
                    error_type = "timeout"
                elif "network" in error_msg or "connection" in error_msg:
                    error_type = "network"
                elif "403" in error_msg or "blocked" in error_msg:
                    error_type = "blocked"
                elif "404" in error_msg or "not found" in error_msg:
                    error_type = "not_found"
                else:
                    error_type = "unknown"
                
                # Retry logic with exponential backoff
                if attempt < self.RETRY_COUNT - 1 and error_type not in ["blocked", "not_found"]:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {delay:.1f}s due to {error_type} error...")
                    time.sleep(delay)
                    continue
                else:
                    # Final failure - return error information
                    return {
                        'url': url,
                        'status': 'error',
                        'error_type': error_type,
                        'title': f'Scraping Failed - {error_type.title()} Error',
                        'description': f'Unable to scrape {url}: {str(e)}',
                        'features': 'N/A - Scraping failed',
                        'pricing': 'N/A - Scraping failed',
                        'contact': 'N/A - Scraping failed',
                        'full_text_preview': f'Error: {str(e)}',
                        'scrape_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'suggestions': self._get_error_suggestions(error_type)
                    }
        
        # Should not reach here but handle gracefully
        return {
            'url': url,
            'status': 'error',
            'title': 'Scraping Failed',
            'description': f'Failed to scrape {url} after {self.RETRY_COUNT} attempts',
            'features': 'N/A',
            'pricing': 'N/A',
            'contact': 'N/A',
            'full_text_preview': 'Scraping failed',
            'scrape_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_error_suggestions(self, error_type: str) -> str:
        """Get suggestions based on error type"""
        suggestions = {
            "timeout": "Try again later or check if the website is slow to load",
            "network": "Check your internet connection and try again", 
            "blocked": "Website may block automated access - try manual visit",
            "not_found": "Check if the URL is correct and the page exists",
            "unknown": "Try a different URL or check website accessibility"
        }
        return suggestions.get(error_type, "Try again later")

    def _format_scraping_results(self, content: Dict[str, str]) -> str:
        """Format scraping results into readable text"""
        
        if content.get('status') == 'error':
            return f"""
🚫 Scraping Error for {content['url']}
Error Type: {content.get('error_type', 'Unknown')}
Details: {content['description']}
Suggestions: {content.get('suggestions', 'Try again later')}
Timestamp: {content.get('scrape_timestamp', 'N/A')}
"""
        
        return f"""
🌐 Website Analysis: {content['title']}
URL: {content['url']}
Scraped: {content.get('scrape_timestamp', 'N/A')}

📋 Description:
{content['description']}

⭐ Key Features:
{content['features']}

💰 Pricing Information:
{content['pricing']}

📞 Contact Information:
{content['contact']}

📄 Content Preview:
{content['full_text_preview']}

Status: ✅ Successfully scraped
"""

    def _run(self, url: str) -> str:
        """
        Enhanced scraping execution with comprehensive error handling
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Formatted scraping results with structured content
        """
        try:
            # Input validation
            if not url or not url.strip():
                return "Error: Empty URL provided"
            
            url = url.strip()
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Validate URL
            if not self._is_valid_url(url):
                return f"Error: Invalid URL format or blocked URL: {url}"
            
            logger.info(f"Starting enhanced scraping for: {url}")
            
            # Perform scraping
            content = self._scrape_with_playwright(url)
            
            # Format and return results
            formatted_results = self._format_scraping_results(content)
            
            if content.get('status') == 'success':
                logger.info(f"Scraping completed successfully for: {url}")
            else:
                logger.warning(f"Scraping completed with errors for: {url}")
            
            return formatted_results
            
        except Exception as e:
            error_msg = f"Scrape tool failed with unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"Critical Error: {error_msg}. Please check the URL and try again."

    # Async methods for backward compatibility
    async def _arun(self, url: str) -> str:
        """Async wrapper for the sync _run method"""
        return self._run(url)

# Alias for backwards compatibility
ScrapeTool = EnhancedScrapeTool