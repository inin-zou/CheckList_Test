"""LLM Service for interacting with OpenAI GPT models"""
import logging
from typing import List, Dict, Any, Optional
import openai
from src.config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with OpenAI GPT models"""
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        openai.api_key = self.api_key
    
    async def generate_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate a response using OpenAI GPT
        
        Args:
            prompt: The user prompt
            system_message: Optional system message to set context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise
    
    async def analyze_compliance(
        self,
        checklist_item: str,
        document_context: str
    ) -> Dict[str, Any]:
        """Analyze if a document meets a checklist requirement
        
        Args:
            checklist_item: The checklist requirement to check
            document_context: Relevant document content
            
        Returns:
            Dictionary with compliance status and explanation
        """
        system_message = "You are a compliance expert analyzing documents against requirements."
        
        prompt = f"""Analyze if the following document content meets this requirement:

Requirement: {checklist_item}

Document Content:
{document_context}

Provide a JSON response with:
- "compliant": true/false
- "confidence": 0-1 score
- "explanation": brief explanation
- "evidence": relevant excerpts from document
"""
        
        try:
            response = await self.generate_response(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3
            )
            
            # Parse JSON response
            import json
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Error analyzing compliance: {e}")
            return {
                "compliant": False,
                "confidence": 0.0,
                "explanation": f"Error during analysis: {str(e)}",
                "evidence": []
            }


# Global instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
