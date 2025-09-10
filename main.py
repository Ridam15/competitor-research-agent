#!/usr/bin/env python3
"""
🏆 10/10 Professional Competitor Research Agent

World-class AI-powered competitive intelligence system with:
• Multi-agent architecture with specialized expertise
• Real-time financial data integration  
• Advanced market intelligence
• Interactive visualizations
• Executive-grade reporting

Usage:
    python main.py "your competitor research query"
    python main.py --enhanced "competitors to Tesla"
    
Examples:
    python main.py "competitors to OpenAI"
    python main.py "top fintech companies 2024"  
    python main.py --enhanced "Tesla competitors analysis"
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Import both standard and enhanced workflows
from src.workflows.competitor_research import create_workflow
from src.workflows.enhanced_competitor_research import enhanced_agent_system
from src.utils.logger import logger
from src.utils.config import validate_configuration, config

def print_banner():
    """Print enhanced application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║          🏆 10/10 COMPETITOR RESEARCH AGENT 🏆              ║
    ║                                                              ║
    ║     🤖 Multi-Agent Intelligence | 💰 Real-time Finance      ║
    ║     📊 Advanced Analytics | 📈 Interactive Visualizations   ║
    ║     🎯 Executive-Grade Reports | ⚡ Enhanced Performance    ║
    ║                                                              ║
    ║                     v3.0.0 Professional                     ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_usage_examples():
    """Print enhanced usage examples"""
    examples = """
    � 10/10 Professional Analysis Examples:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Standard Analysis:
    • python main.py "competitors to OpenAI"
    • python main.py "top fintech companies 2024"  
    • python main.py "cloud infrastructure providers"
    
    🏆 Enhanced Professional Analysis (10/10 Features):
    • python main.py --enhanced "Tesla competitors analysis"
    • python main.py --enhanced "AI companies competitive landscape"
    • python main.py --enhanced "fintech market intelligence"
    • python main.py --enhanced "SaaS platforms comparison 2024"
    
    📊 Advanced Features Available:
    • Real-time financial data integration
    • Interactive visualization dashboards  
    • Executive-grade strategic analysis
    • Multi-agent specialized intelligence
    • Professional PDF reports with charts
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    print(examples)

def format_enhanced_result_output(result):
    """Format enhanced analysis results with detailed metrics"""
    if isinstance(result, dict):
        print(f"\n🏆 10/10 PROFESSIONAL ANALYSIS COMPLETED")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📊 Query: {result.get('query', 'N/A')}")
        print(f"🎯 Analysis Type: {result.get('analysis_type', 'Enhanced Multi-Agent')}")
        print(f"⏱️  Completed: {result.get('timestamp', 'N/A')}")
        print(f"🤖 Agents Deployed: {result.get('agents_deployed', 'N/A')}")
        print(f"✅ Tasks Completed: {result.get('tasks_completed', 'N/A')}")
        print(f"🎯 Confidence Level: {result.get('confidence_level', 'High')}")
        print(f"📈 Analysis Depth: {result.get('analysis_depth', 'Professional')}")
        
        if result.get('data_sources'):
            print(f"📡 Data Sources:")
            for source in result['data_sources']:
                print(f"    • {source}")
        
        if result.get('suitable_for'):
            print(f"🎯 Suitable For:")
            for use_case in result['suitable_for']:
                print(f"    • {use_case}")
                
        # Show executive report snippet
        executive_report = result.get('executive_report', '')
        if executive_report:
            print(f"\n📝 Executive Report Generated:")
            print(f"   Length: {len(executive_report):,} characters")
            print(f"   Preview: {executive_report[:200]}...")
            
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
    else:
        print(f"\n📝 Analysis Result: {result}")

def format_result_output(result):
    """Format standard analysis results"""
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
    """Setup enhanced command line argument parser"""
    parser = argparse.ArgumentParser(
        description="🏆 10/10 Professional AI-Powered Competitor Research Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 Examples:
  %(prog)s "competitors to Tesla"
  %(prog)s --enhanced "Tesla competitive landscape analysis"
  %(prog)s --query "fintech startups" --output custom_report.pdf
  %(prog)s --enhanced "AI market intelligence 2024"
        """
    )
    
    parser.add_argument(
        'query', 
        nargs='?',
        default=None,
        help='Competitor research query (e.g., "competitors to OpenAI")'
    )
    
    parser.add_argument(
        '--enhanced', '-e',
        action='store_true',
        help='🏆 Use 10/10 enhanced analysis with multi-agent intelligence, real-time data, and advanced visualizations'
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
    
    parser.add_argument(
        '--features',
        action='store_true',
        help='Show 10/10 enhanced features and exit'
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