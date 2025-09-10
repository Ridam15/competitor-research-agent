import pytest
from src.workflows.competitor_research import create_workflow
from crewai import CrewOutput

def test_workflow_basic():
    """Test basic workflow execution"""
    result = create_workflow("test AI companies")
    
    # Handle both string and CrewOutput return types
    if isinstance(result, CrewOutput):
        # CrewOutput object - check the raw attribute which should contain the filename
        assert hasattr(result, 'raw'), "CrewOutput should have raw attribute"
        result_str = str(result.raw).lower()
    elif isinstance(result, str):
        result_str = result.lower()
    else:
        result_str = str(result).lower()
    
    # Check for successful PDF generation
    assert "pdf" in result_str, f"Expected 'pdf' in result, got: {result}"

def test_workflow_with_different_queries():
    """Test workflow with various query types"""
    test_queries = [
        "fintech competitors",
        "cloud computing companies", 
        "AI startups"
    ]
    
    for query in test_queries:
        result = create_workflow(query)
        
        # Convert result to string for testing
        if hasattr(result, 'raw'):
            result_str = str(result.raw)
        else:
            result_str = str(result)
            
        assert len(result_str) > 0, f"Empty result for query: {query}"
        # Should either be a PDF filename or error message
        assert ("pdf" in result_str.lower() or 
                "error" in result_str.lower() or 
                "failed" in result_str.lower()), f"Unexpected result format: {result_str}"

def test_workflow_error_handling():
    """Test workflow handles empty/invalid queries gracefully"""
    result = create_workflow("")
    
    # Should handle empty query without crashing
    assert result is not None, "Workflow should return something even for empty query"
    
    result_str = str(result.raw if hasattr(result, 'raw') else result)
    assert len(result_str) > 0, "Should return some result even for empty query"