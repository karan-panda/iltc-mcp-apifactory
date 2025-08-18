"""
MCP protocol definition for insurance policy assistant.
"""
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ToolType(str, Enum):
    """Types of tools available in the MCP framework."""
    VECTOR_SEARCH = "vector_search"
    INTENT_DETECTION = "intent_detection"
    POLICY_LOOKUP = "policy_lookup"
    FAQ_LOOKUP = "faq_lookup"
    COVERAGE_COMPARISON = "coverage_comparison"
    ACTION_RECOMMENDER = "action_recommender"
    USER_POLICY = "user_policy"


class ToolCall(BaseModel):
    """Represents a call to a specific tool."""
    tool_type: ToolType
    parameters: Dict[str, Any]


class ToolResponse(BaseModel):
    """Response from a tool call."""
    tool_type: ToolType
    result: Any
    error: Optional[str] = None


class MCPPrompt(BaseModel):
    """MCP structured prompt template."""
    template: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    
    def format(self, **kwargs):
        """Format the prompt with the provided variables."""
        template = self.template
        variables = {**self.variables, **kwargs}
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in template:
                template = template.replace(placeholder, str(value))
        return template


class MCPRequest(BaseModel):
    """A structured request in the MCP framework."""
    user_query: str
    context: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, Any]]] = None
    tools: Optional[List[ToolCall]] = None


class MCPResponse(BaseModel):
    """A structured response in the MCP framework."""
    response: str
    sources: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[ToolResponse]] = None
    detected_intent: Optional[Dict[str, Any]] = None


class MCPSession(BaseModel):
    """Represents an ongoing MCP session with history."""
    session_id: str
    history: List[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
