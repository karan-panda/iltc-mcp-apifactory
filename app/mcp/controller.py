"""
MCP Controller for orchestrating the enhanced insurance policy assistant.
"""
import logging
import uuid
from typing import Dict, List, Any, Optional

from app.mcp.protocol import MCPRequest, MCPResponse, MCPSession, ToolType, ToolCall, ToolResponse
from app.mcp.tools.intent_detection import IntentDetectionTool
from app.mcp.tools.vector_search import VectorSearchTool
from app.mcp.tools.action_recommender import ActionRecommenderTool
from app.mcp.tools.user_policy import UserPolicyTool
from app.utils.chatbot import ChatbotService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MCPController:
    """Controller for MCP-based interactions."""
    
    def __init__(self):
        """Initialize the MCP controller with tools."""
        self.chatbot_service = ChatbotService()
        self.sessions: Dict[str, MCPSession] = {}
        self.tools = {
            ToolType.INTENT_DETECTION: IntentDetectionTool(),
            ToolType.VECTOR_SEARCH: VectorSearchTool(),
            ToolType.ACTION_RECOMMENDER: ActionRecommenderTool(),
            ToolType.USER_POLICY: UserPolicyTool(),
        }
        logger.info("MCP Controller initialized with tools")
    
    def create_session(self) -> str:
        """Create a new MCP session."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = MCPSession(session_id=session_id)
        return session_id
    
    def process_request(self, request: MCPRequest, session_id: Optional[str] = None) -> MCPResponse:
        """
        Process an MCP request and return a structured response.
        
        Args:
            request: The MCP request to process
            session_id: Optional session ID for maintaining context
            
        Returns:
            Structured MCP response
        """
        # Create or retrieve session
        if not session_id or session_id not in self.sessions:
            session_id = self.create_session()
        
        session = self.sessions[session_id]
        
        # Process tool calls
        tool_results = []
        detected_intent = None
        context_results = []
        
        # If no specific tools were requested, use the action recommender to suggest tools
        if not request.tools:
            action_recommender = self.tools[ToolType.ACTION_RECOMMENDER]
            try:
                recommended_tools = action_recommender.run(request.user_query)
                logger.info(f"Action recommender suggested {len(recommended_tools)} tools")
                # Create tool calls from recommendations
                request.tools = [ToolCall(tool_type=tool["tool_type"], parameters=tool["parameters"]) 
                               for tool in recommended_tools]
            except Exception as e:
                logger.error(f"Error using action recommender: {str(e)}")
        
        # Always run intent detection first
        intent_tool = self.tools[ToolType.INTENT_DETECTION]
        try:
            detected_intent = intent_tool.run(request.user_query)
            # Check if we have a valid list of intents
            if detected_intent and isinstance(detected_intent, list) and len(detected_intent) > 0:
                # Log the top intent
                top_intent = detected_intent[0]
                logger.info(f"Top intent: {top_intent['intent']} with score: {top_intent['score']}")
                
                # Log secondary intents if available
                if len(detected_intent) > 1:
                    secondary_intents = [f"{intent['intent']} ({intent['score']:.2f})" for intent in detected_intent[1:]]
                    logger.info(f"Secondary intents: {', '.join(secondary_intents)}")
            else:
                logger.warning(f"Unexpected intent result type or empty list: {type(detected_intent)}")
                detected_intent = [{"intent": None, "route": None, "score": 0.0}]
        except Exception as e:
            logger.error(f"Error in intent detection: {str(e)}")
            detected_intent = [{"intent": None, "route": None, "score": 0.0}]
        
        # Process explicitly requested tools
        if request.tools:
            for tool_call in request.tools:
                if tool_call.tool_type in self.tools:
                    tool = self.tools[tool_call.tool_type]
                    try:
                        result = tool.run(**tool_call.parameters)
                        tool_results.append(
                            ToolResponse(
                                tool_type=tool_call.tool_type,
                                result=result
                            )
                        )
                    except Exception as e:
                        logger.error(f"Error executing tool {tool_call.tool_type}: {str(e)}")
                        tool_results.append(
                            ToolResponse(
                                tool_type=tool_call.tool_type,
                                result=None,
                                error=str(e)
                            )
                        )
        
        # Always perform vector search to get relevant context
        vector_tool = self.tools[ToolType.VECTOR_SEARCH]
        vector_results = vector_tool.run(query=request.user_query, top_k=3)
        
        if vector_results:
            context_results = vector_results
            
        # Include user policy tool results in context if available
        user_policy_results = None
        user_policy_source_added = False
        for tool_result in tool_results:
            if tool_result.tool_type == ToolType.USER_POLICY and tool_result.result and not tool_result.error:
                user_policy_results = tool_result.result
                
                # Format policy data into context for the LLM
                if isinstance(user_policy_results, dict) and 'result' in user_policy_results:
                    policy_data = user_policy_results['result']
                    if policy_data:
                        # Add policy information to the sources
                        product_name = None
                        if 'policy_details' in policy_data and 'product_name' in policy_data['policy_details']:
                            product_name = policy_data['policy_details']['product_name']
                        
                        # Format the policy data into readable text
                        policy_context = {
                            "source": f"User Policy: {product_name or 'Personal Policy'}",
                            "doc_type": "User Policy Details",
                            "text": self._format_policy_data(policy_data)
                        }
                        # Add to context with high priority (first in list)
                        context_results.insert(0, policy_context)
                        user_policy_source_added = True
                        
        # Generate response using the chatbot service
        chat_history = request.history if request.history else []
        
        # Add intent information to the system prompt
        system_prompt = """You are an insurance policy assistant. Your task is to answer questions about insurance policies based on the provided context.

