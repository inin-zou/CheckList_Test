"""Service for automatically generating checklist templates from documents"""
from anthropic import Anthropic
from typing import Dict, List, Any
import json
from ..config import get_settings
from ..models.checklist import ChecklistTemplate, Question, Condition
from datetime import datetime
import uuid


class ChecklistGeneratorService:
    """Service for generating checklists from document content using LLM"""
    
    def __init__(self):
        settings = get_settings()
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
    
    async def generate_checklist_from_content(self, 
                                             document_content: str,
                                             filename: str) -> ChecklistTemplate:
        """Generate a checklist template by analyzing document content
        
        Args:
            document_content: The text content extracted from the document
            filename: Name of the source document
            
        Returns:
            ChecklistTemplate with auto-generated questions and conditions
        """
        prompt = f"""Analyze the following document and generate a comprehensive compliance checklist.

Document Content:
{document_content}

Your task is to:
1. Identify key requirements, standards, or criteria mentioned in the document
2. Generate relevant questions to verify compliance with these requirements
3. Create specific conditions that need to be met

Provide your response in the following JSON format:
{{
    "template_name": "A descriptive name for this checklist",
    "description": "Brief description of what this checklist covers",
    "questions": [
        {{
            "question": "The question text",
            "context": "Additional context or explanation for this question",
            "category": "Category name (e.g., 'Safety', 'Quality', 'Documentation')"
        }}
    ],
    "conditions": [
        {{
            "condition": "The condition that must be met",
            "context": "Additional context for this condition",
            "category": "Category name",
            "severity": "critical/high/medium/low"
        }}
    ]
}}

Generate 5-10 questions and 3-8 conditions based on the document content.
Ensure questions are specific, measurable, and directly related to the document.
Conditions should be clear, testable criteria for compliance."""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            # Parse the JSON response
            try:
                parsed_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                    parsed_data = json.loads(response_text)
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                    parsed_data = json.loads(response_text)
                else:
                    raise ValueError("Could not parse LLM response as JSON")
            
            # Create Question objects
            questions = []
            for q_data in parsed_data.get('questions', []):
                question = Question(
                    id=str(uuid.uuid4()),
                    question=q_data['question'],
                    context=q_data.get('context', ''),
                    category=q_data.get('category', 'General'),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                questions.append(question)
            
            # Create Condition objects
            conditions = []
            for c_data in parsed_data.get('conditions', []):
                condition = Condition(
                    id=str(uuid.uuid4()),
                    condition=c_data['condition'],
                    context=c_data.get('context', ''),
                    category=c_data.get('category', 'General'),
                    severity=c_data.get('severity', 'medium'),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                conditions.append(condition)
            
            # Create ChecklistTemplate
            template = ChecklistTemplate(
                id=str(uuid.uuid4()),
                name=parsed_data.get('template_name', f'Checklist for {filename}'),
                description=parsed_data.get('description', f'Auto-generated checklist from {filename}'),
                questions=questions,
                conditions=conditions,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            return template
            
        except Exception as e:
            # Return a minimal template if generation fails
            return ChecklistTemplate(
                id=str(uuid.uuid4()),
                name=f'Failed Generation for {filename}',
                description=f'Error generating checklist: {str(e)}',
                questions=[],
                conditions=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )


# Singleton instance
_generator_service = None

def get_checklist_generator() -> ChecklistGeneratorService:
    """Get or create the checklist generator service instance"""
    global _generator_service
    if _generator_service is None:
        _generator_service = ChecklistGeneratorService()
    return _generator_service
