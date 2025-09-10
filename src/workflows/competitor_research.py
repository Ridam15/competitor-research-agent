from crewai import Crew, Process, Task
from src.agents.researcher import researcher
from src.agents.analyzer import analyzer
from src.agents.reporter import reporter
from src.utils.logger import logger
from src.utils.config import validate_configuration, config
import time
import random
from typing import Union, Dict, Any

def create_enhanced_tasks(query: str) -> list:
    """Create enhanced task definitions with better descriptions and validation"""
    
    # Validate query input
    if not query or not query.strip():
        query = "top AI companies and competitors"
        logger.warning(f"Empty query provided, using default: {query}")
    
    # Task 1: Enhanced Research Task
    research_task = Task(
        description=f"""
        Conduct comprehensive competitor research for: "{query}"
        
        Your objectives:
        1. Search for and identify 5-7 key competitors in this space
        2. For each competitor, gather information about:
           - Company overview and business model
           - Key products and services offered
           - Pricing information (if publicly available)
           - Target market and customer base
           - Recent news and developments
           - Market positioning and competitive advantages
        3. Scrape their official websites to extract detailed information
        4. Focus on factual, up-to-date information from reliable sources
        
        Provide comprehensive raw data that can be analyzed for insights.
        """,
        agent=researcher,
        expected_output="""
        Detailed competitor profiles containing:
        - Company names and websites
        - Business model descriptions  
        - Product/service offerings
        - Pricing information (where available)
        - Market positioning data
        - Recent company developments
        """
    )

    # Task 2: Enhanced Analysis Task  
    analyze_task = Task(
        description=f"""
        Analyze the competitor research data and provide strategic insights for: "{query}"
        
        Your analysis should include:
        1. Market landscape overview and key trends
        2. Competitive positioning matrix comparing features, pricing, and market focus
        3. Identification of market gaps and opportunities
        4. Strengths and weaknesses analysis for each competitor
        5. Pricing strategy analysis and comparison
        6. Target audience and market segmentation insights
        7. Strategic recommendations based on competitive analysis
        
        Present insights in a structured, actionable format suitable for business decision-making.
        """,
        agent=analyzer,
        expected_output="""
        Structured competitive analysis including:
        - Executive summary of key findings
        - Competitive positioning matrix
        - Market opportunity analysis
        - Strategic recommendations
        - Key insights and actionable takeaways
        """,
        context=[research_task]  # Depends on research task
    )

    # Task 3: Enhanced Reporting Task
    report_task = Task(
        description=f"""
        Create a comprehensive competitor analysis report for: "{query}"
        
        Generate a professional PDF report that includes:
        1. Executive Summary highlighting key findings and recommendations
        2. Market Overview with industry trends and landscape analysis
        3. Detailed Competitor Profiles with company information, offerings, and positioning
        4. Competitive Matrix comparing features, pricing, and market positioning
        5. Market Opportunities and Gaps Analysis
        6. Strategic Recommendations for market entry or competitive positioning
        7. Appendix with detailed data and sources
        
        Use professional formatting with tables, charts, and clear section headers.
        Ensure the report is suitable for executive presentation and strategic planning.
        """,
        agent=reporter,
        expected_output="Professional PDF report saved as '[Query]_Competitor_Analysis_Report.pdf'",
        context=[analyze_task]  # Depends on analysis task
    )

    return [research_task, analyze_task, report_task]

