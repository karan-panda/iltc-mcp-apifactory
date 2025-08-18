"""
Structured prompts for MCP.
"""
from typing import Dict

from app.mcp.protocol import MCPPrompt


class PromptLibrary:
    """Library of structured prompts for different scenarios."""
    
    @staticmethod
    def get_prompts() -> Dict[str, MCPPrompt]:
        """Get all available prompts."""
        return {
            "default": PromptLibrary.default_prompt(),
            "policy_query": PromptLibrary.policy_query_prompt(),
            "intent_detected": PromptLibrary.intent_detected_prompt(),
            "insufficient_info": PromptLibrary.insufficient_info_prompt(),
            "comparison": PromptLibrary.policy_comparison_prompt(),
        }
    


    @staticmethod
    def default_prompt() -> MCPPrompt:
        """Default prompt for general queries."""
        return MCPPrompt(
            template="""You are an insurance policy assistant. Answer the following question accurately and helpfully.
            
Question: {question}

Use only the information from the provided context to answer:
{context}

Do not include citations or references to specific documents in your response as the source information will be displayed separately."""
        )
    



    @staticmethod
    def policy_query_prompt() -> MCPPrompt:
        """Prompt for specific policy queries."""
        return MCPPrompt(
            template="""You are an insurance policy assistant. Your task is to answer questions about insurance policies based on the provided context.

Answer the following question about {policy_type} insurance:

Question: {question}

Use only the information from these policy documents:
{context}

If the information needed to answer is not available in the context, state that you don't have enough information to provide an accurate answer rather than making up information.

Do not include citations or references to specific documents in your response as the source information will be displayed separately."""
        )
    





    @staticmethod
    def intent_detected_prompt() -> MCPPrompt:
        """Prompt for when a specific intent is detected."""
        return MCPPrompt(
            template="""You are an insurance policy assistant. I've detected that the user is interested in {intent}.

Question: {question}

Based on this intent and the following policy information:
{context}

Provide a helpful response that addresses their specific intent. If they appear to be interested in purchasing a policy or learning about specific coverage, highlight the most relevant details.

If the information needed to answer is not available in the context, state that you don't have enough information to provide an accurate answer rather than making up information.

Do not include citations or references to specific documents in your response as the source information will be displayed separately."""
        )
    





    @staticmethod
    def insufficient_info_prompt() -> MCPPrompt:
        """Prompt for when there isn't enough context to answer."""
        return MCPPrompt(
            template="""You are an insurance policy assistant. The user has asked:

Question: {question}

I don't have enough specific information in the policy documents to provide a complete answer to this question. Based on the limited information I have:
{context}

Provide a helpful response that:
1. Acknowledges the limitations of the available information
2. Provides any partial information that might be helpful
3. Suggests what additional information might be needed
4. Offers alternative ways the user might get the information they need (e.g., calling customer service - 1800 2666)

Do not include citations or references to specific documents in your response as the source information will be displayed separately."""
        )
    





    @staticmethod
    def policy_comparison_prompt() -> MCPPrompt:
        """Prompt for comparing different policies."""
        return MCPPrompt(
            template="""You are an insurance policy assistant. The user wants to compare different policies.

Question: {question}

Based on these policy documents:
{context}

Create a helpful comparison that highlights:
1. Key differences between the policies
2. Unique benefits of each policy
3. Coverage limitations for each policy
4. Price considerations if available

Present this information in a clear, structured way that helps the user make an informed decision.

Do not include citations or references to specific documents in your response as the source information will be displayed separately."""
        )
