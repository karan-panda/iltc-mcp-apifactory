"""
JSON processing utility for extracting FAQ data and preparing them for embedding.
"""
import os
import json
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_faq_from_json(json_path: str) -> List[Dict]:
    """
    Extract FAQ data from a JSON file.
    
    Args:
        json_path: Path to the JSON file.
        
    Returns:
        List of dictionaries with extracted FAQ data.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Successfully loaded JSON data from {json_path}")
        
        if not isinstance(data, list):
            logger.warning(f"Expected a list of FAQs, got {type(data)} instead")
            return []
            
        return data
    except Exception as e:
        logger.error(f"Error extracting data from {json_path}: {str(e)}")
        return []

def process_faq_json(json_path: str, metadata: Dict = None) -> List[Dict]:
    """
    Process a JSON FAQ file and prepare it for embedding.
    
    Args:
        json_path: Path to the JSON file.
        metadata: Optional metadata to include with each chunk.
        
    Returns:
        List of dictionaries with text chunks and metadata.
    """
    documents = []
    
    try:
        # Get filename for source attribution
        filename = os.path.basename(json_path)
        
        # Extract document type from filename
        doc_type = os.path.splitext(filename)[0].replace('_', ' ').title()
        
        # Extract FAQ data from JSON
        faqs = extract_faq_from_json(json_path)
        
        if not faqs:
            logger.warning(f"No FAQs found in {json_path}")
            return []
        
        # Process each FAQ
        for i, faq in enumerate(faqs):
            # Check if the FAQ has both question and answer
            if not isinstance(faq, dict) or 'question' not in faq or 'answer' not in faq:
                logger.warning(f"Skipping invalid FAQ format at index {i}")
                continue
                
            question = faq['question']
            answer = faq['answer']
            
            # Combine question and answer for better semantic search
            text = f"Question: {question}\nAnswer: {answer}"
            
            # Create metadata for this FAQ
            chunk_metadata = {
                "source": filename,
                "doc_type": doc_type,
                "faq_id": i,
                "question": question
            }
            
            # Add additional metadata if provided
            if metadata and filename in metadata:
                chunk_metadata.update(metadata[filename])
            
            # Add to documents list
            documents.append({
                "text": text,
                "metadata": chunk_metadata
            })
        
        logger.info(f"Processed {len(documents)} FAQ items from {json_path}")
        return documents
        
    except Exception as e:
        logger.error(f"Error processing {json_path}: {str(e)}")
        return []

def process_json_directory(directory_path: str, metadata: Dict = None) -> List[Dict]:
    """
    Process all JSON files in a directory and prepare them for embedding.
    
    Args:
        directory_path: Path to directory containing JSON files.
        metadata: Optional dictionary mapping filenames to metadata.
        
    Returns:
        List of dictionaries with text chunks and metadata.
    """
    if metadata is None:
        metadata = {}
    
    documents = []
    
    try:
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.json'):
                file_path = os.path.join(directory_path, filename)
                logger.info(f"Processing {filename}...")
                
                # Process the JSON file
                docs = process_faq_json(file_path, metadata)
                documents.extend(docs)
        
        logger.info(f"Processed {len(documents)} total FAQ items from JSON files")
        return documents
        
    except Exception as e:
        logger.error(f"Error processing directory {directory_path}: {str(e)}")
        return documents  # Return any documents processed so far