def create_workflow(query: str = "top competitors to xAI") -> Union[str, Dict[str, Any]]:
    """
    Create and execute enhanced competitor research workflow with improved error handling
    
    Args:
        query: The competitor research query to analyze
        
    Returns:
        Union[str, Dict[str, Any]]: Result of the workflow execution
    """
    
    # Validate configuration before starting
    if not validate_configuration():
        return {
            "status": "error",
            "message": "Configuration validation failed. Please check your API keys.",
            "success": False
        }
    
    # Enhanced retry configuration
    rate_limits = config.rate_limit_config
    max_retries = rate_limits["max_retries"]
    base_delay = rate_limits["base_delay"]
    max_delay = rate_limits["max_delay"]
    
    logger.info(f"Starting enhanced competitor research workflow for: '{query}'")
    logger.info(f"Using configuration: max_retries={max_retries}, base_delay={base_delay}s")
    
    try:
        # Create enhanced tasks
        tasks = create_enhanced_tasks(query)
        
        # Create crew with enhanced configuration
        crew = Crew(
            agents=[researcher, analyzer, reporter],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,  # Enable crew memory for better context
            embedder={"provider": "google", "config": {"model": "models/embedding-001"}},  # Optional: better memory
            max_rpm=10,  # Requests per minute limit
            language="en"  # Specify language for better results
        )

        # Execute with enhanced retry logic and error categorization
        for attempt in range(max_retries):
            try:
                logger.info(f"Starting crew execution (attempt {attempt + 1}/{max_retries})")
                
                # Execute the workflow
                result = crew.kickoff()
                
                logger.info(f"Workflow completed successfully: {result}")
                
                return {
                    "status": "success", 
                    "result": result,
                    "query": query,
                    "attempts": attempt + 1,
                    "success": True
                }
                
            except Exception as e:
                error_str = str(e).lower()
                error_type = "unknown"
                
                # Categorize error types for better handling
                if any(term in error_str for term in ["rate_limit", "429", "ratelimiterror", "quota"]):
                    error_type = "rate_limit"
                elif any(term in error_str for term in ["api_key", "authentication", "unauthorized", "401", "403"]):
                    error_type = "authentication"
                elif any(term in error_str for term in ["network", "connection", "timeout", "502", "503", "504"]):
                    error_type = "network"
                elif any(term in error_str for term in ["model", "decommissioned", "deprecated", "invalid_request"]):
                    error_type = "model_config"
                
                logger.error(f"Attempt {attempt + 1} failed with {error_type} error: {e}")
                
                # Handle different error types
                if error_type == "rate_limit":
                    if attempt < max_retries - 1:
                        delay = min(base_delay * (config.rate_limit_config["backoff_factor"] ** attempt) + random.uniform(0, 2), max_delay)
                        logger.warning(f"Rate limit detected, waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        return {
                            "status": "error",
                            "error_type": "rate_limit",
                            "message": f"Rate limit exceeded after {max_retries} attempts. Please upgrade your API tier or try again later.",
                            "success": False,
                            "attempts": max_retries
                        }
                        
                elif error_type == "authentication":
                    return {
                        "status": "error", 
                        "error_type": "authentication",
                        "message": "API authentication failed. Please check your API keys in the .env file.",
                        "success": False,
                        "attempts": attempt + 1
                    }
                    
                elif error_type == "model_config":
                    return {
                        "status": "error",
                        "error_type": "model_config", 
                        "message": f"Model configuration error: {str(e)}. Please check your model settings.",
                        "success": False,
                        "attempts": attempt + 1
                    }
                    
                else:
                    # For other errors, retry with exponential backoff
                    if attempt < max_retries - 1:
                        delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                        logger.warning(f"Retrying after {delay:.1f}s due to: {e}")
                        time.sleep(delay)
                        continue
                    else:
                        return {
                            "status": "error",
                            "error_type": error_type,
                            "message": f"Workflow failed after {max_retries} attempts: {str(e)}",
                            "success": False,
                            "attempts": max_retries
                        }
        
        # Should not reach here, but handle it gracefully
        return {
            "status": "error",
            "message": "Workflow failed after all retry attempts",
            "success": False,
            "attempts": max_retries
        }
        
    except Exception as e:
        logger.error(f"Fatal error in workflow setup: {e}")
        return {
            "status": "error", 
            "error_type": "setup",
            "message": f"Failed to initialize workflow: {str(e)}",
            "success": False,
            "attempts": 0
        }