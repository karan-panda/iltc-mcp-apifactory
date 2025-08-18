"""
Vector search tool for MCP.
"""
import logging
from typing import List, Dict, Any, Optional

from app.utils.embeddings import EmbeddingService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VectorSearchTool:
    """Tool for performing vector searches in Pinecone."""
    
    def __init__(self):
        """Initialize the vector search tool."""
        self.embedding_service = EmbeddingService()
        logger.info("Vector search tool initialized")
    
    def run(self, query: str, top_k: int = 5, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Perform vector search for relevant content.
        
        Args:
            query: Query text to search for
            top_k: Maximum number of results to return
            filter_criteria: Optional filter to apply to search
            
        Returns:
            List of matching documents
        """
        logger.info(f"Performing vector search for query: {query}")
        
        try:
            # Just pass the parameters that are supported by the embedding service
            results = self.embedding_service.query_similar(
                query_text=query,
                top_k=top_k
            )
            
            logger.info(f"Found {len(results)} matching documents")
            return results
            
        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            return []
