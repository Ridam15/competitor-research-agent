#!/usr/bin/env python3
"""
Comprehensive Test Runner for Competitor Research Agent

Advanced test execution with reporting, performance analysis, and CI/CD integration.
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union
import argparse

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logger import logger
from src.utils.config import validate_configuration


class TestRunner:
    """Advanced test runner with comprehensive reporting"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests"
        self.reports_dir = project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Test categories and their configurations
        self.test_categories = {
            "unit": {
                "description": "Unit tests for individual components",
                "markers": "unit",
                "timeout": 60,
                "parallel": True
            },
            "integration": {
                "description": "Integration tests for component interaction",
                "markers": "integration",
                "timeout": 300,
                "parallel": False
            },
            "performance": {
                "description": "Performance and scalability tests",
                "markers": "performance",
                "timeout": 600,
                "parallel": False
            },
            "security": {
                "description": "Security and vulnerability tests",
                "markers": "security", 
                "timeout": 120,
                "parallel": True
            },
            "e2e": {
                "description": "End-to-end workflow tests",
                "markers": "e2e",
                "timeout": 900,
                "parallel": False
            }
        }
    
    def run_test_suite(self, 
                      category: Optional[str] = None,
                      specific_tests: Optional[List[str]] = None,
                      coverage: bool = True,
                      verbose: bool = True,
                      parallel: bool = False,
                      fail_fast: bool = False) -> Dict:
        """
        Run comprehensive test suite with advanced options
        
        Args:
            category: Test category to run (unit, integration, etc.)
            specific_tests: List of specific test files to run
            coverage: Enable coverage reporting
            verbose: Enable verbose output
            parallel: Run tests in parallel where possible
            fail_fast: Stop on first failure
        
        Returns:
            Dictionary with test results and metrics
        """
        
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info("🧪 Starting Competitor Research Agent Test Suite")
        logger.info(f"Timestamp: {timestamp}")
        
        # Validate environment
        env_valid = self._validate_test_environment()
        if not env_valid:
            return {"success": False, "error": "Test environment validation failed"}
        
        # Build pytest command
        pytest_cmd = self._build_pytest_command(
            category=category,
            specific_tests=specific_tests,
            coverage=coverage,
            verbose=verbose,
            parallel=parallel,
            fail_fast=fail_fast,
            timestamp=timestamp
        )
        
        # Run tests
        logger.info(f"Executing: {' '.join(pytest_cmd)}")
        
        try:
            result = subprocess.run(
                pytest_cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=self._get_timeout(category)
            )
            
            execution_time = time.time() - start_time
            
            # Process results
            test_results = self._process_test_results(
                result=result,
                execution_time=execution_time,
                timestamp=timestamp,
                category=category
            )
            
            # Generate reports
            self._generate_reports(test_results, timestamp)
            
            # Log summary
            self._log_test_summary(test_results)
            
            return test_results
            
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Tests timed out after {self._get_timeout(category)} seconds")
            return {
                "success": False,
                "error": "Test execution timeout",
                "timeout": self._get_timeout(category)
            }
        
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_test_environment(self) -> bool:
        """Validate test environment and dependencies"""
        
        logger.info("🔍 Validating test environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            logger.error(f"❌ Python 3.8+ required, found {python_version}")
            return False
        
        # Check pytest installation
        try:
            import pytest
            logger.info(f"✅ pytest version: {pytest.__version__}")
        except ImportError:
            logger.error("❌ pytest not installed")
            return False
        
        # Check test directory
        if not self.test_dir.exists():
            logger.error(f"❌ Test directory not found: {self.test_dir}")
            return False
        
        # Check for test files
        test_files = list(self.test_dir.glob("test_*.py"))
        if not test_files:
            logger.error("❌ No test files found")
            return False
        
        logger.info(f"✅ Found {len(test_files)} test files")
        
        # Check configuration
        config_valid = validate_configuration()
        if config_valid:
            logger.info("✅ Configuration valid - API tests will run")
        else:
            logger.warning("⚠️  Configuration incomplete - API tests will be skipped")
        
        logger.info("✅ Test environment validation complete")
        return True
    
    def _build_pytest_command(self,
                             category: Optional[str],
                             specific_tests: Optional[List[str]],
                             coverage: bool,
                             verbose: bool,
                             parallel: bool,
                             fail_fast: bool,
                             timestamp: str) -> List[str]:
        """Build pytest command with all options"""
        
        cmd = ["python", "-m", "pytest"]
        
        # Test selection
        if specific_tests:
            cmd.extend(specific_tests)
        elif category:
            cmd.extend(["-m", self.test_categories[category]["markers"]])
        else:
            cmd.append("tests/")
        
        # Output options
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Failure handling
        if fail_fast:
            cmd.append("-x")
        
        # Parallel execution
        if parallel and category != "integration":  # Integration tests shouldn't run in parallel
            try:
                import pytest_xdist
                cmd.extend(["-n", "auto"])
            except ImportError:
                logger.warning("⚠️  pytest-xdist not available, running sequentially")
        
        # Coverage options
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html",
                f"--cov-report=html:test_reports/coverage_{timestamp}",
                "--cov-report=term-missing",
                "--cov-report=json",
                f"--cov-report=json:test_reports/coverage_{timestamp}.json"
            ])
        
        # Output options
        cmd.extend([
            "--tb=short",
            "--color=yes",
            "--durations=10",
            f"--junitxml=test_reports/junit_{timestamp}.xml",
            f"--html=test_reports/report_{timestamp}.html",
            "--self-contained-html"
        ])
        
        return cmd
    
    def _get_timeout(self, category: Optional[str]) -> int:
        """Get timeout for test category"""
        if category and category in self.test_categories:
            return self.test_categories[category]["timeout"]
        return 300  # Default 5 minutes
    
    def _process_test_results(self,
                            result: subprocess.CompletedProcess,
                            execution_time: float,
                            timestamp: str,
                            category: Optional[str]) -> Dict:
        """Process and analyze test results"""
        
        # Parse pytest output
        output_lines = result.stdout.split('\n')
        
        # Extract test statistics
        stats = self._extract_test_stats(output_lines)
        
        # Extract coverage information
        coverage_info = self._extract_coverage_info(timestamp)
        
        # Build comprehensive results
        test_results = {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "execution_time": execution_time,
            "timestamp": timestamp,
            "category": category,
            "stats": stats,
            "coverage": coverage_info,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(result.args) if hasattr(result, 'args') else "unknown"
        }
        
        return test_results
    
    def _extract_test_stats(self, output_lines: List[str]) -> Dict:
        """Extract test statistics from pytest output"""
        
        stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "warnings": 0
        }
        
        # Look for the final summary line (usually at the end)
        import re
        
        # Remove ANSI escape codes and look for pytest summary patterns
        for line in output_lines:
            # Remove ANSI escape codes
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            
            # Look for patterns like "9 passed, 40 deselected, 43 warnings in 8.03s"
            if re.search(r'\d+\s+(passed|failed|skipped|error)', clean_line):
                try:
                    # Extract passed tests
                    passed_match = re.search(r'(\d+)\s+passed', clean_line)
                    if passed_match:
                        stats["passed"] = int(passed_match.group(1))
                    
                    # Extract failed tests
                    failed_match = re.search(r'(\d+)\s+failed', clean_line)
                    if failed_match:
                        stats["failed"] = int(failed_match.group(1))
                    
                    # Extract skipped tests
                    skipped_match = re.search(r'(\d+)\s+skipped', clean_line)
                    if skipped_match:
                        stats["skipped"] = int(skipped_match.group(1))
                    
                    # Extract errors
                    error_match = re.search(r'(\d+)\s+error', clean_line)
                    if error_match:
                        stats["errors"] = int(error_match.group(1))
                    
                    # Extract warnings
                    warning_match = re.search(r'(\d+)\s+warnings?', clean_line)
                    if warning_match:
                        stats["warnings"] = int(warning_match.group(1))
                        
                except (ValueError, AttributeError):
                    continue
        
        stats["total"] = stats["passed"] + stats["failed"] + stats["skipped"] + stats["errors"]
        
        return stats
    
    def _extract_coverage_info(self, timestamp: str) -> Optional[Dict]:
        """Extract coverage information from coverage report"""
        
        coverage_file = self.reports_dir / f"coverage_{timestamp}.json"
        
        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                
                return {
                    "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                    "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                    "lines_missing": coverage_data.get("totals", {}).get("missing_lines", 0),
                    "total_lines": coverage_data.get("totals", {}).get("num_statements", 0)
                }
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"⚠️  Could not parse coverage data: {e}")
        
        return None
    
    def _generate_reports(self, test_results: Dict, timestamp: str):
        """Generate comprehensive test reports"""
        
        # Save detailed results
        results_file = self.reports_dir / f"results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        # Generate summary report
        summary_file = self.reports_dir / f"summary_{timestamp}.md"
        self._generate_markdown_summary(test_results, summary_file)
        
        logger.info(f"📊 Reports generated in: {self.reports_dir}")
    
    def _generate_markdown_summary(self, test_results: Dict, output_file: Path):
        """Generate markdown summary report"""
        
        with open(output_file, 'w') as f:
            f.write(f"# Test Results Summary - {test_results['timestamp']}\n\n")
            
            # Overall status
            status_emoji = "✅" if test_results["success"] else "❌"
            f.write(f"## Overall Status: {status_emoji} {'PASSED' if test_results['success'] else 'FAILED'}\n\n")
            
            # Execution details
            f.write("## Execution Details\n\n")
            f.write(f"- **Category**: {test_results.get('category', 'All')}\n")
            f.write(f"- **Execution Time**: {test_results['execution_time']:.2f} seconds\n")
            f.write(f"- **Return Code**: {test_results['return_code']}\n\n")
            
            # Test statistics
            stats = test_results["stats"]
            f.write("## Test Statistics\n\n")
            f.write(f"- **Total Tests**: {stats['total']}\n")
            f.write(f"- **Passed**: {stats['passed']} ✅\n")
            f.write(f"- **Failed**: {stats['failed']} ❌\n") 
            f.write(f"- **Skipped**: {stats['skipped']} ⏭️\n")
            f.write(f"- **Errors**: {stats['errors']} 🚨\n\n")
            
            # Coverage information
            if test_results.get("coverage"):
                coverage = test_results["coverage"]
                f.write("## Coverage Report\n\n")
                f.write(f"- **Total Coverage**: {coverage['total_coverage']:.1f}%\n")
                f.write(f"- **Lines Covered**: {coverage['lines_covered']}\n")
                f.write(f"- **Lines Missing**: {coverage['lines_missing']}\n")
                f.write(f"- **Total Lines**: {coverage['total_lines']}\n\n")
            
            # Success rate
            if stats['total'] > 0:
                success_rate = (stats['passed'] / stats['total']) * 100
                f.write(f"## Success Rate: {success_rate:.1f}%\n\n")
            
            # Command executed
            f.write("## Command Executed\n\n")
            f.write(f"```bash\n{test_results.get('command', 'Unknown')}\n```\n\n")
    
    def _log_test_summary(self, test_results: Dict):
        """Log comprehensive test summary"""
        
        logger.info("=" * 60)
        logger.info("🧪 TEST EXECUTION SUMMARY")
        logger.info("=" * 60)
        
        # Overall status
        if test_results["success"]:
            logger.info("✅ Overall Status: PASSED")
        else:
            logger.error("❌ Overall Status: FAILED")
        
        # Statistics
        stats = test_results["stats"]
        logger.info(f"📊 Test Statistics:")
        logger.info(f"   Total: {stats['total']}")
        logger.info(f"   Passed: {stats['passed']} ✅")
        logger.info(f"   Failed: {stats['failed']} ❌")
        logger.info(f"   Skipped: {stats['skipped']} ⏭️")
        logger.info(f"   Errors: {stats['errors']} 🚨")
        
        # Success rate
        if stats['total'] > 0:
            success_rate = (stats['passed'] / stats['total']) * 100
            logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Coverage
        if test_results.get("coverage"):
            coverage = test_results["coverage"]
            logger.info(f"📐 Code Coverage: {coverage['total_coverage']:.1f}%")
        
        # Execution time
        logger.info(f"⏱️  Execution Time: {test_results['execution_time']:.2f} seconds")
        
        # Reports location
        logger.info(f"📄 Reports saved to: {self.reports_dir}")
        
        logger.info("=" * 60)
    
    def run_quick_tests(self) -> bool:
        """Run quick smoke tests for CI/CD"""
        
        logger.info("🚀 Running quick smoke tests...")
        
        result = self.run_test_suite(
            category="unit",
            coverage=False,
            verbose=False,
            parallel=True,
            fail_fast=True
        )
        
        return result["success"]
    
    def run_full_test_suite(self) -> Dict:
        """Run complete comprehensive test suite"""
        
        logger.info("🔬 Running complete test suite...")
        
        all_results = {}
        overall_success = True
        
        # Run each category
        for category, config in self.test_categories.items():
            logger.info(f"Running {category} tests: {config['description']}")
            
            result = self.run_test_suite(
                category=category,
                coverage=(category == "unit"),  # Only coverage for unit tests
                verbose=True,
                parallel=config.get("parallel", False)
            )
            
            all_results[category] = result
            if not result["success"]:
                overall_success = False
        
        # Combine results
        combined_results = {
            "success": overall_success,
            "categories": all_results,
            "timestamp": datetime.now().isoformat()
        }
        
        return combined_results


