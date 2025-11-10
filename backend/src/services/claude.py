"""Claude AI service for document analysis and condition evaluation"""
from anthropic import Anthropic
from typing import Dict, List, Any, Optional
import json
from ..config import get_settings


class ClaudeService:
    """Service for interacting with Claude AI"""
    
    def __init__(self):
        settings = get_settings()
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
    
    async def extract_information(self, 
                                 document_content: str, 
                                 question: str,
                                 context: Optional[str] = None) -> Dict[str, Any]:
        """Extract information from document to answer a question
        
        Args:
            document_content: The content of the document to analyze
            question: The question to answer
            context: Optional context or instructions
            
        Returns:
            Dict containing the answer and confidence level
        """
        prompt = f"""Analyze the following document and answer the question.

Document Content:
{document_content}

Question: {question}

{f'Additional Context: {context}' if context else ''}

Provide your answer in the following JSON format:
{{
    "answer": "your detailed answer here",
    "confidence": "high/medium/low",
    "evidence": "relevant excerpts from the document that support your answer",
    "explanation": "brief explanation of your reasoning"
}}

If the document does not contain enough information to answer the question, set answer to "Information not found" and confidence to "low"."""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the response text
            response_text = message.content[0].text
            
            # Try to parse as JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # If not valid JSON, extract manually
                result = {
                    "answer": response_text,
                    "confidence": "medium",
                    "evidence": "",
                    "explanation": "Response parsing failed"
                }
            
            return result
            
        except Exception as e:
            return {
                "answer": f"Error: {str(e)}",
                "confidence": "low",
                "evidence": "",
                "explanation": "API call failed"
            }
    
    async def evaluate_condition(self,
                               document_content: str,
                               condition: str,
                               context: Optional[str] = None) -> Dict[str, Any]:
        """Evaluate whether a condition is met in the document
        
        Args:
            document_content: The content of the document to analyze
            condition: The condition to evaluate
            context: Optional context or instructions
            
        Returns:
            Dict containing evaluation result and reasoning
        """
        prompt = f"""Analyze the following document and evaluate whether the given condition is met.

Document Content:
{document_content}

Condition to Evaluate: {condition}

{f'Additional Context: {context}' if context else ''}

Provide your evaluation in the following JSON format:
{{
    "is_met": true/false,
    "confidence": "high/medium/low",
    "evidence": "relevant excerpts from the document",
    "reasoning": "detailed explanation of why the condition is or is not met",
    "recommendations": "suggestions if condition is not met (optional)"
}}"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the response text
            response_text = message.content[0].text
            
            # Try to parse as JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # If not valid JSON, return error
                result = {
                    "is_met": False,
                    "confidence": "low",
                    "evidence": "",
                    "reasoning": "Response parsing failed",
                    "recommendations": "Please review manually"
                }
            
            return result
            
        except Exception as e:
            return {
                "is_met": False,
                "confidence": "low",
                "evidence": "",
                "reasoning": f"API call failed: {str(e)}",
                "recommendations": "Please review manually"
            }
    
    async def batch_extract(self,
                          document_content: str,
                          questions: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Extract answers for multiple questions from a document
        
        Args:
            document_content: The content of the document
            questions: List of question dictionaries with 'id', 'question', and optional 'context'
            
        Returns:
            List of answer dictionaries
        """
        results = []
        for q in questions:
            result = await self.extract_information(
                document_content=document_content,
                question=q['question'],
                context=q.get('context')
            )
            result['question_id'] = q.get('id')
            results.append(result)
        return results
    
    async def batch_evaluate(self,
                           document_content: str,
                           conditions: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Evaluate multiple conditions against a document
        
        Args:
            document_content: The content of the document
            conditions: List of condition dictionaries with 'id', 'condition', and optional 'context'
            
        Returns:
            List of evaluation results
        """
        results = []
        for c in conditions:
            result = await self.evaluate_condition(
                document_content=document_content,
                condition=c['condition'],
                context=c.get('context')
            )
            result['condition_id'] = c.get('id')
            results.append(result)
        return results


# Singleton instance
_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    """Get or create Claude service singleton"""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service
