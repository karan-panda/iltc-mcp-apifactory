"""
Intent detection tool for MCP.
"""
import json
import logging
import requests
from typing import Dict, Any, Optional, Union, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntentDetectionTool:
    """Tool for detecting user intent using the ML API. Returns a list of top 3 intents sorted by score."""
    
    def __init__(self, api_url: str = "http://0.0.0.0:8000/predict"):
        """
        Initialize the intent detection tool.
        
        Args:
            api_url: URL of the intent detection API
        """
        self.api_url = api_url
        logger.info(f"Intent detection tool initialized with API URL: {api_url}")
    
    def run(self, query: str) -> List[Dict[str, Any]]:
        """
        Detect user intent from query.
        
        Args:
            query: User query text
            
        Returns:
            List of dictionaries with detected intents and confidence scores,
            with a maximum of 3 results sorted by score in descending order
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
                
                # Return the top 3 intents if available, sorted by score
                if intents and len(intents) > 0:
                    # Sort intents by score in descending order and take top 3
                    top_intents = sorted(intents, key=lambda x: x.get('score', 0), reverse=True)[:3]
                    
                    # Log the top intent
                    if top_intents:
                        top_intent = top_intents[0]
                        logger.info(f"Top detected intent: {top_intent['intent']} with score: {top_intent['score']}")
                        
                        # Log secondary intents
                        if len(top_intents) > 1:
                            secondary_intents = [f"{intent['intent']} ({intent['score']:.2f})" for intent in top_intents[1:]]
                            logger.info(f"Secondary intents: {', '.join(secondary_intents)}")
                    
                    return top_intents
            
            # Return default if no intent detected or API error
            return [{"intent": None, "route": None, "score": 0.0}]
            
        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            return [{"intent": None, "route": None, "score": 0.0}]
