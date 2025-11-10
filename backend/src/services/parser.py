"""Document parsing service for extracting text and metadata from PDF files."""

import os
from typing import Dict, List, Any
from datetime import datetime
import fitz  # PyMuPDF
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parser for extracting text and metadata from PDF documents."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the document parser.
        
        Args:
            chunk_size: Maximum size of each text chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse a PDF file and extract text and metadata.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing text content, metadata, and chunks
        """
        logger.info(f"Parsing PDF file: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Open PDF
        doc = fitz.open(file_path)
        
        # Extract text from all pages
        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            full_text += page.get_text()
        
        # Extract metadata
        file_stat = os.stat(file_path)
        metadata = {
            "filename": os.path.basename(file_path),
            "file_path": file_path,
            "file_size": file_stat.st_size,
            "created_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat() + "Z",
            "modified_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat() + "Z",
            "update_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat() + "Z",
            "page_count": len(doc),
            "pdf_metadata": doc.metadata,
        }
        
        # Close document
        doc.close()
        
        # Chunk the text
        chunks = self._chunk_text(full_text)
        
        logger.info(f"Parsed PDF: {metadata['filename']}, Pages: {metadata['page_count']}, Chunks: {len(chunks)}")
        
        return {
            "text": full_text,
            "metadata": metadata,
            "chunks": chunks,
        }
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into overlapping chunks (public method).
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk (uses instance default if not provided)
            overlap: Overlap between chunks (uses instance default if not provided)
            
        Returns:
            List of text chunks
        """
        # Use provided parameters or fall back to instance defaults
        size = chunk_size if chunk_size is not None else self.chunk_size
        overlap_size = overlap if overlap is not None else self.chunk_overlap
        
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + size
            chunk = text[start:end]
            chunks.append(chunk)
            start += size - overlap_size
        
        return chunks
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks (internal method).
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        return self.chunk_text(text)
    
    def parse_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Parse all PDF files in a directory.
        
        Args:
            directory_path: Path to the directory containing PDF files
            
        Returns:
            List of parsed document dictionaries
        """
        logger.info(f"Parsing all PDFs in directory: {directory_path}")
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        results = []
        pdf_files = list(Path(directory_path).rglob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            try:
                result = self.parse_pdf(str(pdf_file))
                results.append(result)
            except Exception as e:
                logger.error(f"Error parsing {pdf_file}: {str(e)}")
                continue
        
        return results


# Global instance
_parser: DocumentParser = None


def get_parser() -> DocumentParser:
    """Get or create the global parser instance.
    
    Returns:
        DocumentParser instance
    """
    global _parser
    if _parser is None:
        _parser = DocumentParser()
    return _parser