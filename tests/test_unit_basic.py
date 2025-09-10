"""
Basic unit tests for core functionality
"""
import pytest
from src.tools.search_tool import SearchTool
from src.utils.config import config

@pytest.mark.unit
def test_search_tool_basic_init():
    """Test basic SearchTool initialization"""
    tool = SearchTool()
    assert tool.name == "Enhanced Competitor Search Tool"
    assert hasattr(tool, '_run')

@pytest.mark.unit  
def test_config_basic():
    """Test basic config functionality"""
    assert hasattr(config, 'get_model_config')
    # Just test that config exists and has basic functionality
    assert config is not None
    
@pytest.mark.unit
def test_search_empty_query():
    """Test search tool with empty query"""
    tool = SearchTool()
    result = tool._run("")
    assert isinstance(result, str)
    # Should handle empty query gracefully
    assert len(result) > 0
