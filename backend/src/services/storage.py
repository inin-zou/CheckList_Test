"""Storage service for questions, conditions, and checklists"""
import json
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.checklist import (
    Question, Condition, ChecklistTemplate, ChecklistResult
)


class StorageService:
    """Service for storing and retrieving checklist data"""
    
    def __init__(self, storage_path: str = "./data/checklists"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.questions_file = self.storage_path / "questions.json"
        self.conditions_file = self.storage_path / "conditions.json"
        self.templates_file = self.storage_path / "templates.json"
        self.results_file = self.storage_path / "results.json"
        
        # Initialize files if they don't exist
        for file in [self.questions_file, self.conditions_file, 
                     self.templates_file, self.results_file]:
            if not file.exists():
                file.write_text(json.dumps([]))
    
    def _read_json(self, file_path: Path) -> List[Dict]:
        """Read JSON file"""
        try:
            return json.loads(file_path.read_text())
        except Exception:
            return []
    
    def _write_json(self, file_path: Path, data: List[Dict]):
        """Write JSON file"""
        file_path.write_text(json.dumps(data, indent=2, default=str))
    
    # Question operations
    def create_question(self, question: Question) -> Question:
        """Create a new question"""
        questions = self._read_json(self.questions_file)
        
        question.id = str(uuid.uuid4())
        question.created_at = datetime.now()
        question.updated_at = datetime.now()
        
        questions.append(question.model_dump())
        self._write_json(self.questions_file, questions)
        
        return question
    
    def get_question(self, question_id: str) -> Optional[Question]:
        """Get a question by ID"""
        questions = self._read_json(self.questions_file)
        for q in questions:
            if q['id'] == question_id:
                return Question(**q)
        return None
    
    def list_questions(self) -> List[Question]:
        """List all questions"""
        questions = self._read_json(self.questions_file)
        return [Question(**q) for q in questions]
    
    def update_question(self, question_id: str, updates: Dict[str, Any]) -> Optional[Question]:
        """Update a question"""
        questions = self._read_json(self.questions_file)
        
        for i, q in enumerate(questions):
            if q['id'] == question_id:
                q.update(updates)
                q['updated_at'] = datetime.now().isoformat()
                questions[i] = q
                self._write_json(self.questions_file, questions)
                return Question(**q)
        
        return None
    
    def delete_question(self, question_id: str) -> bool:
        """Delete a question"""
        questions = self._read_json(self.questions_file)
        original_len = len(questions)
        questions = [q for q in questions if q['id'] != question_id]
        
        if len(questions) < original_len:
            self._write_json(self.questions_file, questions)
            return True
        return False
    
    # Condition operations
    def create_condition(self, condition: Condition) -> Condition:
        """Create a new condition"""
        conditions = self._read_json(self.conditions_file)
        
        condition.id = str(uuid.uuid4())
        condition.created_at = datetime.now()
        condition.updated_at = datetime.now()
        
        conditions.append(condition.model_dump())
        self._write_json(self.conditions_file, conditions)
        
        return condition
    
    def get_condition(self, condition_id: str) -> Optional[Condition]:
        """Get a condition by ID"""
        conditions = self._read_json(self.conditions_file)
        for c in conditions:
            if c['id'] == condition_id:
                return Condition(**c)
        return None
    
    def list_conditions(self) -> List[Condition]:
        """List all conditions"""
        conditions = self._read_json(self.conditions_file)
        return [Condition(**c) for c in conditions]
    
    def update_condition(self, condition_id: str, updates: Dict[str, Any]) -> Optional[Condition]:
        """Update a condition"""
        conditions = self._read_json(self.conditions_file)
        
        for i, c in enumerate(conditions):
            if c['id'] == condition_id:
                c.update(updates)
                c['updated_at'] = datetime.now().isoformat()
                conditions[i] = c
                self._write_json(self.conditions_file, conditions)
                return Condition(**c)
        
        return None
    
    def delete_condition(self, condition_id: str) -> bool:
        """Delete a condition"""
        conditions = self._read_json(self.conditions_file)
        original_len = len(conditions)
        conditions = [c for c in conditions if c['id'] != condition_id]
        
        if len(conditions) < original_len:
            self._write_json(self.conditions_file, conditions)
            return True
        return False
    
    # Checklist template operations
    def create_template(self, template: ChecklistTemplate) -> ChecklistTemplate:
        """Create a new checklist template"""
        templates = self._read_json(self.templates_file)
        
        template.id = str(uuid.uuid4())
        template.created_at = datetime.now()
        template.updated_at = datetime.now()
        
        templates.append(template.model_dump())
        self._write_json(self.templates_file, templates)
        
        return template
    
    def get_template(self, template_id: str) -> Optional[ChecklistTemplate]:
        """Get a template by ID"""
        templates = self._read_json(self.templates_file)
        for t in templates:
            if t['id'] == template_id:
                return ChecklistTemplate(**t)
        return None
    
    def list_templates(self) -> List[ChecklistTemplate]:
        """List all templates"""
        templates = self._read_json(self.templates_file)
        return [ChecklistTemplate(**t) for t in templates]
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        templates = self._read_json(self.templates_file)
        original_len = len(templates)
        templates = [t for t in templates if t['id'] != template_id]
        
        if len(templates) < original_len:
            self._write_json(self.templates_file, templates)
            return True
        return False
    
    # Checklist result operations
    def save_result(self, result: ChecklistResult) -> ChecklistResult:
        """Save a checklist result"""
        results = self._read_json(self.results_file)
        
        if not result.id:
            result.id = str(uuid.uuid4())
        result.created_at = datetime.now()
        
        results.append(result.model_dump())
        self._write_json(self.results_file, results)
        
        return result
    
    def get_result(self, result_id: str) -> Optional[ChecklistResult]:
        """Get a result by ID"""
        results = self._read_json(self.results_file)
        for r in results:
            if r['id'] == result_id:
                return ChecklistResult(**r)
        return None
    
    def list_results(self, checklist_id: Optional[str] = None) -> List[ChecklistResult]:
        """List all results, optionally filtered by checklist_id"""
        results = self._read_json(self.results_file)
        if checklist_id:
            results = [r for r in results if r.get('checklist_id') == checklist_id]
        return [ChecklistResult(**r) for r in results]


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create storage service singleton"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
