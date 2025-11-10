"""Test user document ingestion specifically."""

import asyncio
import sys
from pathlib import Path
import logging

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from pipelines.ingest import get_ingestion_pipeline
from services.vector_db import get_vector_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    pipeline = get_ingestion_pipeline()
    data_dir = Path(__file__).parent.parent / "data" / "Tender_documents"
    
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"Directory exists: {data_dir.exists()}")
    
    if data_dir.exists():
        logger.info(f"Files in directory: {list(data_dir.glob('*.pdf'))}")
        
        # Process as user documents
        logger.info("\nProcessing as USER documents...")
        results = await pipeline.process_directory(str(data_dir), collection_type="user")
        
        logger.info("\nResults:")
        for result in results:
            logger.info(f"  {result}")
        
        # Check database
        vector_db = get_vector_db()
        user_files = vector_db.list_files("user")
        logger.info(f"\nUser documents in database: {len(user_files)}")
        for f in user_files:
            logger.info(f"  - {f['filename']}: {f['chunks_count']} chunks")
        
        vector_db.close()

if __name__ == "__main__":
    asyncio.run(main())
