#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.vector_db import get_vector_db

def check_database():
    print("Connecting to Weaviate...")
    vector_db = get_vector_db()
    
    print("\n=== CHECKLIST TEMPLATES COLLECTION ===")
    checklist_files = vector_db.list_files("checklist")
    print(f"Unique files: {len(checklist_files)}")
    total_chunks = sum(f['chunks_count'] for f in checklist_files)
    print(f"Total chunks: {total_chunks}")
    if checklist_files:
        print("Files:")
        for f in checklist_files:
            print(f"  - {f['filename']}: {f['chunks_count']} chunks")
    
    print("\n=== USER DOCUMENTS COLLECTION ===")
    user_files = vector_db.list_files("user")
    print(f"Unique files: {len(user_files)}")
    total_chunks = sum(f['chunks_count'] for f in user_files)
    print(f"Total chunks: {total_chunks}")
    if user_files:
        print("Files:")
        for f in user_files:
            print(f"  - {f['filename']}: {f['chunks_count']} chunks")
    
    vector_db.close()
    print("\nDatabase check complete!")

if __name__ == "__main__":
    check_database()