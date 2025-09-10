"""
Enhanced CLI Interface with Rich formatting and advanced features

This module provides a beautiful, interactive command-line interface for the
Competitor Research Agent with progress tracking, real-time updates, and
comprehensive reporting.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import time
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TaskID
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.tree import Tree
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich import box
from rich.align import Align

from src.workflows.competitor_research import create_workflow
from src.utils.config import validate_configuration, config
from src.utils.logger import logger
from src.utils.monitoring import error_monitor, health_checker
from src.utils.performance import performance_monitor, intelligent_cache


console = Console()


@dataclass
class CLIConfig:
    """CLI configuration settings"""
    verbose: bool = False
    interactive: bool = False
    output_format: str = "pdf"
    theme: str = "professional"
    auto_open: bool = False
    save_history: bool = True
    show_progress: bool = True


class EnhancedCLI:
    """Enhanced CLI with rich interface and advanced features"""
    
    def __init__(self):
        from pathlib import Path
        
        self.config = CLIConfig()
        self.console = Console()
        self.history_file = Path("cli_history.json")
        self.load_history()
        
        # Initialize enhanced features
        from run_tests import TestRunner
        project_root = Path(__file__).parent.parent.parent
        self.test_runner = TestRunner(project_root)
        self.performance_monitor = performance_monitor
        self.error_monitor = error_monitor
        
        # Initialize themes
        self.themes = {
            "default": {"primary": "cyan", "secondary": "blue", "accent": "green"},
            "dark": {"primary": "bright_white", "secondary": "white", "accent": "yellow"},
            "professional": {"primary": "blue", "secondary": "bright_blue", "accent": "green"},
            "hacker": {"primary": "bright_green", "secondary": "green", "accent": "bright_cyan"},
        }
        self.current_theme = "default"
    
    def load_history(self):
        """Load CLI usage history"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            else:
                self.history = {"queries": [], "settings": {}}
        except Exception as e:
            logger.warning(f"Failed to load CLI history: {e}")
            self.history = {"queries": [], "settings": {}}
    
    def save_history(self):
        """Save CLI usage history"""
        try:
            if self.config.save_history:
                with open(self.history_file, 'w') as f:
                    json.dump(self.history, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save CLI history: {e}")
    
    def show_banner(self):
        """Display application banner"""
        banner_text = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║              🤖 COMPETITOR RESEARCH AGENT v2.0                  ║
    ║                                                                  ║
    ║           AI-Powered Market Intelligence & Analysis              ║
    ║                    Enhanced Professional Edition                 ║
    ╚══════════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(Panel(
            banner_text.strip(),
            style="bold blue",
            box=box.DOUBLE
        ))
    
    def show_system_status(self) -> bool:
        """Display system status and health checks"""
        with self.console.status("[bold blue]Checking system status..."):
            health_results = health_checker.run_health_checks()
            config_valid = validate_configuration()
        
        # Create status table
        status_table = Table(title="System Status", box=box.ROUNDED)
        status_table.add_column("Component", style="cyan", no_wrap=True)
        status_table.add_column("Status", justify="center")
        status_table.add_column("Details", style="dim")
        
        # Configuration status
        config_status = "✅ Valid" if config_valid else "❌ Invalid"
        config_details = "All API keys configured" if config_valid else "Missing API keys"
        status_table.add_row("Configuration", config_status, config_details)
        
        # Health check results
        for check_name, check_result in health_results.get("checks", {}).items():
            status = "✅ Healthy" if check_result["healthy"] else "❌ Unhealthy"
            details = f"{check_result.get('duration_ms', 0):.1f}ms"
            if not check_result["healthy"] and "error" in check_result:
                details += f" - {check_result['error']}"
            status_table.add_row(check_name.replace("_", " ").title(), status, details)
        
        self.console.print(status_table)
        
        # Show performance summary if available
        perf_summary = performance_monitor.get_performance_summary(hours=1)
        if perf_summary.get("total_function_calls", 0) > 0:
            self.console.print(f"\\n📊 Recent Performance: {perf_summary['total_function_calls']} operations, "
                             f"{perf_summary['success_rate']:.1f}% success rate")
        
        return config_valid and health_results.get("overall_status") == "healthy"
    
    def show_examples(self):
        """Show usage examples with rich formatting"""
        examples = [
            {
                "category": "🏢 Company Analysis",
                "examples": [
                    ("competitors to Tesla", "Analyze Tesla's competitive landscape"),
                    ("alternatives to Slack", "Find Slack alternatives and competitors"),
                    ("OpenAI competitors", "Research AI/ML companies competing with OpenAI")
                ]
            },
            {
                "category": "🏭 Industry Research", 
                "examples": [
                    ("top fintech companies 2024", "Analyze leading fintech companies"),
                    ("cloud infrastructure providers", "Research cloud service providers"),
                    ("project management tools comparison", "Compare PM tools and platforms")
                ]
            },
            {
                "category": "🎯 Market Segments",
                "examples": [
                    ("AI image generation tools", "Analyze AI image generation market"),
                    ("European SaaS companies", "Research European SaaS landscape"),
                    ("cybersecurity startups", "Find emerging cybersecurity companies")
                ]
            }
        ]
        
        for category in examples:
            panel_content = "\\n".join([
                f"• [bold cyan]{example}[/bold cyan]\\n  [dim]{description}[/dim]"
                for example, description in category["examples"]
            ])
            
            self.console.print(Panel(
                panel_content,
                title=category["category"],
                border_style="green",
                padding=(1, 2)
            ))
    
    def show_recent_history(self, limit: int = 5):
        """Show recent query history"""
        recent_queries = self.history.get("queries", [])[-limit:]
        if not recent_queries:
            self.console.print("[yellow]No recent queries found[/yellow]")
            return
        
        history_table = Table(title=f"Recent Queries (Last {len(recent_queries)})", box=box.SIMPLE)
        history_table.add_column("#", style="dim", width=3)
        history_table.add_column("Query", style="cyan")
        history_table.add_column("Date", style="green", justify="right")
        history_table.add_column("Status", justify="center")
        
        for i, query_info in enumerate(recent_queries, 1):
            status_icon = "✅" if query_info.get("success", False) else "❌"
            history_table.add_row(
                str(i),
                query_info.get("query", "Unknown"),
                query_info.get("date", "Unknown")[:16],
                status_icon
            )
        
        self.console.print(history_table)
    
    def interactive_mode(self):
        """Interactive mode with menu-driven interface"""
        while True:
            self.console.clear()
            self.show_banner()
            
            menu_options = [
                ("1", "🔍 New Analysis", "Start a new competitor analysis"),
                ("2", "📊 System Status", "Check system health and performance"),
                ("3", "📈 Performance Report", "View detailed performance metrics"),
                ("4", "🧪 Test Management", "Run and manage test suites"),
                ("5", "🗂️ Cache Management", "Manage intelligent cache"),
                ("6", "📝 Recent History", "View recent query history"),
                ("7", "💡 Examples", "Show usage examples"),
                ("8", "⚙️ Settings", "Configure CLI settings"),
                ("9", "❌ Exit", "Exit the application")
            ]
            
            menu_table = Table(title="Main Menu", box=box.ROUNDED, show_header=False)
            menu_table.add_column("Option", style="bold cyan", width=8)
            menu_table.add_column("Description", style="white")
            menu_table.add_column("Details", style="dim")
            
            for option, title, description in menu_options:
                menu_table.add_row(f"[{option}]", title, description)
            
            self.console.print(menu_table)
            
            choice = Prompt.ask("\\nSelect an option", choices=[opt[0] for opt in menu_options])
            
            if choice == "1":
                self.interactive_analysis()
            elif choice == "2":
                self.show_system_status()
                Prompt.ask("\\nPress Enter to continue")
            elif choice == "3":
                self.show_performance_report()
                Prompt.ask("\\nPress Enter to continue")
            elif choice == "4":
                self.test_management_menu()
            elif choice == "5":
                self.cache_management()
            elif choice == "6":
                self.show_recent_history(10)
                Prompt.ask("\\nPress Enter to continue")
            elif choice == "7":
                self.show_examples()
                Prompt.ask("\\nPress Enter to continue")
            elif choice == "8":
                self.settings_menu()
            elif choice == "9":
                self.console.print("[green]Thank you for using Competitor Research Agent![/green]")
                break
    
    def interactive_analysis(self):
        """Interactive analysis with guided input"""
        self.console.print("\\n[bold blue]🔍 New Competitor Analysis[/bold blue]\\n")
        
        # Get query with suggestions
        suggested_queries = [
            "competitors to Tesla",
            "top fintech companies 2024", 
            "AI image generation tools",
            "project management software comparison"
        ]
        
        self.console.print("[dim]Suggested queries:[/dim]")
        for i, suggestion in enumerate(suggested_queries, 1):
            self.console.print(f"  {i}. {suggestion}")
        
        query = Prompt.ask("\\nEnter your analysis query (or number for suggestion)")
        
        # Handle numeric selection
        if query.isdigit() and 1 <= int(query) <= len(suggested_queries):
            query = suggested_queries[int(query) - 1]
            self.console.print(f"Selected: [cyan]{query}[/cyan]")
        
        # Confirm analysis
        if not Confirm.ask(f"\\nProceed with analysis: '{query}'?", default=True):
            return
        
        # Execute analysis with progress tracking
        self.execute_analysis_with_progress(query)
    
    def execute_analysis_with_progress(self, query: str):
        """Execute analysis with rich progress tracking"""
        start_time = time.time()
        
        # Add to history
        self.history["queries"].append({
            "query": query,
            "date": datetime.now().isoformat(),
            "success": False
        })
        
        # Progress tracking setup
        task_descriptions = [
            ("Initializing analysis", 0.1),
            ("Searching for competitors", 0.3), 
            ("Analyzing market data", 0.6),
            ("Generating insights", 0.8),
            ("Creating PDF report", 1.0)
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            # Create main progress task
            main_task = progress.add_task("Competitor Analysis", total=1.0)
            
            try:
                # Simulate progress updates (in real implementation, this would be integrated with the workflow)
                for description, target_progress in task_descriptions:
                    progress.update(main_task, description=description)
                    
                    # Simulate work (replace with actual workflow integration)
                    if target_progress == 1.0:
                        # Execute the actual analysis
                        result = create_workflow(query)
                        progress.update(main_task, advance=target_progress - progress.tasks[main_task].completed)
                    else:
                        # Simulate intermediate progress
                        while progress.tasks[main_task].completed < target_progress:
                            time.sleep(0.1)
                            progress.update(main_task, advance=0.01)
                
                # Analysis completed
                execution_time = time.time() - start_time
                
                # Update history with success
                self.history["queries"][-1]["success"] = True
                self.history["queries"][-1]["execution_time"] = execution_time
                self.save_history()
                
                # Show results
                self.show_analysis_results(query, result, execution_time)
                
            except Exception as e:
                progress.update(main_task, description="❌ Analysis failed")
                self.console.print(f"\\n[red]Analysis failed: {str(e)}[/red]")
                logger.error(f"Analysis failed: {e}")
    
    def show_analysis_results(self, query: str, result: Dict[str, Any], execution_time: float):
        """Show analysis results with rich formatting"""
        self.console.print("\\n" + "="*60)
        self.console.print(f"[bold green]✅ Analysis Complete![/bold green]")
        self.console.print("="*60)
        
        # Results summary
        results_table = Table(box=box.SIMPLE_HEAD)
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")
        
        results_table.add_row("Query", query)
        results_table.add_row("Execution Time", f"{execution_time:.2f} seconds")
        results_table.add_row("Status", "✅ Success" if result.get("success") else "❌ Failed")
        
        if result.get("success"):
            # Extract report path from result
            report_path = "Unknown"
            if hasattr(result.get("result"), "raw"):
                report_path = str(result.get("result").raw)
            
            results_table.add_row("Report Generated", report_path)
            results_table.add_row("Attempts", str(result.get("attempts", 1)))
        
        self.console.print(results_table)
        
        # Show recommendations
        if result.get("success"):
            self.console.print("\\n[bold blue]📄 Report Details:[/bold blue]")
            self.console.print(f"• Professional PDF report generated")
            self.console.print(f"• Comprehensive competitor analysis")
            self.console.print(f"• Strategic recommendations included")
            self.console.print(f"• Executive summary provided")
            
            if self.config.auto_open:
                if Confirm.ask("\\nOpen the generated report?", default=True):
                    import subprocess
                    subprocess.run(["open", report_path])
        else:
            self.console.print(f"\\n[red]❌ Error: {result.get('message', 'Unknown error')}[/red]")
            
            # Show error-specific suggestions
            error_type = result.get("error_type")
            if error_type == "rate_limit":
                self.console.print("[yellow]💡 Try again in a few minutes or upgrade your API plan[/yellow]")
            elif error_type == "authentication":
                self.console.print("[yellow]💡 Check your API keys in the .env file[/yellow]")
    
    def show_performance_report(self):
        """Show detailed performance report"""
        self.console.print("\\n[bold blue]📈 Performance Report[/bold blue]\\n")
        
        # Performance metrics
        perf_summary = performance_monitor.get_performance_summary(hours=24)
        
        if perf_summary.get("total_function_calls", 0) == 0:
            self.console.print("[yellow]No performance data available[/yellow]")
            return
        
        # Performance overview table
        perf_table = Table(title="24-Hour Performance Overview", box=box.ROUNDED)
        perf_table.add_column("Metric", style="cyan")
        perf_table.add_column("Value", style="green", justify="right")
        
        perf_table.add_row("Total Operations", str(perf_summary.get("total_function_calls", 0)))
        perf_table.add_row("Success Rate", f"{perf_summary.get('success_rate', 0):.1f}%")
        perf_table.add_row("Total Execution Time", f"{perf_summary.get('total_execution_time_seconds', 0):.2f}s")
        perf_table.add_row("Average Execution Time", f"{perf_summary.get('average_execution_time_seconds', 0):.2f}s")
        perf_table.add_row("Cache Hit Rate", f"{perf_summary.get('cache_hit_rate', 0):.1f}%")
        perf_table.add_row("Memory Delta", f"{perf_summary.get('average_memory_delta_mb', 0):.2f}MB")
        
        self.console.print(perf_table)
        
        # Cache statistics
        cache_stats = intelligent_cache.get_stats()
        cache_table = Table(title="Cache Statistics", box=box.ROUNDED)
        cache_table.add_column("Metric", style="cyan")
        cache_table.add_column("Value", style="green", justify="right")
        
        for key, value in cache_stats.items():
            if key != 'error':
                display_key = key.replace('_', ' ').title()
                cache_table.add_row(display_key, str(value))
        
        self.console.print("\\n")
        self.console.print(cache_table)
        
        # Error summary
        error_summary = error_monitor.get_error_summary(hours=24)
        if error_summary.get("total_errors", 0) > 0:
            self.console.print("\\n[bold red]⚠️ Error Summary (Last 24h)[/bold red]")
            error_table = Table(box=box.SIMPLE)
            error_table.add_column("Severity", style="red")
            error_table.add_column("Count", justify="right")
            
            for severity, count in error_summary.get("by_severity", {}).items():
                error_table.add_row(severity.title(), str(count))
            
            self.console.print(error_table)
    
    def cache_management(self):
        """Cache management interface"""
        while True:
            self.console.print("\\n[bold blue]🗂️ Cache Management[/bold blue]\\n")
            
            # Show cache stats
            stats = intelligent_cache.get_stats()
            stats_table = Table(title="Current Cache Statistics", box=box.SIMPLE)
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green", justify="right")
            
            for key, value in stats.items():
                if key != 'error':
                    display_key = key.replace('_', ' ').title()
                    stats_table.add_row(display_key, str(value))
            
            self.console.print(stats_table)
            
            # Cache management options
            cache_options = [
                ("1", "Clear All Cache", "Remove all cached data"),
                ("2", "Clear Search Cache", "Clear search-related cache only"),
                ("3", "Clear Old Entries", "Remove expired cache entries"),
                ("4", "Back to Main Menu", "Return to main menu")
            ]
            
            option_table = Table(box=box.SIMPLE, show_header=False)
            option_table.add_column("Option", style="bold cyan", width=8)
            option_table.add_column("Action", style="white")
            option_table.add_column("Description", style="dim")
            
            for option, title, description in cache_options:
                option_table.add_row(f"[{option}]", title, description)
            
            self.console.print("\\n")
            self.console.print(option_table)
            
            choice = Prompt.ask("\\nSelect an option", choices=[opt[0] for opt in cache_options])
            
            if choice == "1":
                if Confirm.ask("Clear all cache data?", default=False):
                    intelligent_cache.clear()
                    self.console.print("[green]✅ Cache cleared successfully[/green]")
            elif choice == "2":
                intelligent_cache.clear(pattern="search")
                self.console.print("[green]✅ Search cache cleared[/green]")
            elif choice == "3":
                # This would require additional implementation in the cache system
                self.console.print("[yellow]Feature coming soon[/yellow]")
            elif choice == "4":
                break
            
            if choice != "4":
                Prompt.ask("\\nPress Enter to continue")
    
    def settings_menu(self):
        """Settings configuration menu"""
        while True:
            self.console.print("\\n[bold blue]⚙️ CLI Settings[/bold blue]\\n")
            
            settings_table = Table(title="Current Settings", box=box.ROUNDED)
            settings_table.add_column("Setting", style="cyan")
            settings_table.add_column("Value", style="green", justify="center")
            settings_table.add_column("Description", style="dim")
            
            settings_table.add_row("Verbose Output", "✅" if self.config.verbose else "❌", "Show detailed output")
            settings_table.add_row("Auto-open Reports", "✅" if self.config.auto_open else "❌", "Open reports automatically")
            settings_table.add_row("Save History", "✅" if self.config.save_history else "❌", "Save query history")
            settings_table.add_row("Show Progress", "✅" if self.config.show_progress else "❌", "Show progress bars")
            settings_table.add_row("Output Format", self.config.output_format, "Default output format")
            settings_table.add_row("Theme", self.config.theme, "Report theme")
            
            self.console.print(settings_table)
            
            setting_options = [
                ("1", "Toggle Verbose Output"),
                ("2", "Toggle Auto-open Reports"),
                ("3", "Toggle Save History"),
                ("4", "Toggle Show Progress"),
                ("5", "Change Output Format"),
                ("6", "Change Theme"),
                ("7", "Back to Main Menu")
            ]
            
            for i, (num, desc) in enumerate(setting_options):
                self.console.print(f"[cyan]{num}[/cyan]. {desc}")
            
            choice = Prompt.ask("\\nSelect setting to modify", choices=[opt[0] for opt in setting_options])
            
            if choice == "1":
                self.config.verbose = not self.config.verbose
            elif choice == "2":
                self.config.auto_open = not self.config.auto_open
            elif choice == "3":
                self.config.save_history = not self.config.save_history
            elif choice == "4":
                self.config.show_progress = not self.config.show_progress
            elif choice == "5":
                format_choice = Prompt.ask("Output format", choices=["pdf", "json", "markdown", "html"], default="pdf")
                self.config.output_format = format_choice
            elif choice == "6":
                theme_choice = Prompt.ask("Report theme", choices=["professional", "modern", "minimal", "corporate"], default="professional")
                self.config.theme = theme_choice
            elif choice == "7":
                break
    
    def run_single_analysis(self, query: str, output_file: Optional[str] = None, verbose: bool = False):
        """Run a single analysis from command line"""
        self.config.verbose = verbose
        
        if verbose:
            self.show_banner()
            self.console.print(f"\\n[bold cyan]Query:[/bold cyan] {query}")
            
            # Show system status if verbose
            if not self.show_system_status():
                self.console.print("[red]System checks failed. Proceeding anyway...[/red]")
        
        # Execute analysis
        if self.config.show_progress:
            self.execute_analysis_with_progress(query)
        else:
            # Simple execution without progress bars
            self.console.print(f"Analyzing: {query}")
            result = create_workflow(query)
            execution_time = 0  # Would need to be tracked
            self.show_analysis_results(query, result, execution_time)

    def test_management_menu(self):
        """Interactive test management interface"""
        while True:
            self.console.clear()
            self.console.print("[bold cyan]🧪 Test Management Suite[/bold cyan]\n")
            
            test_options = [
                ("1", "Quick Tests", "Run essential unit tests"),
                ("2", "Full Test Suite", "Run comprehensive test suite"),
                ("3", "Unit Tests", "Run unit tests only"),
                ("4", "Integration Tests", "Run integration tests"),
                ("5", "Performance Tests", "Run performance benchmarks"),
                ("6", "Security Tests", "Run security validation tests"),
                ("7", "Test Reports", "View recent test reports"),
                ("8", "Back to Main Menu", "Return to main menu"),
            ]
            
            test_table = Table(title="Test Management Options", box=box.ROUNDED, show_header=False)
            test_table.add_column("Option", style="bold cyan", width=8)
            test_table.add_column("Description", style="white")
            test_table.add_column("Details", style="dim")
            
            for option, title, description in test_options:
                test_table.add_row(f"[{option}]", title, description)
            
            self.console.print(test_table)
            
            choice = Prompt.ask("\nSelect test option", choices=[opt[0] for opt in test_options])
            
            if choice == "8":
                break
            elif choice == "1":
                self.run_test_suite("quick")
            elif choice == "2":
                self.run_test_suite("full")
            elif choice == "3":
                self.run_test_suite("unit")
            elif choice == "4":
                self.run_test_suite("integration")
            elif choice == "5":
                self.run_test_suite("performance")
            elif choice == "6":
                self.run_test_suite("security")
            elif choice == "7":
                self.show_test_reports()
            
            if choice != "8":
                input("\nPress Enter to continue...")
    
    def run_test_suite(self, category: str):
        """Run test suite with progress tracking"""
        self.console.print(f"\n[bold blue]Running {category} tests...[/bold blue]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Executing {category} tests...", total=None)
            
            try:
                # Run tests using the test runner
                if category == "quick":
                    result = self.test_runner.run_tests_by_category("unit", verbose=False, fail_fast=True)
                else:
                    result = self.test_runner.run_tests_by_category(category, verbose=True)
                
                progress.update(task, completed=True)
                
                # Display results
                self.show_test_results(result, category)
                
            except Exception as e:
                progress.update(task, completed=True)
                self.console.print(f"[red]❌ Test execution failed: {e}[/red]")
    
    def show_test_results(self, result: Dict, category: str):
        """Display formatted test results"""
        stats = result.get("stats", {})
        
        # Overall status
        status = "✅ PASSED" if result.get("success") else "❌ FAILED"
        status_color = "green" if result.get("success") else "red"
        
        self.console.print(f"\n[bold {status_color}]{status}[/bold {status_color}]")
        
        # Test statistics table
        stats_table = Table(title=f"{category.title()} Test Results", box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Count", style="green", justify="right")
        stats_table.add_column("Status", justify="center")
        
        total = stats.get("total", 0)
        passed = stats.get("passed", 0)
        failed = stats.get("failed", 0)
        skipped = stats.get("skipped", 0)
        
        stats_table.add_row("Total Tests", str(total), "📊")
        stats_table.add_row("Passed", str(passed), "✅" if passed == total and total > 0 else "")
        stats_table.add_row("Failed", str(failed), "❌" if failed > 0 else "")
        stats_table.add_row("Skipped", str(skipped), "⏭️" if skipped > 0 else "")
        
        if total > 0:
            success_rate = (passed / total) * 100
            stats_table.add_row("Success Rate", f"{success_rate:.1f}%", "📈")
        
        execution_time = result.get("execution_time", 0)
        stats_table.add_row("Execution Time", f"{execution_time:.2f}s", "⏱️")
        
        self.console.print(stats_table)


# Global CLI instance
enhanced_cli = EnhancedCLI()


def create_cli_parser():
    """Create enhanced argument parser with rich help"""
    parser = argparse.ArgumentParser(
        description="🤖 Competitor Research Agent - AI-Powered Market Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "competitors to Tesla"                    # Basic analysis
  %(prog)s "fintech companies" --verbose            # Verbose output
  %(prog)s --interactive                            # Interactive mode
  %(prog)s --status                                 # System status check
  %(prog)s --performance                            # Performance report
  %(prog)s --examples                               # Show examples
        """
    )
    
    # Main arguments
    parser.add_argument('query', nargs='?', help='Competitor research query')
    
    # Operation modes
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Launch interactive mode with menu interface')
    parser.add_argument('--status', action='store_true',
                       help='Show system status and health checks')
    parser.add_argument('--performance', action='store_true',
                       help='Show performance metrics and statistics')
    parser.add_argument('--examples', action='store_true',
                       help='Show usage examples and exit')
    
    # Output options
    parser.add_argument('--output', '-o', type=str,
                       help='Custom output filename for the report')
    parser.add_argument('--format', choices=['pdf', 'json', 'markdown', 'html'],
                       default='pdf', help='Output format (default: pdf)')
    parser.add_argument('--theme', choices=['professional', 'modern', 'minimal', 'corporate'],
                       default='professional', help='Report theme (default: professional)')
    
    # Behavior options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output with detailed progress')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress non-essential output')
    parser.add_argument('--no-progress', action='store_true',
                       help='Disable progress bars and animations')
    parser.add_argument('--auto-open', action='store_true',
                       help='Automatically open generated reports')
    
    # Configuration options
    parser.add_argument('--config-check', action='store_true',
                       help='Check configuration and exit')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear all cached data before running')
    
    # History and management
    parser.add_argument('--history', type=int, metavar='N',
                       help='Show last N queries from history')
    parser.add_argument('--export-errors', type=str, metavar='FILE',
                       help='Export error report to specified file')
    
    return parser


def main():
    """Enhanced main function with rich CLI interface"""
    try:
        parser = create_cli_parser()
        args = parser.parse_args()
        
        # Configure CLI based on arguments
        enhanced_cli.config.verbose = args.verbose
        enhanced_cli.config.output_format = args.format
        enhanced_cli.config.theme = args.theme
        enhanced_cli.config.auto_open = args.auto_open
        enhanced_cli.config.show_progress = not args.no_progress
        
        # Handle special operations first
        if args.interactive:
            enhanced_cli.interactive_mode()
            return 0
        
        if args.examples:
            enhanced_cli.show_banner()
            enhanced_cli.show_examples()
            return 0
        
        if args.status:
            enhanced_cli.show_banner()
            is_healthy = enhanced_cli.show_system_status()
            return 0 if is_healthy else 1
        
        if args.performance:
            enhanced_cli.show_banner()
            enhanced_cli.show_performance_report()
            return 0
        
        if args.config_check:
            enhanced_cli.show_banner()
            is_valid = validate_configuration()
            if is_valid:
                console.print("[green]✅ Configuration is valid![/green]")
                model_config = config.get_model_config()
                console.print(f"🤖 Provider: {model_config['provider']}")
                console.print(f"📋 Model: {model_config['model']}")
            else:
                console.print("[red]❌ Configuration validation failed![/red]")
                console.print("Please check your API keys in the .env file")
            return 0 if is_valid else 1
        
        if args.clear_cache:
            intelligent_cache.clear()
            console.print("[green]✅ Cache cleared successfully[/green]")
        
        if args.history:
            enhanced_cli.show_recent_history(args.history)
            return 0
        
        if args.export_errors:
            error_monitor.export_error_report(args.export_errors)
            console.print(f"[green]✅ Error report exported to {args.export_errors}[/green]")
            return 0
        
        # Main analysis execution
        if not args.query:
            if not args.quiet:
                enhanced_cli.show_banner()
                console.print("[yellow]⚠️ No query provided. Use --interactive for guided mode or --examples for help.[/yellow]")
            return 1
        
        # Execute single analysis
        enhanced_cli.run_single_analysis(
            query=args.query,
            output_file=args.output,
            verbose=args.verbose
        )
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\\n[yellow]⚠️ Analysis interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\\n[red]💥 Fatal error: {str(e)}[/red]")
        if enhanced_cli.config.verbose:
            console.print_exception()
        return 1
    finally:
        enhanced_cli.save_history()


if __name__ == "__main__":
    sys.exit(main())
