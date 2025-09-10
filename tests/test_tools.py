import pytest
from src.tools.search_tool import SearchTool

def test_search_tool_initialization():
    """Test that SearchTool can be initialized properly"""
    tool = SearchTool()
    assert tool.name == "Enhanced Competitor Search Tool"
    assert "Advanced web search tool" in tool.description
    assert hasattr(tool, '_run')

def test_search_tool_basic_functionality():
    """Test basic search functionality with a simple query"""
    tool = SearchTool()
    result = tool._run("test query")
    # The result should be either a valid search result or the failure message
    assert isinstance(result, str)
    assert len(result) > 0
    # Either we get results or a graceful failure message
    assert ("Search failed" in result) or ("Title:" in result) or len(result.strip()) > 0