def main():
    """Main CLI interface for test runner"""
    
    parser = argparse.ArgumentParser(description="Competitor Research Agent Test Runner")
    
    parser.add_argument(
        "command",
        choices=["quick", "full", "unit", "integration", "performance", "security", "e2e"],
        help="Test command to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c", 
        action="store_true",
        help="Enable coverage reporting"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true", 
        help="Run tests in parallel where possible"
    )
    
    parser.add_argument(
        "--fail-fast", "-x",
        action="store_true",
        help="Stop on first failure"
    )
    
    parser.add_argument(
        "--tests", "-t",
        nargs="+",
        help="Specific test files to run"
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    project_root = Path(__file__).parent
    runner = TestRunner(project_root)
    
    try:
        if args.command == "quick":
            success = runner.run_quick_tests()
            sys.exit(0 if success else 1)
            
        elif args.command == "full":
            results = runner.run_full_test_suite()
            sys.exit(0 if results["success"] else 1)
            
        else:
            # Run specific category
            results = runner.run_test_suite(
                category=args.command,
                specific_tests=args.tests,
                coverage=args.coverage,
                verbose=args.verbose,
                parallel=args.parallel,
                fail_fast=args.fail_fast
            )
            
            sys.exit(0 if results["success"] else 1)
    
    except KeyboardInterrupt:
        logger.info("🛑 Test execution interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
