"""Weaviate vector database service for storing and querying document embeddings."""

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery, Filter
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import base64

from src.config import get_settings

logger = logging.getLogger(__name__)


class WeaviateService:
    """Service for managing document embeddings in Weaviate with dual collections."""
    
    # Two collections: one for checklist templates (read-only), one for user documents
    CHECKLIST_COLLECTION = "ChecklistTemplates"
    USER_DOCUMENT_COLLECTION = "UserDocuments"
    
    def __init__(self):
        """Initialize Weaviate service with lazy connection."""
        logger.info("Initializing Weaviate service (lazy mode)")
        self.client = None
        self._initialized = False
    
    def _connect(self):
        """Establish connection to Weaviate (lazy initialization)."""
        if self._initialized:
            return
            
        logger.info("Connecting to Weaviate...")
        settings = get_settings()
        
        # Connect to Weaviate
        if settings.weaviate_api_key:
            self.client = weaviate.connect_to_weaviate_cloud(
                cluster_url=settings.weaviate_url,
                auth_credentials=weaviate.auth.AuthApiKey(settings.weaviate_api_key),
            )
        else:
            # For local testing without authentication
            url_without_protocol = settings.weaviate_url.replace("http://", "").replace("https://", "")
            if ":" in url_without_protocol:
                host, port = url_without_protocol.split(":", 1)
                self.client = weaviate.connect_to_local(host=host, port=int(port))
            else:
                self.client = weaviate.connect_to_local(host=url_without_protocol)
        
        logger.info("Connected to Weaviate")
        self._initialized = True
    
    def _ensure_collections(self):
        """Create collection schemas if they don't exist."""
        try:
            # Create ChecklistTemplates collection
            if not self.client.collections.exists(self.CHECKLIST_COLLECTION):
                self.client.collections.create(
                    name=self.CHECKLIST_COLLECTION,
                    vectorizer_config=Configure.Vectorizer.none(),
                    properties=[
                        Property(name="content", data_type=DataType.TEXT),
                        Property(name="filename", data_type=DataType.TEXT),
                        Property(name="file_path", data_type=DataType.TEXT),
                        Property(name="chunk_index", data_type=DataType.INT),
                        Property(name="upload_time", data_type=DataType.DATE),
                        Property(name="page_count", data_type=DataType.INT),
                        Property(name="file_size", data_type=DataType.INT),
                        Property(name="pdf_title", data_type=DataType.TEXT),
                        Property(name="pdf_author", data_type=DataType.TEXT),
                        Property(name="pdf_subject", data_type=DataType.TEXT),
                        Property(name="pdf_blob", data_type=DataType.BLOB),  # Store PDF file
                    ]
                )
                logger.info(f"Collection '{self.CHECKLIST_COLLECTION}' created")
            else:
                logger.info(f"Collection '{self.CHECKLIST_COLLECTION}' already exists")
            
            # Create UserDocuments collection
            if not self.client.collections.exists(self.USER_DOCUMENT_COLLECTION):
                self.client.collections.create(
                    name=self.USER_DOCUMENT_COLLECTION,
                    vectorizer_config=Configure.Vectorizer.none(),
                    properties=[
                        Property(name="content", data_type=DataType.TEXT),
                        Property(name="filename", data_type=DataType.TEXT),
                        Property(name="file_path", data_type=DataType.TEXT),
                        Property(name="chunk_index", data_type=DataType.INT),
                        Property(name="upload_time", data_type=DataType.DATE),
                        Property(name="modified_time", data_type=DataType.DATE),
                        Property(name="page_count", data_type=DataType.INT),
                        Property(name="file_size", data_type=DataType.INT),
                        Property(name="pdf_title", data_type=DataType.TEXT),
                        Property(name="pdf_author", data_type=DataType.TEXT),
                        Property(name="pdf_subject", data_type=DataType.TEXT),
                        Property(name="pdf_blob", data_type=DataType.BLOB),  # Store PDF file
                    ]
                )
                logger.info(f"Collection '{self.USER_DOCUMENT_COLLECTION}' created")
            else:
                logger.info(f"Collection '{self.USER_DOCUMENT_COLLECTION}' already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring collections: {str(e)}")
            raise
    
    def upload_pdf_to_weaviate(self, pdf_bytes: bytes, filename: str, collection_type: str = "user") -> str:
        """Upload PDF file to Weaviate object storage.
        
        Args:
            pdf_bytes: PDF file content as bytes
            filename: Name of the PDF file
            collection_type: 'checklist' or 'user'
            
        Returns:
            Base64 encoded blob reference
        """
        logger.info(f"Uploading PDF to Weaviate: {filename} (type: {collection_type})")
        # Encode PDF as base64 for storage
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        logger.info(f"PDF encoded, size: {len(pdf_base64)} characters")
        return pdf_base64
    
    def download_pdf_from_weaviate(self, filename: str, collection_type: str = "user") -> Optional[bytes]:
        """Download PDF file from Weaviate object storage.
        
        Args:
            filename: Name of the PDF file
            collection_type: 'checklist' or 'user'
            
        Returns:
            PDF file content as bytes, or None if not found
        """
        self._connect()
        self._ensure_collections()
        collection_name = self.CHECKLIST_COLLECTION if collection_type == "checklist" else self.USER_DOCUMENT_COLLECTION
        collection = self.client.collections.get(collection_name)
        
        # Query for the file (get first chunk which contains the blob)
        response = collection.query.fetch_objects(
            filters=Filter.by_property("filename").equal(filename) & Filter.by_property("chunk_index").equal(0),
            limit=1
        )
        
        if response.objects:
            pdf_base64 = response.objects[0].properties.get("pdf_blob")
            if pdf_base64:
                return base64.b64decode(pdf_base64)
        
        logger.warning(f"PDF not found: {filename}")
        return None
    
    def add_document_chunks(
        self,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: Dict[str, Any],
        collection_type: str = "user",
        pdf_bytes: Optional[bytes] = None
    ) -> List[str]:
        """Add document chunks with embeddings to Weaviate.
        
        Args:
            chunks: List of text chunks
            embeddings: List of embedding vectors
            metadata: Document metadata
            collection_type: 'checklist' or 'user'
            pdf_bytes: Optional PDF file bytes to store
            
        Returns:
            List of UUIDs for inserted objects
        """
        self._connect()
        self._ensure_collections()
        collection_name = self.CHECKLIST_COLLECTION if collection_type == "checklist" else self.USER_DOCUMENT_COLLECTION
        logger.info(f"Adding {len(chunks)} chunks to {collection_name}: {metadata.get('filename')}")
        
        collection = self.client.collections.get(collection_name)
        
        # Upload PDF if provided (only store in first chunk)
        pdf_base64 = None
        if pdf_bytes:
            pdf_base64 = self.upload_pdf_to_weaviate(pdf_bytes, metadata.get('filename'), collection_type)
        
        # Prepare objects for batch insert
        objects = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            obj = {
                "content": chunk,
                "filename": metadata.get("filename"),
                "file_path": metadata.get("file_path"),
                "chunk_index": i,
                "upload_time": datetime.now().isoformat() + "Z",
                "page_count": metadata.get("page_count"),
                "file_size": metadata.get("file_size"),
                "pdf_title": metadata.get("pdf_metadata", {}).get("title", ""),
                "pdf_author": metadata.get("pdf_metadata", {}).get("author", ""),
                "pdf_subject": metadata.get("pdf_metadata", {}).get("subject", ""),
            }
            
            # Only store PDF blob in first chunk to save space
            if i == 0 and pdf_base64:
                obj["pdf_blob"] = pdf_base64
            
            # Add modified_time for user documents
            if collection_type == "user":
                obj["modified_time"] = metadata.get("modified_time", datetime.now().isoformat() + "Z")
            
            objects.append(obj)
        
        # Batch insert with vectors
        uuids = []
        with collection.batch.dynamic() as batch:
            for obj, embedding in zip(objects, embeddings):
                uuid = batch.add_object(
                    properties=obj,
                    vector=embedding
                )
                uuids.append(uuid)
        
        # Check for batch errors
        if hasattr(batch, 'failed_objects') and batch.failed_objects:
            logger.error(f"Batch insert had {len(batch.failed_objects)} failed objects")
            for failed in batch.failed_objects:
                logger.error(f"Failed object: {failed}")
        
        logger.info(f"Successfully added {len(uuids)} chunks to {collection_name}")
        return uuids
    
    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        filename: Optional[str] = None,
        collection_type: str = "user"
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            filename: Optional filename filter
            collection_type: 'checklist' or 'user'
            
        Returns:
            List of search results with content and metadata
        """
        self._connect()
        self._ensure_collections()
        collection_name = self.CHECKLIST_COLLECTION if collection_type == "checklist" else self.USER_DOCUMENT_COLLECTION
        collection = self.client.collections.get(collection_name)
        
        # Build query
        query_builder = collection.query.near_vector(
            near_vector=query_vector,
            limit=limit,
            return_metadata=MetadataQuery(distance=True)
        )
        
        # Add filename filter if provided
        if filename:
            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                filters=Filter.by_property("filename").equal(filename),
                return_metadata=MetadataQuery(distance=True)
            )
        else:
            response = query_builder
        
        results = []
        for item in response.objects:
            results.append({
                "content": item.properties.get("content"),
                "filename": item.properties.get("filename"),
                "chunk_index": item.properties.get("chunk_index"),
                "upload_time": item.properties.get("upload_time"),
                "distance": item.metadata.distance,
                "metadata": {
                    "file_path": item.properties.get("file_path"),
                    "page_count": item.properties.get("page_count"),
                    "file_size": item.properties.get("file_size"),
                }
            })
        
        return results
    
    def delete_by_filename(self, filename: str, collection_type: str = "user") -> int:
        """Delete all chunks for a specific file.
        
        Args:
            filename: Name of the file to delete
            collection_type: 'checklist' or 'user'
            
        Returns:
            Number of objects deleted
        """
        self._connect()
        self._ensure_collections()
        collection_name = self.CHECKLIST_COLLECTION if collection_type == "checklist" else self.USER_DOCUMENT_COLLECTION
        logger.info(f"Deleting chunks for file: {filename} from {collection_name}")
        
        collection = self.client.collections.get(collection_name)
        result = collection.data.delete_many(
            where=Filter.by_property("filename").equal(filename)
        )
        
        logger.info(f"Deleted {result.successful} chunks for {filename}")
        return result.successful
    
    def get_document_content(self, filename: str, collection_type: str = "user") -> Optional[str]:
        """Get the full content of a document by combining all its chunks.
        
        Args:
            filename: Name of the file to retrieve
            collection_type: 'checklist' or 'user'
            
        Returns:
            Combined content of all chunks, or None if not found
        """
        self._connect()
        self._ensure_collections()
        collection_name = self.CHECKLIST_COLLECTION if collection_type == "checklist" else self.USER_DOCUMENT_COLLECTION
        collection = self.client.collections.get(collection_name)
        
        # Query all chunks for this file, ordered by chunk_index
        response = collection.query.fetch_objects(
            filters=Filter.by_property("filename").equal(filename),
            limit=10000
        )
        
        if not response.objects:
            logger.warning(f"No chunks found for file: {filename}")
            return None
        
        # Sort chunks by chunk_index and combine content
        chunks = sorted(response.objects, key=lambda x: x.properties.get("chunk_index", 0))
        content = "\n\n".join([chunk.properties.get("content", "") for chunk in chunks])
        
        logger.info(f"Retrieved {len(chunks)} chunks for file: {filename}")
        return content
    
    def list_files(self, collection_type: str = "user") -> List[Dict[str, Any]]:
        """List all unique files in the database with their metadata.
        
        Args:
            collection_type: 'checklist' or 'user'
            
        Returns:
            List of file metadata
        """
        self._connect()
        self._ensure_collections()
        collection_name = self.CHECKLIST_COLLECTION if collection_type == "checklist" else self.USER_DOCUMENT_COLLECTION
        collection = self.client.collections.get(collection_name)
        
        # Query all objects
        response = collection.query.fetch_objects(limit=10000)
        
        # Group by filename and get latest metadata
        files_dict = {}
        for item in response.objects:
            filename = item.properties.get("filename")
            if filename not in files_dict:
                files_dict[filename] = {
                    "filename": filename,
                    "file_path": item.properties.get("file_path"),
                    "upload_time": item.properties.get("upload_time"),
                    "page_count": item.properties.get("page_count"),
                    "file_size": item.properties.get("file_size"),
                    "chunks_count": 1,
                }
            else:
                files_dict[filename]["chunks_count"] += 1
        
        return list(files_dict.values())
    
    def clear_all(self, collection_type: str = "user"):
        """Delete all objects from the collection.
        
        Args:
            collection_type: 'checklist' or 'user'
        """
        self._connect()
        self._ensure_collections()
        collection_name = self.CHECKLIST_COLLECTION if collection_type == "checklist" else self.USER_DOCUMENT_COLLECTION
        logger.warning(f"Clearing all data from {collection_name}")
        collection = self.client.collections.get(collection_name)
        collection.data.delete_many(
            where=Filter.by_property("filename").contains_any(["*"])
        )
        logger.info(f"All data cleared from {collection_name}")
    
    def close(self):
        """Close the Weaviate client connection."""
        self.client.close()
        logger.info("Weaviate connection closed")


# Global instance
_vector_db: WeaviateService = None


def get_vector_db() -> WeaviateService:
    """Get or create the global vector database instance.
    
    Returns:
        WeaviateService instance
    """
    global _vector_db
    if _vector_db is None:
        _vector_db = WeaviateService()
    return _vector_db