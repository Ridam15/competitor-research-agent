"""
Enhanced test suite for improved tools and functionality
"""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.tools.search_tool import SearchTool, SearchResult
from src.tools.pdf_tool import EnhancedPDFReportTool
from src.tools.llm_tool import LLMSummarizerTool
from src.utils.config import config, validate_configuration

class TestSearchTool:
    """Test cases for enhanced SearchTool"""
    
    def setup_method(self):
        """Setup test environment"""
        self.search_tool = SearchTool()
    
    def test_search_tool_initialization(self):
        """Test that SearchTool initializes properly with enhanced features"""
        assert self.search_tool.name == "Enhanced Competitor Search Tool"
        assert "Advanced web search" in self.search_tool.description
        assert hasattr(self.search_tool, 'MAX_RESULTS')
        assert hasattr(self.search_tool, 'RETRY_COUNT')
    
    def test_query_optimization(self):
        """Test query optimization functionality"""
        optimized = self.search_tool._optimize_query("OpenAI")
        assert isinstance(optimized, list)
        assert len(optimized) >= 1
        assert "OpenAI" in optimized[0]
        # Should contain variations
        assert any("competitors" in q or "alternatives" in q for q in optimized)
    
    def test_search_result_formatting(self):
        """Test search result formatting"""
        mock_results = [
            SearchResult("Test Company", "https://test.com", "Test description"),
            SearchResult("Another Company", "https://another.com", "Another description")
        ]
        
        formatted = self.search_tool._format_results(mock_results, "test query")
        assert "Search Results for: 'test query'" in formatted
        assert "Test Company" in formatted
        assert "https://test.com" in formatted
        assert "Result 1:" in formatted
        assert "Result 2:" in formatted
    
    def test_empty_query_handling(self):
        """Test handling of empty queries"""
        result = self.search_tool._run("")
        assert "Error: Empty search query" in result
        
        result = self.search_tool._run("   ")
        assert "Error: Empty search query" in result
    
    @patch('src.tools.search_tool.DDGS')
    def test_search_with_mock_results(self, mock_ddgs):
        """Test search functionality with mocked results"""
        # Setup mock
        mock_instance = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_instance
        mock_instance.text.return_value = [
            {'title': 'Test Company', 'href': 'https://test.com', 'body': 'Test description'},
            {'title': 'Competitor Corp', 'href': 'https://competitor.com', 'body': 'Competitor info'}
        ]
        
        result = self.search_tool._run("test query")
        
        assert isinstance(result, str)
        assert "Test Company" in result
        assert "Competitor Corp" in result
    
    def test_result_filtering_and_ranking(self):
        """Test result filtering and ranking"""
        mock_results = [
            SearchResult("Quality Company", "https://quality.com", "Great business description"),
            SearchResult("Error", "javascript:void(0)", "Error page"),
            SearchResult("Short", "https://short.com", "X"),  # Too short
            SearchResult("Another Quality Co", "https://another-quality.com", "Excellent enterprise solution")
        ]
        
        filtered = self.search_tool._filter_and_rank_results(mock_results, "business enterprise")
        
        # Should filter out poor quality results
        assert len(filtered) < len(mock_results)
        assert not any(r.title == "Error" for r in filtered)
        assert not any(r.title == "Short" for r in filtered)


