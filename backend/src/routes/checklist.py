"""Checklist management routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.checklist import (
    Question, Condition, ChecklistTemplate, ChecklistResult,
    CreateQuestionRequest, UpdateQuestionRequest,
    CreateConditionRequest, UpdateConditionRequest,
    CreateChecklistRequest, RunChecklistRequest
)
from ..services.storage import get_storage_service, StorageService
from ..services.claude import get_claude_service, ClaudeService
from ..services.vector_db import get_vector_db
from pathlib import Path

router = APIRouter()


# Question endpoints
@router.post("/questions", response_model=Question)
async def create_question(
    request: CreateQuestionRequest,
    storage: StorageService = Depends(get_storage_service)
):
    """Create a new question"""
    question = Question(
        question=request.question,
        question_type=request.question_type,
        context=request.context,
        options=request.options,
        required=request.required,
        order=request.order
    )
    return storage.create_question(question)


@router.get("/questions", response_model=List[Question])
async def list_questions(storage: StorageService = Depends(get_storage_service)):
    """List all questions"""
    return storage.list_questions()


@router.get("/questions/{question_id}", response_model=Question)
async def get_question(
    question_id: str,
    storage: StorageService = Depends(get_storage_service)
):
    """Get a specific question"""
    question = storage.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.put("/questions/{question_id}", response_model=Question)
async def update_question(
    question_id: str,
    request: UpdateQuestionRequest,
    storage: StorageService = Depends(get_storage_service)
):
    """Update a question"""
    updates = request.model_dump(exclude_unset=True)
    question = storage.update_question(question_id, updates)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: str,
    storage: StorageService = Depends(get_storage_service)
):
    """Delete a question"""
    success = storage.delete_question(question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}


# Condition endpoints
@router.post("/conditions", response_model=Condition)
async def create_condition(
    request: CreateConditionRequest,
    storage: StorageService = Depends(get_storage_service)
):
    """Create a new condition"""
    condition = Condition(
        condition=request.condition,
        condition_type=request.condition_type,
        context=request.context,
        parameters=request.parameters,
        required=request.required,
        order=request.order
    )
    return storage.create_condition(condition)


@router.get("/conditions", response_model=List[Condition])
async def list_conditions(storage: StorageService = Depends(get_storage_service)):
    """List all conditions"""
    return storage.list_conditions()


@router.get("/conditions/{condition_id}", response_model=Condition)
async def get_condition(
    condition_id: str,
    storage: StorageService = Depends(get_storage_service)
):
    """Get a specific condition"""
    condition = storage.get_condition(condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="Condition not found")
    return condition


@router.put("/conditions/{condition_id}", response_model=Condition)
async def update_condition(
    condition_id: str,
    request: UpdateConditionRequest,
    storage: StorageService = Depends(get_storage_service)
):
    """Update a condition"""
    updates = request.model_dump(exclude_unset=True)
    condition = storage.update_condition(condition_id, updates)
    if not condition:
        raise HTTPException(status_code=404, detail="Condition not found")
    return condition


@router.delete("/conditions/{condition_id}")
async def delete_condition(
    condition_id: str,
    storage: StorageService = Depends(get_storage_service)
):
    """Delete a condition"""
    success = storage.delete_condition(condition_id)
    if not success:
        raise HTTPException(status_code=404, detail="Condition not found")
    return {"message": "Condition deleted successfully"}


# Checklist template endpoints
@router.post("/templates", response_model=ChecklistTemplate)
async def create_template(
    request: CreateChecklistRequest,
    storage: StorageService = Depends(get_storage_service)
):
    """Create a new checklist template"""
    # Get questions and conditions
    questions = [storage.get_question(qid) for qid in request.question_ids]
    conditions = [storage.get_condition(cid) for cid in request.condition_ids]
    
    # Filter out None values
    questions = [q for q in questions if q is not None]
    conditions = [c for c in conditions if c is not None]
    
    template = ChecklistTemplate(
        name=request.name,
        description=request.description,
        questions=questions,
        conditions=conditions
    )
    return storage.create_template(template)


@router.get("/templates", response_model=List[ChecklistTemplate])
async def list_templates(storage: StorageService = Depends(get_storage_service)):
    """List all checklist templates"""
    return storage.list_templates()


@router.get("/templates/{template_id}", response_model=ChecklistTemplate)
async def get_template(
    template_id: str,
    storage: StorageService = Depends(get_storage_service)
):
    """Get a specific checklist template"""
    template = storage.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    storage: StorageService = Depends(get_storage_service)
):
    """Delete a checklist template"""
    success = storage.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}


# Checklist execution endpoint
@router.post("/run", response_model=ChecklistResult)
async def run_checklist(
    request: RunChecklistRequest,
    storage: StorageService = Depends(get_storage_service),
    claude: ClaudeService = Depends(get_claude_service),
    vector_db = Depends(get_vector_db)
):
    """Run a checklist against a document"""
    # Get the checklist template
    template = storage.get_template(request.checklist_id)
    if not template:
        raise HTTPException(status_code=404, detail="Checklist template not found")
    
    # Read the document content - skip path check as we'll get content from vector DB
    # The document should already be indexed in the vector database
    
    # Get document content from vector DB by querying all chunks for the file
    try:
        from weaviate.classes.query import Filter
        collection = vector_db.client.collections.get(vector_db.USER_DOCUMENT_COLLECTION)
        
        # Query all chunks for this file, ordered by chunk_index
        response = collection.query.fetch_objects(
            filters=Filter.by_property("filename").equal(request.document_filename),
            limit=1000  # Get all chunks
        )
        
        if not response.objects:
            raise HTTPException(status_code=404, detail=f"Document '{request.document_filename}' not found in database")
        
        # Sort chunks by chunk_index and combine
        chunks_with_index = [(obj.properties.get('chunk_index', 0), obj.properties.get('content', '')) 
                             for obj in response.objects]
        chunks_with_index.sort(key=lambda x: x[0])
        document_content = "\n\n".join([content for _, content in chunks_with_index])
        
        if not document_content:
            raise HTTPException(status_code=400, detail="Could not retrieve document content")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")
    
    # Process questions
    question_dicts = [
        {
            'id': q.id,
            'question': q.question,
            'context': q.context
        }
        for q in template.questions
    ]
    answers = await claude.batch_extract(document_content, question_dicts)
    
    # Process conditions
    condition_dicts = [
        {
            'id': c.id,
            'condition': c.condition,
            'context': c.context
        }
        for c in template.conditions
    ]
    evaluations = await claude.batch_evaluate(document_content, condition_dicts)
    
    # Calculate compliance
    total_conditions = len(evaluations)
    met_conditions = sum(1 for e in evaluations if e.get('is_met', False))
    compliance_percentage = (met_conditions / total_conditions * 100) if total_conditions > 0 else 100.0
    overall_compliance = all(e.get('is_met', False) for e in evaluations)
    
    # Create result
    result = ChecklistResult(
        checklist_id=request.checklist_id,
        checklist_name=template.name,
        document_filename=request.document_filename,
        answers=[
            {
                'question_id': a.get('question_id', ''),
                'question': next((q.question for q in template.questions if q.id == a.get('question_id')), ''),
                'answer': a.get('answer', ''),
                'confidence': a.get('confidence', 'medium'),
                'evidence': a.get('evidence', ''),
                'explanation': a.get('explanation', '')
            }
            for a in answers
        ],
        evaluations=[
            {
                'condition_id': e.get('condition_id', ''),
                'condition': next((c.condition for c in template.conditions if c.id == e.get('condition_id')), ''),
                'is_met': e.get('is_met', False),
                'confidence': e.get('confidence', 'medium'),
                'evidence': e.get('evidence', ''),
                'reasoning': e.get('reasoning', ''),
                'recommendations': e.get('recommendations', '')
            }
            for e in evaluations
        ],
        overall_compliance=overall_compliance,
        compliance_percentage=compliance_percentage
    )
    
    # Save result
    result = storage.save_result(result)
    
    return result


@router.get("/results", response_model=List[ChecklistResult])
async def list_results(
    checklist_id: str = None,
    storage: StorageService = Depends(get_storage_service)
):
    """List checklist results"""
    return storage.list_results(checklist_id)


@router.get("/results/{result_id}", response_model=ChecklistResult)
async def get_result(
    result_id: str,
    storage: StorageService = Depends(get_storage_service)
):
    """Get a specific checklist result"""
    result = storage.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result