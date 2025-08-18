import os
import argparse
import logging
import shutil
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        'app/data',
        'app/backend',
        'app/frontend',
        'app/utils',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_path = Path('.env')
    if not env_path.exists():
        with open(env_path, 'w') as f:
            f.write("""PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
HUGGINGFACE_API_TOKEN=your_huggingface_api_token_here
INDEX_NAME=policy-assistant
""")
        logger.info("Created .env file")
    else:
        logger.info(".env file already exists")

def ensure_data_directory():
    """Ensure the data directory exists for user's PDF files."""
    data_dir = 'app/data'
    os.makedirs(data_dir, exist_ok=True)
    logger.info(f"Ensured data directory exists: {data_dir}")
    logger.info(f"Please place your insurance PDF files in the {data_dir} directory.")
    logger.info(f"Required files: travel_insurance.pdf, health_insurance.pdf")

def main():
    """Main function to initialize the project."""
    parser = argparse.ArgumentParser(description='Initialize the Policy Wording Assistant project.')
    args = parser.parse_args()
    
    try:
        # Create directory structure
        create_directories()
        
        # Create .env file
        create_env_file()
        
        # Ensure data directory exists for user's PDF files
        ensure_data_directory()
        
        logger.info("Project initialization complete!")
        logger.info("Next steps:")
        logger.info("1. Add your API keys to the .env file")
        logger.info("2. Add your PDF documents to the app/data directory")
        logger.info("3. Run: python -m app.backend.ingest")
        logger.info("4. Start the backend: python main.py")
        logger.info("5. Start the frontend: python -m app.frontend.serve")
        
    except Exception as e:
        logger.error(f"Error initializing project: {str(e)}")

if __name__ == "__main__":
    main()
