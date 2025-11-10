from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Optional
import os
import tempfile
import shutil
import logging

from src.pipelines.ingest import get_ingestion_pipeline
from src.services.vector_db import get_vector_db
from src.services.checklist_generator import get_checklist_generator
from src.services.storage import get_storage_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload/checklist")
async def upload_checklist(file: UploadFile = File(...)):
    """Upload a checklist template PDF
    
    This endpoint handles checklist PDFs that serve as validation templates.
    Files are uploaded to Weaviate object storage and indexed in the ChecklistTemplates collection.
    """
    try:
        # Support both PDF and TXT files for testing
        if not (file.filename.endswith('.pdf') or file.filename.endswith('.txt')):
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
        
        suffix = '.pdf' if file.filename.endswith('.pdf') else '.txt'
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        try:
            # Process the file through the ingestion pipeline
            pipeline = get_ingestion_pipeline()
            result = await pipeline.process_file(temp_path, collection_type="checklist")
            
            if result["status"] == "error":
                raise HTTPException(status_code=500, detail=result["error"])
            
            # Auto-generate checklist template from the uploaded document
            template_id = None
            try:
                # Get document content from vector DB
                vector_db = get_vector_db()
                document_content = await vector_db.get_document_content(
                    collection_name="ChecklistTemplates",
                    filename=file.filename
                )
                
                if document_content:
                    # Generate checklist template using LLM
                    generator = get_checklist_generator()
                    template = await generator.generate_checklist_from_content(
                        document_content=document_content,
                        filename=file.filename
                    )
                    
                    # Save the generated template
                    storage = get_storage_service()
                    saved_template = storage.create_template(template)
                    template_id = saved_template.id
                    
                    logger.info(f"Auto-generated checklist template {template_id} for {file.filename}")
            except Exception as gen_error:
                logger.error(f"Error auto-generating checklist template: {str(gen_error)}")
                # Don't fail the upload if template generation fails
            
            return {
                "status": "success",
                "filename": file.filename,
                "message": "Checklist template uploaded successfully",
                "template_id": template_id,
                "details": {
                    "chunks_count": result.get("chunks_count"),
                    "page_count": result.get("page_count"),
                    "file_size": result.get("file_size"),
                    "pdf_uuid": result.get("pdf_uuid"),
                    "auto_generated_template": template_id is not None
                }
            }
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading checklist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/user")
async def upload_user_document(file: UploadFile = File(...)):
    """Upload a user document PDF
    
    This endpoint handles user-uploaded PDFs that will be validated against checklist templates.
    Files are uploaded to Weaviate object storage and indexed in the UserDocuments collection.
    """
    try:
        # Support both PDF and TXT files for testing
        if not (file.filename.endswith('.pdf') or file.filename.endswith('.txt')):
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
        
        suffix = '.pdf' if file.filename.endswith('.pdf') else '.txt'
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        try:
            # Process the file through the ingestion pipeline
            pipeline = get_ingestion_pipeline()
            result = await pipeline.process_file(temp_path, collection_type="user")
            
            if result["status"] == "error":
                raise HTTPException(status_code=500, detail=result["error"])
            
            return {
                "status": "success",
                "filename": file.filename,
                "message": "User document uploaded successfully",
                "details": {
                    "chunks_count": result.get("chunks_count"),
                    "page_count": result.get("page_count"),
                    "file_size": result.get("file_size"),
                    "pdf_uuid": result.get("pdf_uuid")
                }
            }
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading user document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/checklist")
async def list_checklist_files():
    """List all checklist template files"""
    try:
        vector_db = get_vector_db()
        files = vector_db.list_files(collection_type="checklist")
        return {
            "status": "success",
            "count": len(files),
            "files": files
        }
    except Exception as e:
        logger.error(f"Error listing checklist files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/user")
async def list_user_files():
    """List all user document files"""
    try:
        vector_db = get_vector_db()
        files = vector_db.list_files(collection_type="user")
        return {
            "status": "success",
            "count": len(files),
            "files": files
        }
    except Exception as e:
        logger.error(f"Error listing user files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/checklist/{filename}")
async def delete_checklist_file(filename: str):
    """Delete a checklist template file"""
    try:
        vector_db = get_vector_db()
        vector_db.delete_by_filename(filename, collection_type="checklist")
        return {
            "status": "success",
            "message": f"Checklist file '{filename}' deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting checklist file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/user/{filename}")
async def delete_user_file(filename: str):
    """Delete a user document file"""
    try:
        vector_db = get_vector_db()
        vector_db.delete_by_filename(filename, collection_type="user")
        return {
            "status": "success",
            "message": f"User file '{filename}' deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting user file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{collection_type}/{pdf_uuid}")
async def download_pdf(collection_type: str, pdf_uuid: str):
    """Download a PDF from Weaviate object storage
    
    Args:
        collection_type: 'checklist' or 'user'
        pdf_uuid: UUID of the PDF in Weaviate
    """
    try:
        if collection_type not in ["checklist", "user"]:
            raise HTTPException(status_code=400, detail="Invalid collection type. Must be 'checklist' or 'user'")
        
        vector_db = get_vector_db()
        pdf_bytes = vector_db.download_pdf(pdf_uuid, collection_type)
        
        if pdf_bytes is None:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        from fastapi.responses import Response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={pdf_uuid}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))