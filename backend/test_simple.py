#!/usr/bin/env python3
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipelines.ingest import get_ingestion_pipeline
import asyncio

async def test():
    pipeline = get_ingestion_pipeline()
    print("Testing checklist ingestion...")
    
    # Process tender documents
    tender_dir = "/Users/yongkangzou/Desktop/personal projects/Forgent TechTest/CheckList_Test/data/Tender_documents"
    results = await pipeline.process_directory(tender_dir, collection_type="checklist")
    
    print(f"\nProcessed {len(results)} files:")
    for result in results:
        print(f"  - {result['filename']}: {result['status']}")
        if result['status'] == 'success':
            print(f"    Chunks: {result.get('chunks_count', 0)}")
            print(f"    PDF UUID: {result.get('pdf_uuid', 'N/A')}")
        elif result['status'] == 'error':
            print(f"    Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test())