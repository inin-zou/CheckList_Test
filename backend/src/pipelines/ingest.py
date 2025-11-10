"""File ingestion pipeline for processing uploaded documents"""

from typing import List, Dict, Any
import logging
import os
from pathlib import Path

from src.services.parser import DocumentParser
from src.services.embeddings import get_embedding_service
from src.services.vector_db import get_vector_db

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Pipeline for ingesting and processing documents"""
    
    def __init__(self):
        """Initialize the ingestion pipeline with lazy loading of services."""
        logger.info("Initializing ingestion pipeline (lazy loading enabled)")
        self._parser = None
        self._embedding_service = None
        self._vector_db = None
        logger.info("Ingestion pipeline initialized")
    
    @property
    def parser(self):
        """Lazy load document parser."""
        if self._parser is None:
            logger.info("Loading document parser")
            self._parser = DocumentParser()
        return self._parser
    
    @property
    def embedding_service(self):
        """Lazy load embedding service."""
        if self._embedding_service is None:
            logger.info("Loading embedding service")
            self._embedding_service = get_embedding_service()
        return self._embedding_service
    
    @property
    def vector_db(self):
        """Lazy load vector database."""
        if self._vector_db is None:
            logger.info("Loading vector database")
            self._vector_db = get_vector_db()
        return self._vector_db
    
    async def process_file(self, file_path: str, collection_type: str = "user") -> Dict[str, Any]:
        """Process a single PDF file through the ingestion pipeline.
        
        Steps:
        1. Upload PDF to Weaviate object storage
        2. Parse PDF and extract text with metadata
        3. Split text into chunks
        4. Generate embeddings for each chunk
        5. Store chunks and embeddings in Weaviate (referencing cloud PDF)
        
        Args:
            file_path: Path to the PDF file
            collection_type: 'checklist' or 'user' - determines which collection to use
            
        Returns:
            Dictionary with processing status and metadata
        """
        try:
            logger.info(f"Processing file: {file_path} for collection type: {collection_type}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Step 1: Upload PDF to Weaviate object storage
            logger.info("Step 1: Uploading PDF to Weaviate object storage")
            filename = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            pdf_uuid = self.vector_db.upload_pdf_to_weaviate(pdf_bytes, filename, collection_type)
            logger.info(f"PDF uploaded with UUID: {pdf_uuid}")
            
            # Step 2: Parse PDF
            logger.info("Step 2: Parsing PDF")
            parsed_data = self.parser.parse_pdf(file_path)
            text = parsed_data["text"]
            metadata = parsed_data["metadata"]
            
            if not text.strip():
                logger.warning(f"No text extracted from {file_path}")
                return {
                    "status": "warning",
                    "message": "No text content found in PDF",
                    "file_path": file_path,
                    "filename": metadata["filename"],
                    "pdf_uuid": pdf_uuid,
                    "collection_type": collection_type
                }
            
            # Step 3: Split into chunks
            logger.info("Step 3: Splitting text into chunks")
            chunks = self.parser.chunk_text(text, chunk_size=1000, overlap=200)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Step 4: Generate embeddings
            logger.info("Step 4: Generating embeddings")
            embeddings = self.embedding_service.encode_batch(chunks)
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # Step 5: Store in Weaviate with reference to cloud PDF
            logger.info("Step 5: Storing chunks in Weaviate")
            # Delete existing chunks for this file first
            self.vector_db.delete_by_filename(metadata["filename"], collection_type)
            
            # Add new chunks with reference to the uploaded PDF
            metadata["pdf_uuid"] = pdf_uuid  # Reference to cloud PDF
            uuids = self.vector_db.add_document_chunks(
                chunks=chunks,
                embeddings=embeddings,
                metadata=metadata,
                collection_type=collection_type
            )
            
            logger.info(f"Successfully processed file: {file_path}")
            return {
                "status": "success",
                "file_path": file_path,
                "filename": metadata["filename"],
                "chunks_count": len(chunks),
                "upload_time": metadata["update_time"],
                "page_count": metadata["page_count"],
                "file_size": metadata["file_size"],
                "pdf_uuid": pdf_uuid,
                "chunk_uuids": uuids,
                "collection_type": collection_type
            }
            
        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Error processing file {file_path}: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "file_path": file_path,
                "error": error_msg,
                "collection_type": collection_type
            }
    
    async def process_batch(self, file_paths: List[str], collection_type: str = "user") -> List[Dict[str, Any]]:
        """Process multiple files in batch.
        
        Args:
            file_paths: List of file paths to process
            collection_type: 'checklist' or 'user'
            
        Returns:
            List of processing results for each file
        """
        logger.info(f"Processing batch of {len(file_paths)} files for collection type: {collection_type}")
        results = []
        
        for file_path in file_paths:
            result = await self.process_file(file_path, collection_type)
            results.append(result)
        
        # Summary statistics
        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = sum(1 for r in results if r["status"] == "error")
        warning_count = sum(1 for r in results if r["status"] == "warning")
        
        logger.info(f"Batch processing complete: {success_count} succeeded, {error_count} failed, {warning_count} warnings")
        
        return results
    
    async def process_directory(self, directory_path: str, collection_type: str = "user") -> List[Dict[str, Any]]:
        """Process all PDF files in a directory.
        
        Args:
            directory_path: Path to the directory containing PDF files
            collection_type: 'checklist' or 'user'
            
        Returns:
            List of processing results for each file
        """
        logger.info(f"Processing directory: {directory_path} for collection type: {collection_type}")
        
        # Find all PDF files
        pdf_files = self.parser.parse_directory(directory_path)
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return []
        
        # Extract file paths
        file_paths = [pdf["metadata"]["file_path"] for pdf in pdf_files]
        
        # Process batch
        return await self.process_batch(file_paths, collection_type)


# Global instance
_pipeline: IngestionPipeline = None


def get_ingestion_pipeline() -> IngestionPipeline:
    """Get or create the global ingestion pipeline instance.
    
    Returns:
        IngestionPipeline instance
    """
    global _pipeline
    if _pipeline is None:
        _pipeline = IngestionPipeline()
    return _pipeline