IMPORTANT: When user policy information is available in the context (marked as "User Policy"), prioritize using that information to answer questions about the user's specific policy. The context will include detailed information about policy details, coverages, and personal information.

Use only the information from the policy documents and user policy data when answering. If the information needed to answer is not available in the context,
state that you don't have enough information to provide an accurate answer rather than making up information.

Do not include citations or references to specific documents in your response as the source information will be displayed separately."""
        
        # Enhance prompt with intents if detected
        if detected_intent and isinstance(detected_intent, list) and len(detected_intent) > 0:
            # Add the primary intent
            primary_intent = detected_intent[0]
            if 'intent' in primary_intent and primary_intent['intent']:
                system_prompt += f"\n\nI detected that the user's primary intent may be: {primary_intent['intent']}. Consider this when providing your response."
            
            # Add secondary intents if available
            if len(detected_intent) > 1:
                secondary_intents = [intent['intent'] for intent in detected_intent[1:] if intent.get('intent')]
                if secondary_intents:
                    system_prompt += f"\n\nAlternative intents to consider: {', '.join(secondary_intents)}."
        
        response_text = self.chatbot_service.generate_response(
            query=request.user_query,
            context=context_results,
            chat_history=chat_history,
            system_prompt=system_prompt
        )
        
        # Extract sources for citation
        sources = []
        for result in context_results:
            source = {
                "name": result.get("source", "Unknown"),
                "type": result.get("doc_type", "Unknown"),
            }
            if source not in sources:
                sources.append(source)
                
        # Add user policy source if we used it
        if user_policy_source_added:
            user_source = {
                "name": "User Policy",
                "type": "Personal Policy Details"
            }
            if user_source not in sources:
                # Add user policy source at the beginning
                sources.insert(0, user_source)
        
        # Update session history
        session.history.append({
            "role": "user",
            "content": request.user_query
        })
        session.history.append({
            "role": "assistant",
            "content": response_text
        })
        
        # Return structured response
        return MCPResponse(
            response=response_text,
            sources=sources,
            tool_results=tool_results,
            detected_intent=detected_intent
        )
        
    def _format_policy_data(self, policy_data: Dict[str, Any]) -> str:
        """
        Format policy data into readable text for the LLM.
        
        Args:
            policy_data: Dictionary containing policy information
            
        Returns:
            Formatted string of policy information
        """
        formatted_text = []
        
        # Add policy details section if available
        if 'policy_details' in policy_data:
            policy_details = policy_data['policy_details']
            formatted_text.append("POLICY DETAILS:")
            for key, value in policy_details.items():
                formatted_key = key.replace('_', ' ').title()
                formatted_text.append(f"- {formatted_key}: {value}")
                
        # Add proposer details section if available
        if 'proposer_details' in policy_data:
            proposer_details = policy_data['proposer_details']
            formatted_text.append("\nPROPOSER DETAILS:")
            for key, value in proposer_details.items():
                formatted_key = key.replace('_', ' ').title()
                formatted_text.append(f"- {formatted_key}: {value}")
                
        # Add insured details section if available
        if 'insured_details' in policy_data:
            insured_details = policy_data['insured_details']
            formatted_text.append("\nINSURED DETAILS:")
            for key, value in insured_details.items():
                formatted_key = key.replace('_', ' ').title()
                formatted_text.append(f"- {formatted_key}: {value}")
                
        # Add coverage details if available
        if 'coverages' in policy_data:
            coverages = policy_data['coverages']
            formatted_text.append("\nCOVERAGES:")
            for coverage in coverages:
                formatted_text.append(f"\n- {coverage.get('cover_name', 'Unknown')}")
                formatted_text.append(f"  Benefits: {coverage.get('benefits', 'Not specified')}")
                formatted_text.append(f"  Sum Insured: {coverage.get('sum_insured', 'Not specified')}")
                formatted_text.append(f"  Deductibles: {coverage.get('deductibles', 'Not specified')}")
                
        return "\n".join(formatted_text)
