"""
Chatbot service using Google's Generative AI API with Gemini.
"""
import os
import logging
import google.generativeai as genai
from typing import List, Dict, Optional
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ChatbotService:
    """Service for interacting with the Google Gemini model."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the chatbot service.
        
        Args:
            model_name: Name of the Gemini model to use.
                Options include: 
                - "gemini-1.5-flash" (faster, higher quotas)
                - "gemini-1.5-pro" (balanced)
                - "gemini-2.5-pro" (more advanced, lower quotas)
        """
        self.model_name = model_name
        self.api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyB0rrIVGxe8zImM7LtHpvRBCsDf2ybzOyA")
        self._init_client()
    
    def _init_client(self):
        """Initialize the Gemini API connection."""
        try:
            if not self.api_key:
                logger.error("GOOGLE_API_KEY not found in environment variables")
                raise ValueError("GOOGLE_API_KEY is required")
            
            # Configure the Gemini API
            genai.configure(api_key=self.api_key)
            
            # Get available models
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Successfully initialized Gemini model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error initializing Gemini client: {str(e)}")
            raise
    
    def generate_response(
        self, 
        query: str, 
        context: List[Dict] = None, 
        chat_history: List[Dict] = None,
        temperature: float = 0.2,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response to the user query.
        
        Args:
            query: User question.
            context: List of relevant document contexts.
            chat_history: Previous conversation history.
            temperature: Model temperature setting.
            system_prompt: Optional system prompt to guide the model response.
            
        Returns:
            Model's response text.
        """
        try:
            # Prepare system prompt with context
            if context:
                context_text = "\n\n".join([f"{item['text']}" for item in context])
                
                if system_prompt:
                    system_prompt = f"{system_prompt}\n\nRelevant policy information:\n{context_text}"
                else:
                    system_prompt = f"""You are an insurance policy assistant. Your task is to accurately answer questions about insurance policies.
Base your answers only on the provided policy information below. If the information needed to answer is not available in the context,
say that you don't have enough information to provide an accurate answer rather than making up information.
Do not include citations or references to specific documents in your response as the source information will be displayed separately.

Relevant policy information:
{context_text}"""
            elif not system_prompt:
                system_prompt = "You are an insurance policy assistant. Answer the user's question accurately and helpfully."
            
            # Prepare chat history in the expected format
            formatted_history = []
            if chat_history:
                for message in chat_history:
                    role = message.get("role", "user")
                    content = message.get("content", "")
                    # Convert to Gemini's format
                    gemini_role = "user" if role == "user" else "model"
                    formatted_history.append({"role": gemini_role, "parts": [content]})
            
            # Create a chat session if there's history, otherwise we'll use a direct generation
            if formatted_history:
                chat = self.model.start_chat(history=formatted_history)
                
                # Add system instructions to the query
                full_query = f"{system_prompt}\n\nUser query: {query}"
                
                # Send the message and get response
                response = chat.send_message(
                    full_query,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=1024,
                    )
                )
                result = response.text
            else:
                # For first message without history, use direct generation
                prompt_parts = [
                    f"{system_prompt}\n\nUser question: {query}"
                ]
                
                response = self.model.generate_content(
                    prompt_parts,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=1024,
                    )
                )
                result = response.text
            
            # Return the response
            logger.info("Successfully received response from Gemini API")
            return result
                
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"

if __name__ == "__main__":
    # Example usage
    
    # Choose a model variant based on quota needs:
    # - gemini-1.5-flash (fastest, highest quota)
    # - gemini-1.5-pro (balanced performance and quota)
    # - gemini-2.5-pro (most advanced, lower quota)
    
    chatbot = ChatbotService(model_name="gemini-1.5-flash")  # Using flash for higher quota
    
    response = chatbot.generate_response(
        "What does travel insurance typically cover?",
        context=[{
            "source": "travel_insurance.pdf",
            "text": "Travel insurance typically covers medical emergencies, trip cancellations, lost luggage, and travel delays."
        }]
    )
    print(response)
