# Model Context Protocol (MCP) for IL TakeCare Assistant

This directory contains the Model Context Protocol (MCP) implementation for enhancing the IL TakeCare insurance policy assistant. MCP provides a structured approach to managing context, tools, and prompts for more powerful and consistent interactions.

## Directory Structure

```
app/mcp/
├── __init__.py
├── api.py              # FastAPI router for MCP endpoints
├── controller.py       # Main controller for orchestrating MCP components
├── protocol.py         # Protocol definitions using Pydantic models
├── prompts/            # Structured prompts for different scenarios
│   ├── __init__.py
│   └── library.py      # Library of prompt templates
├── resources/          # External resources and data
│   ├── __init__.py
│   ├── loader.py       # Resource loading utilities
│   └── openapi.json    # API documentation
└── tools/              # Tool implementations
    ├── __init__.py
    ├── intent_detection.py  # Intent detection using external ML API
    └── vector_search.py     # Vector search using Pinecone
```

## Features

- **Structured Prompting**: Manage and reuse prompt templates for different scenarios
- **Tool Integration**: Seamlessly integrate specialized tools like intent detection and vector search
- **Session Management**: Maintain context across multiple interactions
- **Enhanced Responses**: Provide more structured responses with sources and detected intents

## Tools

### Intent Detection

Detects user intent using an external ML API. Example:

```json
{
  "question": "I want to purchase TripSecure+",
  "tools": [
    {
      "tool_type": "intent_detection",
      "parameters": {}
    }
  ]
}
```

### Vector Search

Performs semantic search in the vector database:

```json
{
  "question": "What does travel insurance cover?",
  "tools": [
    {
      "tool_type": "vector_search",
      "parameters": {
        "top_k": 5
      }
    }
  ]
}
```

## Usage

Use the `/mcp/query` endpoint for enhanced interactions:

```bash
curl -X POST "http://localhost:8000/mcp/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does travel insurance cover for medical emergencies?",
    "temperature": 0.7
  }'
```

Example response:

```json
{
  "answer": "Based on your Travel Insurance document, medical emergencies are covered...",
  "sources": [
    {
      "name": "travel_insurance.pdf",
      "type": "Travel Insurance"
    }
  ],
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "detected_intent": {
    "intent": "Information Query",
    "route": "/info/travel",
    "score": 0.92
  },
  "tool_results": null
}
```

## Extending

To add new tools, create a new tool class in the tools directory and register it in the `MCPController` class.
