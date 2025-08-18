"""
Intent detection tool for MCP.
"""
import json
import logging
import requests
from typing import Dict, Any, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntentDetectionTool:
    """Tool for detecting user intent using the ML API."""
    
    def __init__(self, api_url: str = "http://0.0.0.0:8000/predict"):
        """
        Initialize the intent detection tool.
        
        Args:
            api_url: URL of the intent detection API
        """
        self.api_url = api_url
        logger.info(f"Intent detection tool initialized with API URL: {api_url}")
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Detect user intent from query.
        
        Args:
            query: User query text
            
        Returns:
            Dictionary with detected intent and confidence score
        """
        logger.info(f"Detecting intent for query: {query}")
        
        try:
            # Call the intent detection API
            response = requests.post(
                self.api_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps({"query": query}),
                timeout=5
            )
            
            if response.status_code == 200:
                intents = response.json()
                
                # Return the top intent if available
                if intents and len(intents) > 0:
                    top_intent = intents[0]
                    logger.info(f"Detected intent: {top_intent['intent']} with score: {top_intent['score']}")
                    return top_intent
            
            # Return default if no intent detected or API error
            return {"intent": None, "route": None, "score": 0.0}
            
        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            return {"intent": None, "route": None, "score": 0.0}
