"""
Main entry point for the policy wording assistant application.
"""
import os
import logging
import uvicorn
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    """Run the FastAPI application."""
    try:
        logger.info("Starting Policy Wording Assistant API")
        
        # Configure the Uvicorn server
        uvicorn.run(
            "app.backend.api:app",
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")

if __name__ == "__main__":
    main()
