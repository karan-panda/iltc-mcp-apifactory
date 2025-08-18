# Extending the MCP Framework with Custom Tools

This document provides guidance on how to extend the Model Context Protocol (MCP) framework with custom tools to enhance the functionality of the insurance policy assistant.

> **Note**: For information on testing your MCP implementation using the MCP Inspector tool, see [Using MCP Inspector](./using_mcp_inspector.md).

## What is MCP?

The Model Context Protocol (MCP) is a structured approach for building more capable LLM applications by:

1. Clearly defining the inputs and outputs of each component
2. Providing a flexible framework for tool integration
3. Enabling more structured context handling

## Tool Architecture

Each MCP tool follows a consistent pattern:

1. **Tool Type Registration**: Define a new tool type in `protocol.py`
2. **Tool Implementation**: Create a class with a standardized interface
3. **Controller Integration**: Register the tool in the MCP controller
4. **API Access**: Use the tool through the MCP API

## Creating a New Tool

### Step 1: Define Tool Type in Protocol

Add your new tool type to the `ToolType` enum in `app/mcp/protocol.py`:

```python
class ToolType(str, Enum):
    """Types of tools available in the MCP framework."""
    VECTOR_SEARCH = "vector_search"
    INTENT_DETECTION = "intent_detection"
    # Add your new tool type here
    MY_NEW_TOOL = "my_new_tool"
```

### Step 2: Implement the Tool

Create a new Python file in the `app/mcp/tools` directory:

```python
"""
My new tool for MCP.
"""
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MyNewTool:
    """Tool description here."""
    
    def __init__(self, optional_param=None):
        """Initialize the tool."""
        self.optional_param = optional_param
        logger.info("My new tool initialized")
    
    def run(self, required_param: str, optional_param: str = None) -> Dict[str, Any]:
        """
        Main method to execute the tool functionality.
        
        Args:
            required_param: Description of parameter
            optional_param: Description of optional parameter
            
        Returns:
            Results from the tool execution
        """
        try:
            logger.info(f"Running my new tool with params: {required_param}, {optional_param}")
            
            # Implement your tool logic here
            result = {
                "status": "success",
                "data": f"Processed {required_param}"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in my new tool: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
```

### Step 3: Update the Tool Package

Add your tool to the `__init__.py` file in the `app/mcp/tools` directory:

```python
from app.mcp.tools.my_new_tool import MyNewTool

__all__ = [
    'IntentDetectionTool',
    'VectorSearchTool',
    'MyNewTool'
]
```

### Step 4: Register in the Controller

Import and register your tool in the `MCPController` class in `app/mcp/controller.py`:

```python
from app.mcp.tools.my_new_tool import MyNewTool

class MCPController:
    """Controller for MCP-based interactions."""
    
    def __init__(self):
        """Initialize the MCP controller with tools."""
        self.tools = {
            ToolType.INTENT_DETECTION: IntentDetectionTool(),
            ToolType.VECTOR_SEARCH: VectorSearchTool(),
            ToolType.MY_NEW_TOOL: MyNewTool(),
        }
```

## Using Your New Tool

### Option 1: Explicit Tool Invocation

Call your tool explicitly through the MCP API:

```python
import requests
import json

response = requests.post(
    "http://localhost:8001/mcp/query",
    headers={"Content-Type": "application/json"},
    data=json.dumps({
        "question": "Process this with my new tool",
        "tools": [
            {
                "tool_type": "my_new_tool",
                "parameters": {
                    "required_param": "some value",
                    "optional_param": "another value"
                }
            }
        ]
    })
)

print(response.json())
```

### Option 2: Automatic Tool Selection

Modify the controller to automatically invoke your tool for certain queries:

```python
def process_request(self, request: MCPRequest) -> MCPResponse:
    # Existing logic...
    
    # Example: Automatically invoke your tool for certain queries
    if "specific keyword" in request.user_query.lower():
        tool = self.tools[ToolType.MY_NEW_TOOL]
        try:
            result = tool.run(required_param="extracted from query")
            tool_results.append(
                ToolResponse(
                    tool_type=ToolType.MY_NEW_TOOL,
                    result=result
                )
            )
        except Exception as e:
            logger.error(f"Error with my new tool: {str(e)}")
```

## Best Practices for Tool Development

1. **Error Handling**: Always wrap your tool logic in try-except blocks
2. **Logging**: Use the logger to track tool execution
3. **Type Hints**: Use proper type hints for parameters and return values
4. **Documentation**: Document your tool's purpose and usage
5. **Testing**: Create tests for your tool to ensure it works as expected

## Example Tools to Consider

Here are some ideas for custom tools you might want to implement:

1. **Policy Recommendation Tool**: Recommend policies based on user preferences
2. **Claim Status Tracker**: Check the status of a customer's claim
3. **Premium Calculator**: Calculate premiums based on customer information
4. **Appointment Scheduler**: Schedule appointments with insurance agents
5. **Document Validator**: Validate insurance documents for compliance

## Conclusion

The MCP framework provides a flexible architecture for extending your insurance assistant with custom tools. By following this guide, you can create and integrate new tools to enhance the functionality of your application.
