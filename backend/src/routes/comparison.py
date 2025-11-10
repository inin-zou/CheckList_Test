from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from src.services.comparison import get_comparison_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/compare")
async def compare_documents(
    user_filename: str = Query(..., description="Name of the user document to validate"),
    checklist_filename: str = Query(..., description="Name of the checklist template to compare against"),
    top_k: int = Query(10, description="Number of relevant chunks to retrieve for comparison")
):
    """Compare a user document against a checklist template
    
    This endpoint analyzes whether the user document meets all requirements
    specified in the checklist template, identifying any missing or non-compliant items.
    """
    try:
        comparison_service = get_comparison_service()
        result = await comparison_service.compare_document_with_checklist(
            user_filename=user_filename,
            checklist_filename=checklist_filename,
            top_k=top_k
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report")
async def get_compliance_report(
    user_filename: str = Query(..., description="Name of the user document"),
    checklist_filename: str = Query(..., description="Name of the checklist template")
):
    """Generate a human-readable compliance report
    
    Returns a formatted text report summarizing the compliance status
    of the user document against the checklist template.
    """
    try:
        comparison_service = get_comparison_service()
        report = await comparison_service.get_compliance_report(
            user_filename=user_filename,
            checklist_filename=checklist_filename
        )
        
        return {
            "status": "success",
            "report": report
        }
        
    except Exception as e:
        logger.error(f"Error generating compliance report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))