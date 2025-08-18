"""
Embeddings utility for converting text to vectors using HuggingFace models
and storing them in Pinecone vector database.
"""
import os
import logging
from typing import List, Dict, Any
import uuid
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class EmbeddingService:
    """Service for managing document embeddings with Pinecone."""
    
    def __init__(
        self, 
        model_name: str = "all-MiniLM-L6-v2",  # This model produces 384-dimensional embeddings
        index_name: str = None,
        dimension: int = 384  # Matching Pinecone's configured dimension
    ):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the HuggingFace model to use for embeddings.
            index_name: Name of the Pinecone index.
            dimension: Dimension of the embeddings.
        """
        self.model_name = model_name
        self.index_name = index_name or os.getenv("INDEX_NAME", "policy-assistant")
        self.dimension = dimension
        
        # Initialize the embedding model
        logger.info(f"Initializing embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Initialize Pinecone
        self._init_pinecone()
    
    def _init_pinecone(self):
        """Initialize the Pinecone client and ensure the index exists."""
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            
            if not api_key:
                raise ValueError("Pinecone API key must be set in .env file")
            
            # Initialize Pinecone
            self.pc = Pinecone(api_key=api_key)
            
            # my Pinecone index pre-configuration:
            # - Host: https://policy-assistant-emvpjns.svc.aped-4627-b74a.pinecone.io
            # - Dimension: 384
            # - Metric: cosine
            # - Region: us-east-1
            # - Cloud: aws
            
            # Check if index exists, if not create it
            index_list = self.pc.list_indexes()
            if self.index_name not in (index_list.names() if hasattr(index_list, 'names') else [i['name'] for i in index_list]):
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384, 
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1" 
                    )
                )
            
            # Connect to the index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a piece of text.
        
        Args:
            text: Text to embed.
            
        Returns:
            List of embedding values (vector).
        """
        try:
            return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []
    
    def upsert_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Convert documents to embeddings and insert them into Pinecone.
        
        Args:
            documents: List of document dictionaries with "text" and "metadata" keys.
            
        Returns:
            Number of documents inserted.
        """
        try:
            vectors_to_upsert = []
            
            for doc in documents:
                text = doc["text"]
                metadata = doc["metadata"]
                
                # Generate embedding
                embedding = self.generate_embedding(text)
                
                if embedding:
                    # Create a unique ID for this document chunk
                    doc_id = str(uuid.uuid4())
                    
                    # Store the original text in the metadata
                    metadata["text"] = text
                    
                    # Add to list for batch upsert
                    vectors_to_upsert.append((doc_id, embedding, metadata))
            
            # Batch upsert to Pinecone
            if vectors_to_upsert:
                self.index.upsert(vectors=vectors_to_upsert)
                logger.info(f"Upserted {len(vectors_to_upsert)} documents to Pinecone")
                return len(vectors_to_upsert)
            else:
                logger.warning("No valid embeddings to upsert")
                return 0
                
        except Exception as e:
            logger.error(f"Error upserting documents: {str(e)}")
            return 0
    
    def query_similar(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Find similar documents in the vector database.
        
        Args:
            query_text: Text to search for.
            top_k: Number of results to return.
            
        Returns:
            List of dictionaries with similar document info.
        """
        try:
            # Generate embedding for the query
            query_embedding = self.generate_embedding(query_text)
            
            if not query_embedding:
                return []
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Extract and format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "score": match.score,
                    "text": match.metadata.get("text", ""),
                    "source": match.metadata.get("source", ""),
                    "doc_type": match.metadata.get("doc_type", ""),
                    "metadata": {k: v for k, v in match.metadata.items() if k != "text"}
                })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error querying similar documents: {str(e)}")
            return []

if __name__ == "__main__":
    # Example usage
    embedding_service = EmbeddingService()
    test_docs = [
        {
            "text": "Travel insurance covers unexpected medical expenses during your trip abroad.",
            "metadata": {"source": "test", "doc_type": "Travel Insurance"}
        }
    ]
    embedding_service.upsert_documents(test_docs)
    results = embedding_service.query_similar("What does travel insurance cover?")
    print(results)
