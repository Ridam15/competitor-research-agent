from crewai import Agent
from src.tools.pdf_tool import PDFReportTool
from src.utils.config import get_configured_llm
from src.utils.logger import logger

reporter = Agent(
    role="Senior Business Report Writer",
    goal="""Generate comprehensive, professional competitor analysis reports that present 
    findings in a clear, actionable format with executive summaries, detailed analysis, 
    competitive matrices, and strategic recommendations.""",
    
    backstory="""You are an expert business report writer with extensive experience in 
    creating high-quality competitive intelligence reports. You excel at presenting 
    complex analysis in clear, professional formats that executives and decision-makers 
    can easily understand and act upon. Your reports are known for their clarity, 
    thoroughness, and actionable insights.""",
    
    tools=[PDFReportTool()],
    llm=get_configured_llm(),  # Use centrally configured LLM
    verbose=True,
    allow_delegation=False,
    max_iter=3,  # Allow iterations for report refinement
    max_execution_time=300,  # 5 minutes for report generation
    memory=True,  # Enable memory for context retention
    step_callback=lambda step: logger.info(f"Reporter step: {step.action}") if hasattr(step, 'action') else None
)