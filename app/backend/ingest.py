"""
Script for ingesting documents (PDFs and JSON FAQs) into the vector database.
"""
import os
import argparse
import logging
from dotenv import load_dotenv
from app.utils.pdf_processor import process_pdf_directory
from app.utils.json_processor import process_json_directory, process_faq_json
from app.utils.embeddings import EmbeddingService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def ingest_documents(data_dir: str, metadata: dict = None, doc_type: str = None, single_file: str = None):
    """
    Process documents (PDFs and JSON FAQs) and ingest them into Pinecone.
    
    Args:
        data_dir: Directory containing document files.
        metadata: Optional metadata dictionary for each file.
        doc_type: Type of documents to process ('pdf', 'json', or None for all).
        single_file: Optional single file to process.
    """
    try:
        documents = []
        
        # Process PDFs if requested
        if doc_type is None or doc_type.lower() == 'pdf':
            logger.info(f"Processing PDFs from {data_dir}")
            pdf_documents = process_pdf_directory(data_dir, metadata)
            if pdf_documents:
                documents.extend(pdf_documents)
                logger.info(f"Processed {len(pdf_documents)} chunks from PDF documents")
        
        # Process JSON files if requested
        if doc_type is None or doc_type.lower() == 'json':
            logger.info(f"Processing JSON files from {data_dir}")
            # If processing a single JSON file
            if single_file and single_file.lower().endswith('.json'):
                json_path = os.path.join(data_dir, single_file)
                json_documents = process_faq_json(json_path, metadata)
                if json_documents:
                    documents.extend(json_documents)
                    logger.info(f"Processed {len(json_documents)} FAQ items from {single_file}")
            else:
                json_documents = process_json_directory(data_dir, metadata)
                if json_documents:
                    documents.extend(json_documents)
                    logger.info(f"Processed {len(json_documents)} FAQ items from JSON files")
        
        if not documents:
            logger.warning("No documents processed. Check the data directory and files.")
            return
        
        logger.info(f"Total processed chunks: {len(documents)}")
        
        # Initialize embedding service
        logger.info("Initializing embedding service")
        embedding_service = EmbeddingService()
        
        # Upsert documents to Pinecone
        logger.info("Upserting documents to Pinecone")
        count = embedding_service.upsert_documents(documents)
        
        logger.info(f"Successfully ingested {count} document chunks into Pinecone")
        
    except Exception as e:
        logger.error(f"Error ingesting documents: {str(e)}")

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Ingest documents (PDFs and JSON FAQs) into Pinecone vector database.')
    parser.add_argument('--data_dir', type=str, default='app/data', 
                      help='Directory containing document files (default: app/data)')
    parser.add_argument('--single_file', type=str, default=None,
                      help='Process only a specific file in the data directory')
    parser.add_argument('--type', type=str, choices=['pdf', 'json'], default=None,
                      help='Type of documents to process (pdf or json)')
    args = parser.parse_args()
    
    # Set up metadata for each document type
    metadata = {
        "travel_insurance.pdf": {"category": "Travel", "version": "2025"},
        "health_insurance.pdf": {"category": "Health", "version": "2025"},
        "TripSecure+.pdf": {"category": "Travel", "version": "2025", "product": "TripSecure Plus"},
        "travel_faq.json": {"category": "Travel", "version": "2025", "content_type": "FAQ"}
    }
    
    if args.single_file:
        source_file = os.path.join(args.data_dir, args.single_file)
        
        if os.path.exists(source_file):
            logger.info(f"Processing only: {args.single_file}")
            # Determine doc_type from file extension
            doc_type = 'json' if args.single_file.lower().endswith('.json') else 'pdf'
            ingest_documents(args.data_dir, metadata, doc_type, args.single_file)
        else:
            logger.error(f"File not found: {source_file}")
    else:
        # Run ingestion for all files or specific type
        ingest_documents(args.data_dir, metadata, args.type)

if __name__ == "__main__":
    main()
