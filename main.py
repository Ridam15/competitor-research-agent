#!/usr/bin/env python3
"""
Competitor Research Agent - Main Entry Point

Advanced AI-powered competitive intelligence system using multi-agent architecture
to automate competitor research, analysis, and reporting.

Usage:
    python main.py "your competitor research query"
    
Examples:
    python main.py "competitors to OpenAI"
    python main.py "top fintech companies 2024"
    python main.py "cloud computing providers"
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

from src.workflows.competitor_research import create_workflow
from src.utils.logger import logger
from src.utils.config import validate_configuration, config

def print_banner():
    """Print application banner with version info"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                 🤖 COMPETITOR RESEARCH AGENT                 ║
    ║                                                              ║
    ║              AI-Powered Market Intelligence                  ║
    ║                    v2.0.0 Enhanced                          ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_usage_examples():
    """Print usage examples for the user"""
    examples = """
    📋 Usage Examples:
    ─────────────────────────────────────────────────────────────
    • python main.py "competitors to OpenAI"
    • python main.py "top fintech companies 2024"  
    • python main.py "cloud infrastructure providers"
    • python main.py "project management tools comparison"
    • python main.py "AI image generation platforms"
    ─────────────────────────────────────────────────────────────
    """
    print(examples)

def format_result_output(result):
    """Format and display the workflow result"""
    if isinstance(result, dict):
        if result.get("success"):
            print("\n✅ Analysis completed successfully!")
            print(f"📊 Query analyzed: {result.get('query', 'N/A')}")
            print(f"🔄 Attempts required: {result.get('attempts', 'N/A')}")
            
            # Handle CrewOutput object
            actual_result = result.get('result')
            if hasattr(actual_result, 'raw'):
                output_file = str(actual_result.raw)
                print(f"📄 Report generated: {output_file}")
                
                # Check if file exists and provide additional info
                if Path(output_file).exists():
                    file_size = Path(output_file).stat().st_size
                    print(f"📁 File size: {file_size:,} bytes")
                    print(f"📍 Full path: {Path(output_file).absolute()}")
            else:
                print(f"📝 Result: {actual_result}")
                
        else:
            print(f"\n❌ Analysis failed!")
            print(f"🔍 Error type: {result.get('error_type', 'Unknown')}")
            print(f"💬 Message: {result.get('message', 'No details available')}")
            print(f"🔄 Attempts made: {result.get('attempts', 'N/A')}")
            
            # Provide specific guidance based on error type
            error_type = result.get('error_type')
            if error_type == 'rate_limit':
                print("\n💡 Suggestion: Wait a few minutes and try again, or upgrade your API tier")
            elif error_type == 'authentication':
                print("\n💡 Suggestion: Check your API keys in the .env file")
            elif error_type == 'model_config':
                print("\n💡 Suggestion: Update your model configuration in agents files")
                
    else:
        # Handle legacy string results
        print(f"\n📝 Result: {result}")

def setup_argument_parser():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(
        description="AI-Powered Competitor Research Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "competitors to Tesla"
  %(prog)s "top SaaS companies 2024"
  %(prog)s --query "fintech startups" --output custom_report.pdf
        """
    )
    
    parser.add_argument(
        'query', 
        nargs='?',
        default=None,
        help='Competitor research query (e.g., "competitors to OpenAI")'
    )
    
    parser.add_argument(
        '--query', '-q',
        dest='query_flag',
        help='Alternative way to specify query'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Custom output filename for the report'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--config-check',
        action='store_true', 
        help='Check configuration and exit'
    )
    
    parser.add_argument(
        '--examples',
        action='store_true',
        help='Show usage examples and exit'
    )
    
    return parser

def main():
    """Main application entry point with enhanced error handling"""
    try:
        # Setup argument parsing
        parser = setup_argument_parser()
        args = parser.parse_args()
        
        # Handle special flags
        if args.examples:
            print_banner()
            print_usage_examples()
            return 0
            
        if args.config_check:
            print_banner()
            print("🔧 Checking configuration...")
            if validate_configuration():
                print("✅ Configuration is valid!")
                model_config = config.get_model_config()
                print(f"🤖 Using provider: {model_config['provider']}")
                print(f"📋 Model: {model_config['model']}")
            else:
                print("❌ Configuration validation failed!")
                return 1
            return 0
        
        # Print banner
        print_banner()
        
        # Determine query from arguments or command line
        query = args.query or args.query_flag
        
        # If no query provided, try legacy sys.argv approach
        if not query and len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            query = sys.argv[1]
        
        # Default query if none provided
        if not query:
            print("⚠️  No query provided, using default AI competitors analysis")
            query = "top AI companies and competitors 2024"
        
        # Log startup information
        logger.info(f"Starting competitor research for query: '{query}'")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        
        # Validate configuration
        print("🔧 Validating configuration...")
        if not validate_configuration():
            print("❌ Configuration validation failed. Please check your API keys.")
            return 1
        print("✅ Configuration validated successfully")
        
        # Start the workflow
        print(f"🚀 Starting analysis for: '{query}'")
        print("📊 This may take 2-5 minutes depending on query complexity...")
        
        # Execute workflow
        result = create_workflow(query)
        
        # Format and display results
        format_result_output(result)
        
        # Return appropriate exit code
        if isinstance(result, dict) and result.get("success"):
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        logger.info("Analysis interrupted by user (Ctrl+C)")
        return 130  # Standard exit code for Ctrl+C
        
    except Exception as e:
        error_msg = f"Fatal error in main application: {str(e)}"
        print(f"\n💥 {error_msg}")
        logger.error(error_msg, exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)