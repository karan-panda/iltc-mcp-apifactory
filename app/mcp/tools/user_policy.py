"""
User Policy Tool for MCP.

This tool provides access to user policy information.
"""
import logging
from typing import Dict, Any, Optional, List

from app.mcp.resources.loader import ResourceLoader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UserPolicyTool:
    """Tool for retrieving user policy information."""
    
    def __init__(self):
        """Initialize the user policy tool."""
        logger.info("User Policy Tool initialized")
    
    def run(self, 
           policy_id: Optional[str] = None,
           user_name: Optional[str] = None,
           product_name: Optional[str] = None,
           query_type: str = "full") -> Dict[str, Any]:
        """
        Retrieve user policy information based on provided identifiers.
        
        Args:
            policy_id: Policy ID or number
            user_name: User name or identifier
            product_name: Product name
            query_type: Type of query - "full" for full details, 
                       "coverage" for coverage only, 
                       "proposer" for proposer details only,
                       "policy" for policy details only
            
        Returns:
            Dictionary with policy information or empty dict if not found
        """
        try:
            logger.info(f"Retrieving user policy details - policy_id: {policy_id}, user: {user_name}, product: {product_name}")
            
            # Get policy details using the ResourceLoader
            policy_details = ResourceLoader.get_user_policy_details(
                policy_id=policy_id,
                user_id=user_name,
                product_name=product_name
            )
            
            if not policy_details:
                logger.warning("No matching policy found")
                return {"result": {}, "error": "No matching policy found"}
            
            # Filter information based on query_type
            result = {}
            if query_type == "full":
                result = policy_details
            elif query_type == "coverage":
                result = {"coverages": policy_details.get("coverages", [])}
            elif query_type == "proposer":
                result = {"proposer_details": policy_details.get("proposer_details", {})}
            elif query_type == "policy":
                result = {"policy_details": policy_details.get("policy_details", {})}
            elif query_type == "insured":
                result = {"insured_details": policy_details.get("insured_details", {})}
            
            logger.info(f"Successfully retrieved {query_type} policy details")
            return {"result": result, "error": None}
            
        except Exception as e:
            logger.error(f"Error retrieving user policy information: {str(e)}")
            return {"result": {}, "error": str(e)}
    
    def get_coverage_details(self, policy_id: Optional[str] = None, coverage_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get specific coverage details from a policy.
        
        Args:
            policy_id: Policy ID or number
            coverage_name: Name of the specific coverage
            
        Returns:
            Coverage details or empty dict if not found
        """
        try:
            # First get all coverage information
            policy_info = self.run(policy_id=policy_id, query_type="coverage")
            
            if not policy_info.get("result") or "error" in policy_info:
                return {"result": {}, "error": "Policy not found"}
            
            coverages = policy_info["result"].get("coverages", [])
            
            # If no specific coverage requested, return all
            if not coverage_name:
                return {"result": {"coverages": coverages}, "error": None}
            
            # Search for the specific coverage
            for coverage in coverages:
                if coverage_name.lower() in coverage.get("cover_name", "").lower():
                    return {"result": {"coverage": coverage}, "error": None}
            
            return {"result": {}, "error": f"Coverage '{coverage_name}' not found in policy"}
            
        except Exception as e:
            logger.error(f"Error retrieving coverage details: {str(e)}")
            return {"result": {}, "error": str(e)}
