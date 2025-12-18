"""
LLM Smart Router - Intelligent tool routing for Large Language Models

Reduces 90+ tools to 3-8 relevant tools per query with 95.8% reduction.
"""

__version__ = "0.1.3"
__author__ = "LLM Smart Router Contributors"
__license__ = "MIT"

from smart_router.models import AGDomain, ToolMetadata, RoutingDecision
from smart_router.tool_registry import ToolRegistry
from smart_router.router import SmartRouter

__all__ = [
    "AGDomain",
    "ToolMetadata",
    "RoutingDecision",
    "ToolRegistry",
    "SmartRouter",
    
]
