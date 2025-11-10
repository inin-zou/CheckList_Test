"""Data models for checklist, questions, and conditions"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """Types of questions"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    MULTIPLE_CHOICE = "multiple_choice"


class ConditionType(str, Enum):
    """Types of conditions"""
    MUST_CONTAIN = "must_contain"
    MUST_NOT_CONTAIN = "must_not_contain"
    MUST_MATCH = "must_match"
    NUMERIC_COMPARISON = "numeric_comparison"
    DATE_COMPARISON = "date_comparison"
    CUSTOM = "custom"


class Question(BaseModel):
    """Question model"""
    id: Optional[str] = None
    question: str = Field(..., description="The question text")
    question_type: QuestionType = Field(default=QuestionType.TEXT)
    context: Optional[str] = Field(None, description="Additional context or instructions")
    options: Optional[List[str]] = Field(None, description="Options for multiple choice questions")
    required: bool = Field(default=True)
    order: int = Field(default=0, description="Display order")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Condition(BaseModel):
    """Condition model"""
    id: Optional[str] = None
    condition: str = Field(..., description="The condition description")
    condition_type: ConditionType = Field(default=ConditionType.CUSTOM)
    context: Optional[str] = Field(None, description="Additional context")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Condition parameters")
    required: bool = Field(default=True)
    order: int = Field(default=0, description="Display order")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ChecklistTemplate(BaseModel):
    """Checklist template containing questions and conditions"""
    id: Optional[str] = None
    name: str = Field(..., description="Template name")
    description: Optional[str] = None
    questions: List[Question] = Field(default_factory=list)
    conditions: List[Condition] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class QuestionAnswer(BaseModel):
    """Answer to a question"""
    question_id: str
    question: str
    answer: str
    confidence: str = Field(default="medium", description="Confidence level: high/medium/low")
    evidence: Optional[str] = Field(None, description="Supporting evidence from document")
    explanation: Optional[str] = None


class ConditionEvaluation(BaseModel):
    """Evaluation result for a condition"""
    condition_id: str
    condition: str
    is_met: bool
    confidence: str = Field(default="medium")
    evidence: Optional[str] = None
    reasoning: str
    recommendations: Optional[str] = None


class ChecklistResult(BaseModel):
    """Result of running a checklist against a document"""
    id: Optional[str] = None
    checklist_id: str
    checklist_name: str
    document_filename: str
    document_id: Optional[str] = None
    answers: List[QuestionAnswer] = Field(default_factory=list)
    evaluations: List[ConditionEvaluation] = Field(default_factory=list)
    overall_compliance: bool = Field(default=False)
    compliance_percentage: float = Field(default=0.0)
    created_at: Optional[datetime] = None


class CreateQuestionRequest(BaseModel):
    """Request to create a question"""
    question: str
    question_type: QuestionType = QuestionType.TEXT
    context: Optional[str] = None
    options: Optional[List[str]] = None
    required: bool = True
    order: int = 0


class UpdateQuestionRequest(BaseModel):
    """Request to update a question"""
    question: Optional[str] = None
    question_type: Optional[QuestionType] = None
    context: Optional[str] = None
    options: Optional[List[str]] = None
    required: Optional[bool] = None
    order: Optional[int] = None


class CreateConditionRequest(BaseModel):
    """Request to create a condition"""
    condition: str
    condition_type: ConditionType = ConditionType.CUSTOM
    context: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    required: bool = True
    order: int = 0


class UpdateConditionRequest(BaseModel):
    """Request to update a condition"""
    condition: Optional[str] = None
    condition_type: Optional[ConditionType] = None
    context: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    required: Optional[bool] = None
    order: Optional[int] = None


class CreateChecklistRequest(BaseModel):
    """Request to create a checklist"""
    name: str
    description: Optional[str] = None
    question_ids: List[str] = Field(default_factory=list)
    condition_ids: List[str] = Field(default_factory=list)


class RunChecklistRequest(BaseModel):
    """Request to run a checklist against a document"""
    checklist_id: str
    document_filename: str
