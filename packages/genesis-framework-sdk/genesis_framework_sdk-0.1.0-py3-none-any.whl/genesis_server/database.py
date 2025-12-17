"""
Database module for Genesis Server - Qdrant integration
"""

from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import Optional
import logging

from config import settings

logger = logging.getLogger(__name__)

def get_qdrant_client() -> QdrantClient:
    """
    Create and return a Qdrant client instance based on configuration.
    Automatically creates the 'docs' collection if it doesn't exist.
    """
    try:
        if settings.QDRANT_URL:
            # Use URL if provided
            client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                timeout=10
            )
            print("🔌 Connected to Qdrant via URL")
        else:
            # Use host and port for local connection
            client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY,
                timeout=10
            )
            print("🔌 Connected to Qdrant locally")

        # Check if the collection exists
        if not client.collection_exists(settings.QDRANT_DOCS_COLLECTION):
            print(f"❌ Collection '{settings.QDRANT_DOCS_COLLECTION}' does not exist, creating it...")
            # Create the collection if it doesn't exist
            client.create_collection(
                collection_name=settings.QDRANT_DOCS_COLLECTION,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
            )
            print("✅ Collection created")
        else:
            print(f"✅ Collection '{settings.QDRANT_DOCS_COLLECTION}' already exists")

        logger.info("Successfully connected to Qdrant and ensured collection exists")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        print(f"❌ Failed to connect to Qdrant: {e}")
        raise

def ensure_docs_collection_exists(client: QdrantClient):
    """
    Ensure the docs collection exists in Qdrant with the proper vector configuration.
    """
    try:
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [collection.name for collection in collections.collections]

        if settings.QDRANT_DOCS_COLLECTION not in collection_names:
            # Create the collection for documentation with appropriate vector size
            # Using OpenAI's text-embedding-3-small which has 1536 dimensions
            client.create_collection(
                collection_name=settings.QDRANT_DOCS_COLLECTION,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
            )

            # Create payload index for efficient filtering
            client.create_payload_index(
                collection_name=settings.QDRANT_DOCS_COLLECTION,
                field_name="doc_id",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            client.create_payload_index(
                collection_name=settings.QDRANT_DOCS_COLLECTION,
                field_name="source",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            logger.info(f"Created Qdrant collection: {settings.QDRANT_DOCS_COLLECTION}")
        else:
            logger.info(f"Qdrant collection already exists: {settings.QDRANT_DOCS_COLLECTION}")
    except Exception as e:
        logger.error(f"Failed to ensure docs collection exists: {e}")
        raise