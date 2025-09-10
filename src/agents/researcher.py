from crewai import Agent
from src.tools.search_tool import SearchTool
from src.tools.scrape_tool import ScrapeTool
from src.utils.config import get_configured_llm
from src.utils.logger import logger

# Create researcher agent with improved configuration
researcher = Agent(
    role="Senior Competitor Intelligence Analyst",
    goal="""Conduct comprehensive competitor research by searching for companies, analyzing their 
    digital presence, and extracting detailed information about their products, services, 
    pricing models, and market positioning.""",
    
    backstory="""You are an experienced market research analyst with expertise in competitive 
    intelligence gathering. You excel at finding relevant competitors, understanding their 
    business models, and extracting actionable insights from their online presence. You use 
    systematic approaches to ensure comprehensive data collection while being respectful 
    of website terms of service.""",
    
    tools=[SearchTool(), ScrapeTool()],
    llm=get_configured_llm(),  # Use centrally configured LLM
    verbose=True,
    allow_delegation=False,
    max_iter=5,  # Increased iterations for better results
    max_execution_time=600,  # 10 minutes max for thorough research
    memory=True,  # Enable memory for better context retention
    step_callback=lambda step: logger.info(f"Researcher step: {step.action}") if hasattr(step, 'action') else None
)