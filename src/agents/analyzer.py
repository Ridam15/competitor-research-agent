from crewai import Agent
from src.tools.llm_tool import LLMSummarizerTool
from src.utils.config import get_configured_llm
from src.utils.logger import logger

analyzer = Agent(
    role="Senior Business Intelligence Analyst",
    goal="""Analyze competitor data to extract meaningful insights, identify market trends, 
    competitive advantages, pricing strategies, and provide strategic recommendations 
    based on comprehensive data analysis.""",
    
    backstory="""You are a seasoned business analyst with deep expertise in competitive 
    analysis and market intelligence. You excel at processing raw data to identify 
    patterns, competitive gaps, market opportunities, and strategic insights. You 
    provide clear, actionable analysis that helps businesses understand their 
    competitive landscape and make informed decisions.""",
    
    tools=[LLMSummarizerTool()],
    llm=get_configured_llm(),  # Use centrally configured LLM
    verbose=True,
    allow_delegation=False,
    max_iter=3,  # Sufficient for analysis tasks
    max_execution_time=400,  # 6.5 minutes for thorough analysis
    memory=True,  # Enable memory for context retention
    step_callback=lambda step: logger.info(f"Analyzer step: {step.action}") if hasattr(step, 'action') else None
)