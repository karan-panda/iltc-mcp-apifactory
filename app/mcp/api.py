"""
FastAPI endpoints for MCP-enhanced insurance policy assistant.
"""
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.mcp.controller import MCPController
from app.mcp.protocol import MCPRequest, MCPResponse, ToolCall

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/mcp", tags=["MCP"])

# Initialize controller
mcp_controller = MCPController()


class MCPQueryRequest(BaseModel):
    """Request model for the MCP query endpoint."""
    question: str
    chat_history: Optional[List[Dict[str, Any]]] = []
    session_id: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0)


class MCPQueryResponse(BaseModel):
    """Response model for the MCP query endpoint."""
    answer: str
    sources: List[Dict[str, str]]
    session_id: str
    detected_intent: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None


@router.post("/query", response_model=MCPQueryResponse)
async def mcp_query(request: MCPQueryRequest):
    """
    Enhanced query endpoint that leverages MCP for more structured interactions.
    """
    try:
        # Validate input
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
            
        logger.info(f"Received MCP query: {request.question}")
        
        # Convert tools to ToolCall objects if provided
        tools = None
        if request.tools:
            tools = [ToolCall(tool_type=tool["tool_type"], parameters=tool["parameters"]) 
                    for tool in request.tools]
        
        # Create MCP request
        mcp_request = MCPRequest(
            user_query=request.question,
            history=request.chat_history,
            tools=tools
        )
        
        # Process request with MCP controller
        mcp_response = mcp_controller.process_request(mcp_request, session_id=request.session_id)
        
        # Convert tool results to dictionary format if available
        tool_results = None
        if mcp_response.tool_results:
            tool_results = [
                {
                    "tool_type": tool.tool_type,
                    "result": tool.result,
                    "error": tool.error
                }
                for tool in mcp_response.tool_results
            ]
        
        # Return the response
        return {
            "answer": mcp_response.response,
            "sources": mcp_response.sources or [],
            "session_id": request.session_id or mcp_controller.create_session(),
            "detected_intent": mcp_response.detected_intent,
            "tool_results": tool_results
        }
        
    except Exception as e:
        logger.error(f"Error processing MCP query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
