"""
Resource loader for MCP.
"""
import json
import logging
import os
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ResourceLoader:
    """Utility for loading external resources."""
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """
        Load JSON resource.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary with loaded JSON data
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Resource file not found: {file_path}")
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Successfully loaded resource: {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading resource {file_path}: {str(e)}")
            return {}
    
    @staticmethod
    def load_text(file_path: str) -> str:
        """
        Load text resource.
        
        Args:
            file_path: Path to text file
            
        Returns:
            String with file contents
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Resource file not found: {file_path}")
                return ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            logger.info(f"Successfully loaded resource: {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading resource {file_path}: {str(e)}")
            return ""
    
    @staticmethod
    def get_product_info(product_code_or_name: str) -> Dict[str, Any]:
        """
        Get information about a specific insurance product.
        
        Args:
            product_code_or_name: Product code or product name
            
        Returns:
            Dictionary with product information
        """
        try:
            # Load product information from JSON file
            product_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                          "data", "product_mapping.json")
            
            if not os.path.exists(product_file_path):
                logger.error(f"Product mapping file not found: {product_file_path}")
                return {}
                
            with open(product_file_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            # First check if the input matches a product code directly
            if product_code_or_name in products:
                return products[product_code_or_name]
            
            # If not found by code, search by name (case-insensitive)
            product_key = product_code_or_name.lower()
            for code, details in products.items():
                if product_key in details["name"].lower():
                    return details
            
            return {}
        except Exception as e:
            logger.error(f"Error retrieving product information: {str(e)}")
            return {}
            
    @staticmethod
    def get_user_policy_details(policy_id: str = None, user_id: str = None, product_name: str = None) -> Dict[str, Any]:
        """
        Get user's policy details.
        
        Args:
            policy_id: Policy ID or number to look up
            user_id: User ID to look up
            product_name: Product name to look up
            
        Returns:
            Dictionary with user policy information
        """
        try:
            # Load user details from JSON file
            user_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                       "data", "user_details.json")
            
            if not os.path.exists(user_file_path):
                logger.error(f"User details file not found: {user_file_path}")
                return {}
                
            with open(user_file_path, 'r', encoding='utf-8') as f:
                user_details = json.load(f)
            
            # Search by different criteria
            for product_key, details in user_details.items():
                policy_details = details.get("policy_details", {})
                proposer_details = details.get("proposer_details", {})
                
                # Match by policy ID
                if policy_id and (
                    policy_id == policy_details.get("policy_number") or 
                    policy_id == policy_details.get("alternative_policy_number")
                ):
                    return details
                
                # Match by product name
                if product_name and product_name.lower() in policy_details.get("product_name", "").lower():
                    return details
                
                # Match by user name/email (partial)
                if user_id and (
                    user_id.lower() in proposer_details.get("name", "").lower() or
                    user_id.lower() in proposer_details.get("email_id", "").lower()
                ):
                    return details
            
            return {}
        except Exception as e:
            logger.error(f"Error retrieving user policy details: {str(e)}")
            return {}
