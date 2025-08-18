import os
import logging
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from app.utils.embeddings import EmbeddingService
from app.utils.chatbot import ChatbotService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="IL TakeCare Assistant API",
    description="API for querying insurance policy information",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import MCP router if available
try:
    from app.mcp.api import router as mcp_router
    app.include_router(mcp_router)
    logger.info("MCP API router included")
except ImportError:
    logger.warning("MCP API router not available, skipping")

# Initialize services
embedding_service = EmbeddingService()
# We'll initialize the chatbot service on demand with the requested model

# Define request and response models
class QueryRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = []
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    model: Optional[str] = Field("gemini-1.5-flash", description="Gemini model to use: gemini-1.5-flash (highest quota), gemini-1.5-pro, or gemini-2.5-pro (lowest quota)")

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]

@app.get("/")
async def root():
    """Root endpoint for API health check."""
    return {"status": "ok", "message": "Policy Wording Assistant API is running"}

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        # Validate input
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
            
        logger.info(f"Received query: {request.question}")
        
        # Retrieve relevant context from the vector database
        try:
            context_results = embedding_service.query_similar(request.question, top_k=3)
            
            if not context_results:
                logger.warning("No relevant context found in the vector database")
                # Ensure it's at least an empty list
                context_results = []
        except Exception as context_error:
            logger.error(f"Error retrieving context: {str(context_error)}")
            context_results = []
        
        # Generate response using the chatbot service
        system_prompt = """You are an insurance policy assistant. Your task is to answer questions about insurance policies based on the provided context.
Use only the information from the policy documents when answering. If the information needed to answer is not available in the context,
state that you don't have enough information to provide an accurate answer rather than making up information.
Always cite your sources by indicating which policy document (Travel or Health) your information comes from."""

        # MCP Comment: Here is where MCP could be used to structure the prompt assembly and chain queries
        # MCP would enable more structured prompt templates and better handling of multiple knowledge sources
        
        try:
            # Initialize the chatbot service with the requested model
            model_to_use = request.model
            logger.info(f"Using Gemini model: {model_to_use}")
            chatbot_service = ChatbotService(model_name=model_to_use)
            
            response = chatbot_service.generate_response(
                query=request.question,
                context=context_results,
                chat_history=request.chat_history,
                temperature=request.temperature,
                system_prompt=system_prompt
            )
            
            # Ensure response is a string
            if response is None:
                response = "I apologize, but I couldn't generate a response at this time."
        except Exception as resp_error:
            logger.error(f"Error generating response: {str(resp_error)}")
            response = f"I apologize, but I encountered an error while processing your question: {str(resp_error)}"
        
        # Extract sources for citation
        sources = []
        for result in context_results:
            try:
                source = {
                    "name": result.get("source", "Deafault"),
                    "type": result.get("doc_type", "Deafault"),
                }
                if source not in sources:
                    sources.append(source)
            except Exception as source_error:
                logger.error(f"Error processing source: {str(source_error)}")
                
        # If no sources were found, provide a default
        if not sources:
            sources = [{"name": "No specific source", "type": "General Information"}]
        
        return {
            "answer": response,
            "sources": sources
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        # Return a valid response even in case of error
        return {
            "answer": f"I apologize, but I encountered an error while processing your question. Please try again later.",
            "sources": [{"name": "Error", "type": "System"}]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