class TestEnhancedPDFTool:
    """Test cases for EnhancedPDFReportTool"""
    
    def setup_method(self):
        """Setup test environment"""
        self.pdf_tool = EnhancedPDFReportTool()
        self.test_summary = """
        Executive Summary: This analysis covers the competitive landscape for AI companies.
        Key findings include market growth, pricing strategies, and competitive positioning.
        Microsoft and Google are leading competitors. OpenAI shows strong innovation.
        Recommendations include focusing on differentiation and pricing optimization.
        """
    
    def test_pdf_tool_initialization(self):
        """Test PDF tool initialization"""
        assert self.pdf_tool.name == "Enhanced PDF Report Generator Tool"
        # The tool should be able to setup styles when needed
        styles = self.pdf_tool._setup_custom_styles()
        assert isinstance(styles, dict)
        assert 'title' in styles
    
    def test_structured_data_extraction(self):
        """Test extraction of structured data from content"""
        structured = self.pdf_tool._extract_structured_data(self.test_summary)
        
        assert isinstance(structured, dict)
        assert 'executive_summary' in structured
        assert 'key_findings' in structured
        assert 'competitors' in structured
        assert 'recommendations' in structured
        
        # Should extract some companies
        assert len(structured['competitors']) > 0
        assert any('Microsoft' in comp or 'Google' in comp for comp in structured['competitors'])
    
    def test_filename_generation(self):
        """Test filename generation"""
        filename = self.pdf_tool._generate_filename("OpenAI competitors")
        assert filename.endswith('.pdf')
        assert 'OpenAI_competitors' in filename
        assert 'Competitor_Analysis' in filename
        
        # Test with special characters
        filename = self.pdf_tool._generate_filename("Test & Query!")
        assert filename.endswith('.pdf')
        assert '&' not in filename
        assert '!' not in filename
    
    def test_pdf_generation(self):
        """Test actual PDF generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_filename = os.path.join(temp_dir, "test_report.pdf")
            
            result = self.pdf_tool._run(
                summary=self.test_summary,
                filename=test_filename,
                query="Test AI competitors"
            )
            
            # Should return the absolute path
            assert result == os.path.abspath(test_filename)
            assert os.path.exists(test_filename)
            
            # File should have reasonable size (> 1KB)
            assert os.path.getsize(test_filename) > 1000


class TestLLMSummarizerTool:
    """Test cases for LLMSummarizerTool"""
    
    def setup_method(self):
        """Setup test environment"""
        self.llm_tool = LLMSummarizerTool()
    
    def test_llm_tool_initialization(self):
        """Test LLM tool initialization"""
        assert self.llm_tool.name == "LLM Summarizer Tool"
        assert "Summarizes text" in self.llm_tool.description
        assert hasattr(self.llm_tool, 'model')
    
    @pytest.mark.integration
    @patch('google.generativeai.GenerativeModel')
    def test_summarization_with_mock(self, mock_model_class):
        """Test summarization with mocked Gemini API"""
        # Setup mock
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a test summary of the provided content."
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        test_content = "This is a long piece of content that needs to be summarized for analysis."
        result = self.llm_tool._run(test_content)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert result != test_content  # Should be different from input


class TestConfiguration:
    """Test cases for configuration management"""
    
    def test_config_initialization(self):
        """Test configuration initialization"""
        assert hasattr(config, 'groq_api_key')
        assert hasattr(config, 'gemini_api_key')
        assert hasattr(config, 'primary_model')
        assert hasattr(config, 'fallback_models')
    
    def test_model_config(self):
        """Test model configuration retrieval"""
        try:
            model_config = config.get_model_config()
            assert isinstance(model_config, dict)
            assert 'provider' in model_config
            assert 'model' in model_config
            assert 'api_key' in model_config
        except ValueError:
            # Expected if no API keys are configured
            pytest.skip("No valid API keys configured for testing")
    
    def test_rate_limit_config(self):
        """Test rate limiting configuration"""
        rate_config = config.rate_limit_config
        assert isinstance(rate_config, dict)
        assert 'max_retries' in rate_config
        assert 'base_delay' in rate_config
        assert 'backoff_factor' in rate_config
        
        # Values should be reasonable
        assert rate_config['max_retries'] >= 1
        assert rate_config['base_delay'] >= 1
        assert rate_config['backoff_factor'] >= 1.5


class TestIntegration:
    """Integration test cases"""
    
    @pytest.mark.integration
    def test_tool_chain_integration(self):
        """Test that tools can work together"""
        search_tool = SearchTool()
        pdf_tool = EnhancedPDFReportTool()
        
        # Test that search results can be passed to PDF generation
        mock_search_result = "Found 3 competitors: CompanyA, CompanyB, CompanyC. Analysis shows strong market positioning."
        
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = os.path.join(temp_dir, "integration_test.pdf")
            result = pdf_tool._run(mock_search_result, pdf_path, "test integration")
            
            assert os.path.exists(pdf_path)
            assert os.path.getsize(pdf_path) > 1000
    
    def test_error_handling_chain(self):
        """Test error handling across tools"""
        search_tool = SearchTool()
        pdf_tool = EnhancedPDFReportTool()
        
        # Test with problematic inputs
        empty_result = search_tool._run("")
        assert "Error" in empty_result
        
        # PDF tool should handle empty/error content gracefully
        pdf_result = pdf_tool._run(empty_result, query="error test")
        assert isinstance(pdf_result, str)
        # Should either succeed or return error message
        assert pdf_result.endswith('.pdf') or pdf_result.startswith('Error')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
