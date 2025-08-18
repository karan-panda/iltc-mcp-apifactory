"""
PDF processing utility for extracting text from policy documents and preparing them for embedding.
"""
import os
import logging
from typing import List, Dict, Tuple
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        Extracted text as a string.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        
        # Extract text from each page
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
        return ""

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into chunks of specified size with overlap.
    
    Args:
        text: Text to split.
        chunk_size: Size of each chunk (in characters).
        overlap: Number of characters to overlap between chunks.
        
    Returns:
        List of text chunks.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        # Get the chunk of text
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]
        
        # If not at the beginning and not at the end, try to find a period or newline
        # to make a more natural break
        if start > 0 and end < text_len:
            last_period = max(chunk.rfind('. '), chunk.rfind('.\n'))
            last_newline = chunk.rfind('\n\n')
            break_point = max(last_period, last_newline)
            
            if break_point != -1 and break_point > chunk_size // 2:
                end = start + break_point + 1  # +1 to include the period
                chunk = text[start:end]
        
        chunks.append(chunk)
        start = end - overlap if end < text_len else text_len
    
    return chunks

def process_pdf_directory(directory_path: str, doc_metadata: Dict = None) -> List[Dict]:
    """
    Process all PDF files in a directory and prepare them for embedding.
    
    Args:
        directory_path: Path to directory containing PDF files.
        doc_metadata: Optional dictionary mapping filenames to metadata.
        
    Returns:
        List of dictionaries with text chunks and metadata.
    """
    if doc_metadata is None:
        doc_metadata = {}
    
    documents = []
    
    try:
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(directory_path, filename)
                logger.info(f"Processing {filename}...")
                
                # Extract document type from filename (assuming format like "travel_insurance.pdf")
                doc_type = os.path.splitext(filename)[0].replace('_', ' ').title()
                
                # Extract text from PDF
                text = extract_text_from_pdf(file_path)
                
                if text:
                    # Chunk the text
                    chunks = chunk_text(text)
                    
                    # Create document records for each chunk
                    for i, chunk in enumerate(chunks):
                        # Get any additional metadata for this document
                        metadata = doc_metadata.get(filename, {})
                        
                        documents.append({
                            "text": chunk,
                            "metadata": {
                                "source": filename,
                                "doc_type": doc_type,
                                "chunk": i,
                                "total_chunks": len(chunks),
                                **metadata
                            }
                        })
                    
                    logger.info(f"Successfully processed {filename} into {len(chunks)} chunks")
                else:
                    logger.warning(f"No text extracted from {filename}")
    
    except Exception as e:
        logger.error(f"Error processing PDF directory: {str(e)}")
    
    return documents

if __name__ == "__main__":
    # Example usage
    pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    metadata = {
        "travel_insurance.pdf": {"category": "Travel", "version": "2023"},
        "health_insurance.pdf": {"category": "Health", "version": "2023"},
    }
    documents = process_pdf_directory(pdf_dir, metadata)
    print(f"Processed {len(documents)} document chunks")
