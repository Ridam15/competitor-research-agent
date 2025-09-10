from crewai.tools import BaseTool
import google.generativeai as genai
from src.utils.config import GEMINI_API_KEY
from src.utils.logger import logger
from pydantic import Field
import time
import random
import os

class LLMSummarizerTool(BaseTool):
    name: str = "LLM Summarizer Tool"
    description: str = "Summarizes text using Google's Gemini AI. Input: text to summarize."
    model: object = Field(default_factory=lambda: None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Updated to latest version
    
    def _run(self, content: str, prompt: str = "Summarize the following content:") -> str:
        """Required method for CrewAI BaseTool. Summarizes content using Gemini."""
        return self._summarize_with_gemini(content, prompt)

    def _summarize_with_gemini(self, content: str, prompt: str) -> str:
        """Summarize content using Gemini API with retry logic"""
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                import google.generativeai as genai
                
                # Configure Gemini API
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise Exception("GEMINI_API_KEY not found in environment variables")
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Latest Gemini 2.0 Flash Experimental
                
                # Combine prompt with content
                full_prompt = f"{prompt}\n\nContent to analyze:\n{content}"
                
                response = model.generate_content(full_prompt)
                return response.text
                
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Gemini API attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"All Gemini API attempts failed: {str(e)}")
                    return f"Error: Unable to process content with Gemini API - {str(e)}"