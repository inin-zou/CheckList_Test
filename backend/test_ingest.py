"""Test script for document ingestion pipeline with dual-collection architecture."""

import asyncio
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from pipelines.ingest import get_ingestion_pipeline
from services.vector_db import get_vector_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_checklist_ingestion():
    """Test checklist template ingestion."""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING CHECKLIST TEMPLATE INGESTION")
    logger.info("=" * 80)
    
    pipeline = get_ingestion_pipeline()
    data_dir = Path(__file__).parent.parent / "data" / "Tender_documents"
    
    if not data_dir.exists():
        logger.error(f"Directory does not exist: {data_dir}")
        return
    
    # Process as checklist templates
    logger.info(f"Processing PDFs from {data_dir} as checklist templates...")
    results = await pipeline.process_directory(str(data_dir), collection_type="checklist")
    
    logger.info("\nChecklist ingestion results:")
    for i, result in enumerate(results, 1):
        logger.info(f"\n  File {i}:")
        logger.info(f"    Status: {result['status']}")
        if result['status'] == 'success':
            logger.info(f"    Filename: {result.get('filename')}")
            logger.info(f"    Chunks: {result.get('chunks_count')}")
            logger.info(f"    PDF UUID: {result.get('pdf_uuid')}")
            logger.info(f"    Page Count: {result.get('page_count')}")
        elif result['status'] == 'error':
            logger.error(f"    Error: {result.get('error')}")
    
    return results


async def test_user_document_ingestion():
    """Test user document ingestion."""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING USER DOCUMENT INGESTION")
    logger.info("=" * 80)
    
    pipeline = get_ingestion_pipeline()
    data_dir = Path(__file__).parent.parent / "data" / "Tender_documents"
    
    if not data_dir.exists():
        logger.error(f"Directory does not exist: {data_dir}")
        return
    
    # Process as user documents
    logger.info(f"Processing PDFs from {data_dir} as user documents...")
    results = await pipeline.process_directory(str(data_dir), collection_type="user")
    
    logger.info("\nUser document ingestion results:")
    for i, result in enumerate(results, 1):
        logger.info(f"\n  File {i}:")
        logger.info(f"    Status: {result['status']}")
        if result['status'] == 'success':
            logger.info(f"    Filename: {result.get('filename')}")
            logger.info(f"    Chunks: {result.get('chunks_count')}")
            logger.info(f"    PDF UUID: {result.get('pdf_uuid')}")
            logger.info(f"    Page Count: {result.get('page_count')}")
        elif result['status'] == 'error':
            logger.error(f"    Error: {result.get('error')}")
    
    return results


async def test_vector_db_statistics():
    """Test vector database statistics for both collections."""
    logger.info("\n" + "=" * 80)
    logger.info("VECTOR DATABASE STATISTICS")
    logger.info("=" * 80)
    
    vector_db = get_vector_db()
    
    # Check checklist collection
    logger.info("\nChecklist Templates Collection:")
    checklist_files = vector_db.list_files(collection_type="checklist")
    logger.info(f"  Total files: {len(checklist_files)}")
    for file_info in checklist_files:
        logger.info(f"\n    File: {file_info['filename']}")
        logger.info(f"      Chunks: {file_info['chunks_count']}")
        logger.info(f"      PDF UUID: {file_info.get('pdf_uuid', 'N/A')}")
        logger.info(f"      Page Count: {file_info.get('page_count', 'N/A')}")
    
    # Check user documents collection
    logger.info("\nUser Documents Collection:")
    user_files = vector_db.list_files(collection_type="user")
    logger.info(f"  Total files: {len(user_files)}")
    for file_info in user_files:
        logger.info(f"\n    File: {file_info['filename']}")
        logger.info(f"      Chunks: {file_info['chunks_count']}")
        logger.info(f"      PDF UUID: {file_info.get('pdf_uuid', 'N/A')}")
        logger.info(f"      Page Count: {file_info.get('page_count', 'N/A')}")


async def main():
    """Main test function."""
    try:
        logger.info("=" * 80)
        logger.info("DUAL-COLLECTION ARCHITECTURE TEST")
        logger.info("=" * 80)
        
        # Test checklist ingestion
        await test_checklist_ingestion()
        
        # Test user document ingestion
        await test_user_document_ingestion()
        
        # Display statistics
        await test_vector_db_statistics()
        
        logger.info("\n" + "=" * 80)
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        try:
            vector_db = get_vector_db()
            vector_db.close()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())