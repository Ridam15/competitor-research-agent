import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import google.generativeai as genai
from src.utils.logger import logger

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration management with validation and fallbacks"""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") 
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Model configurations with fallbacks
        self.primary_model = "gemini/gemini-2.0-flash-exp"
        self.fallback_models = [
            "groq/llama-3.1-70b-versatile",  # Updated to supported model
            "groq/llama-3.1-8b-instant",
            "groq/mixtral-8x7b-32768"
        ]
        
        # Validate and configure APIs
        self._validate_and_configure()
    
    def _validate_and_configure(self):
        """Validate API keys and configure services"""
        if not self.gemini_api_key or self.gemini_api_key == "YOUR_GEMINI_API_KEY_HERE":
            logger.warning("GEMINI_API_KEY not properly configured")
            self._print_gemini_setup_instructions()
        else:
            try:
                genai.configure(api_key=self.gemini_api_key)
                logger.info("Gemini API configured successfully")
            except Exception as e:
                logger.error(f"Failed to configure Gemini API: {e}")
        
        if not self.groq_api_key:
            logger.warning("GROQ_API_KEY not configured - fallback options limited")
        
        if not self.openai_api_key:
            logger.info("OPENAI_API_KEY not configured - using available providers")
    
    def _print_gemini_setup_instructions(self):
        """Print setup instructions for Gemini API"""
        print("\n🚨 GEMINI_API_KEY Configuration Required!")
        print("=" * 50)
        print("1. Visit: https://aistudio.google.com/")
        print("2. Sign in with your Google account")
        print("3. Click 'Get API key' and create a new key")
        print("4. Add to your .env file: GEMINI_API_KEY='your_actual_key_here'")
        print("5. Run the application again")
        print("=" * 50)
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get the best available model configuration"""
        if self.gemini_api_key:
            return {
                "provider": "gemini",
                "model": "gemini-2.0-flash-exp",
                "api_key": self.gemini_api_key
            }
        elif self.groq_api_key:
            return {
                "provider": "groq", 
                "model": "llama-3.1-70b-versatile",
                "api_key": self.groq_api_key
            }
        else:
            raise ValueError("No valid API keys configured. Please set up Gemini or Groq API keys.")
    
    @property
    def rate_limit_config(self) -> Dict[str, int]:
        """Rate limiting configuration"""
        return {
            "max_retries": 5,
            "base_delay": 2,
            "max_delay": 60,
            "backoff_factor": 2
        }

# Global configuration instance
config = Config()

# Legacy compatibility
GROQ_API_KEY = config.groq_api_key
GEMINI_API_KEY = config.gemini_api_key

def get_configured_llm() -> str:
    """Get the configured LLM model string for CrewAI"""
    model_config = config.get_model_config()
    
    if model_config["provider"] == "gemini":
        return f"gemini/{model_config['model']}"
    elif model_config["provider"] == "groq":
        return f"groq/{model_config['model']}"
    else:
        # Default fallback
        return "gemini/gemini-2.0-flash-exp"

def validate_configuration() -> bool:
    """Validate that all required configuration is present"""
    try:
        config.get_model_config()
        return True
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        return False