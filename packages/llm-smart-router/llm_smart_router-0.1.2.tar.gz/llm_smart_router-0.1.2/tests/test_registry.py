"""
Unit tests for ToolRegistry
"""

import pytest
from smart_router import ToolRegistry, AGDomain, ToolMetadata


def test_registry_initialization():
    """Test basic registry initialization"""
    registry = ToolRegistry()
    assert registry.total_tools == 0


def test_register_tool():
    """Test registering a single tool"""
    registry = ToolRegistry()
    
    registry.register_tool(
        name="test_tool",
        domain=AGDomain.MAAG,
        description="Test tool description"
    )
    
    assert registry.total_tools == 1
    tools = registry.get_tools_by_domain(AGDomain.MAAG)
    assert len(tools) == 1
    assert tools[0].name == "test_tool"


def test_get_tools_by_domain():
    """Test filtering tools by domain"""
    registry = ToolRegistry()
    
    # Register tools in different domains
    registry.register_tool("tool1", AGDomain.MAAG, "Metrics tool")
    registry.register_tool("tool2", AGDomain.MAAG, "Another metrics tool")
    registry.register_tool("tool3", AGDomain.LAAG, "Logs tool")
    
    maag_tools = registry.get_tools_by_domain(AGDomain.MAAG)
    laag_tools = registry.get_tools_by_domain(AGDomain.LAAG)
    
    assert len(maag_tools) == 2
    assert len(laag_tools) == 1


def test_get_tools_by_multiple_domains():
    """Test getting tools from multiple domains"""
    registry = ToolRegistry()
    
    registry.register_tool("tool1", AGDomain.MAAG, "Metrics tool")
    registry.register_tool("tool2", AGDomain.LAAG, "Logs tool")
    registry.register_tool("tool3", AGDomain.CAAG, "Code tool")
    
    tools = registry.get_tools_by_domains([AGDomain.MAAG, AGDomain.LAAG])
    
    assert len(tools) == 2
    tool_names = [t.name for t in tools]
    assert "tool1" in tool_names
    assert "tool2" in tool_names
    assert "tool3" not in tool_names


def test_get_domain_statistics():
    """Test getting statistics about registered tools"""
    registry = ToolRegistry()
    
    # Register varying numbers of tools per domain
    for i in range(5):
        registry.register_tool(f"maag_tool_{i}", AGDomain.MAAG, f"Tool {i}")
    for i in range(3):
        registry.register_tool(f"laag_tool_{i}", AGDomain.LAAG, f"Tool {i}")
    
    stats = registry.get_domain_statistics()
    
    assert AGDomain.MAAG in stats
    assert stats[AGDomain.MAAG] == 5
    assert stats[AGDomain.LAAG] == 3


def test_duplicate_tool_registration():
    """Test that duplicate tools are handled"""
    registry = ToolRegistry()
    
    registry.register_tool("duplicate", AGDomain.MAAG, "First")
    
    # Registering same tool should update, not duplicate
    registry.register_tool("duplicate", AGDomain.MAAG, "Updated")
    
    tools = registry.get_tools_by_domain(AGDomain.MAAG)
    assert len(tools) == 1
    assert tools[0].description == "Updated"
