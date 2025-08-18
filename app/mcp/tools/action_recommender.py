"""
Action recommender tool for MCP.

This tool analyzes user queries and recommends which tools to execute.
"""
import logging
import re
from typing import Dict, Any, List

from app.mcp.protocol import ToolType

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ActionRecommenderTool:
    """Tool for recommending which other tools to execute based on user query."""
    
    def __init__(self):
        """Initialize the action recommender tool."""
        # Define patterns for tool selection
        self.patterns = {
            ToolType.VECTOR_SEARCH: [
                r"what (does|do|is|are)",
                r"tell me about",
                r"explain",
                r"information",
                r"details"
            ],
            ToolType.USER_POLICY: [
                r"my (policy|insurance|cover|coverage)",
                r"my (plan|benefits)",
                r"(policy|reference) number",
                r"policy details",
                r"my (sum|amount) insured",
                r"what (am i|are we) covered for",
                r"(view|show|get) my policy"
            ]
        }
        
        # Keywords for policy types
        self.policy_types = {
            "travel": ["travel", "trip", "journey", "vacation", "holiday"],
            "health": ["health", "medical", "healthcare", "elevate", "standard"],
            "motor": ["auto", "car", "vehicle", "motor"],
            "home": ["home", "house", "property", "renters"]
        }
        
        logger.info("Action recommender tool initialized")
    
    def _extract_policy_type(self, query: str) -> str:
        """Extract policy type from the query."""
        query_lower = query.lower()
        
        for policy_type, keywords in self.policy_types.items():
            if any(keyword in query_lower for keyword in keywords):
                return policy_type
        
        return "travel"  # Default to travel if no type detected
    
    def _should_use_tool(self, query: str, tool_type: ToolType) -> bool:
        """Check if the tool should be used based on query patterns."""
        query_lower = query.lower()
        
        for pattern in self.patterns.get(tool_type, []):
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def run(self, query: str) -> List[Dict[str, Any]]:
        """
        Recommend tools to execute based on user query.
        
        Args:
            query: User question
            
        Returns:
            List of recommended tool calls with parameters
        """
        try:
            logger.info(f"Analyzing query for tool recommendations: {query}")
            
            recommended_tools = []
            policy_type = self._extract_policy_type(query)
            
            # Check for keywords indicating the query might be about the user's policy
            my_policy_keywords = ["my", "details", "policy", "number", "coverage", "plan", "insurance"]
            user_query_likely = any(keyword in query.lower() for keyword in my_policy_keywords)
            
            # Extract policy ID if present
            policy_id_match = re.search(r"policy (?:number|id)?\s*[:#]?\s*([\w\/\-]+)", query.lower())
            policy_id = policy_id_match.group(1) if policy_id_match else None
            
            # Check for coverage-specific queries
            coverage_match = re.search(r"(cover(age)?|benefit)[s]?\s+for\s+(\w+)", query.lower())
            coverage_name = coverage_match.group(3) if coverage_match else None
            
            # Determine query type
            query_type = "full"
            
            # Always use the user policy tool if we have a policy ID
            # or if the query likely refers to the user's own policy
            if policy_id or user_query_likely:
                if re.search(r"coverage|benefit|cover", query.lower()):
                    query_type = "coverage"
                elif re.search(r"my details|personal (info|details)|proposer", query.lower()):
                    query_type = "proposer"
                
                recommended_tools.append({
                    "tool_type": ToolType.USER_POLICY,
                    "parameters": {
                        "policy_id": policy_id,
                        "query_type": query_type,
                        "product_name": policy_type if policy_type in ["travel", "health"] else None
                    }
                })
            
            # Vector search is always useful
            recommended_tools.append({
                "tool_type": ToolType.VECTOR_SEARCH,
                "parameters": {
                    "query": query,
                    "top_k": 3
                }
            })
            
            logger.info(f"Recommended tools: {[t['tool_type'] for t in recommended_tools]}")
            return recommended_tools
            
        except Exception as e:
            logger.error(f"Error recommending tools: {str(e)}")
            return [{
                "tool_type": ToolType.VECTOR_SEARCH,
                "parameters": {
                    "query": query
                }
            }]
