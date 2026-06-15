"""
Test script for Firestore Vector Database operations.
Tests insertion and search functionality using actual Firestore cloud instance.
"""

import os
import sys
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from coach.lib.firestore_vectordb import FirestoreVectorDb
from coach.lib.db import get_firestore_client
from agno.knowledge.document import Document
from agno.knowledge.embedder.google import GeminiEmbedder

@pytest.fixture(scope="module")
def firestore_db():
    """Initialize Firestore Vector DB with credentials from .env"""
    # Load environment variables
    load_dotenv(override=True)
    
    # Get required environment variables
    project_id = os.getenv("AGENT_PROJECT_ID")

    if not project_id:
        pytest.skip("Firebase credentials not found in .env file")
        
    client = get_firestore_client()
    embedder = GeminiEmbedder()
    
    # Initialize the database
    vec_db = FirestoreVectorDb(
        db_client=client,
        collection_name="test_vectors",
        embedder=embedder,
        distance="cosine"
    )
    
    yield vec_db
    
    # Cleanup: Delete test collection after tests
    try:
        # vec_db.delete()
        pass
    except Exception as e:
        print(f"Cleanup warning: {e}")

@pytest.fixture
def sample_documents():
    """Provide sample documents for testing"""
    return [
        Document(
            id="test_doc_1",
            content="This is a test document about machine learning and AI",
            meta_data={
                "title": "Test Document 1",
                "category": "testing",
                "timestamp": "2024-01-01"
            }
        ),
        Document(
            id="test_doc_2",
            content="Another test document discussing neural networks",
            meta_data={
                "title": "Test Document 2",
                "category": "testing",
                "timestamp": "2024-01-02"
            }
        ),
        Document(
            id="test_doc_3",
            content="Production document about deep learning models",
            meta_data={
                "title": "Test Document 3",
                "category": "production",
                "timestamp": "2024-01-03"
            }
        )
    ]


class TestFirestoreVectorDB:
    """Test suite for Firestore Vector Database operations"""
    
    def test_connection(self, firestore_db):
        """Test that connection to Firestore is established"""
        assert firestore_db is not None
        assert firestore_db.collection_name == "test_vectors"
        assert firestore_db.db_client is not None
    
    def test_insert_documents(self, firestore_db, sample_documents):
        """Test inserting documents"""
        content_hash = "test_hash_1"
        
        # Insert documents
        firestore_db.insert(
            content_hash=content_hash,
            documents=sample_documents[:1]
        )
        
        # Verify insertion by checking if ID exists
        assert firestore_db.id_exists(sample_documents[0].id)
    
    def test_upsert_documents(self, firestore_db, sample_documents):
        """Test upserting (insert or update) documents"""
        content_hash = "test_hash_2"
        
        # First upsert
        firestore_db.upsert(
            content_hash=content_hash,
            documents=sample_documents[:1]
        )
        
        # Verify
        assert firestore_db.content_hash_exists(content_hash)
        
        # Second upsert with same hash (should replace)
        modified_doc = Document(
            id=sample_documents[0].id,
            content="Updated content for testing",
            meta_data={"title": "Updated", "category": "testing"}
        )
        
        firestore_db.upsert(
            content_hash=content_hash,
            documents=[modified_doc]
        )
        
        assert firestore_db.content_hash_exists(content_hash)
    
    def test_search_documents(self, firestore_db, sample_documents):
        """Test vector similarity search"""
        # First insert test data
        content_hash = "test_hash_search"
        firestore_db.insert(
            content_hash=content_hash,
            documents=sample_documents
        )
        
        # Search with a query

        # query = "machine learning and artificial intelligence"
        query="search about deep learning models"
        
        results = firestore_db.search(
            query=query,
            limit=2
        )
        
        assert len(results) > 0
        assert len(results) <= 2
        assert all(isinstance(doc, Document) for doc in results)
        assert all(hasattr(doc, 'content') for doc in results)
    
    def test_search_with_filters(self, firestore_db, sample_documents):
        """Test vector search with metadata filters"""
        # Insert test data
        content_hash = "test_hash_filter"
        firestore_db.insert(
            content_hash=content_hash,
            documents=sample_documents
        )
        
        # Search with category filter
        query = "neural networks and deep learning"
        
        results = firestore_db.search(
            query=query,
            limit=5,
            filters={"category": "testing"}
        )
        
        assert len(results) > 0
        # Verify all results match the filter
        for result in results:
            if result.meta_data:
                assert result.meta_data.get("category") == "testing"
    
    def test_id_exists(self, firestore_db, sample_documents):
        """Test checking if document ID exists"""
        # Insert test data
        content_hash = "test_hash_exists"
        doc = sample_documents[0]
        firestore_db.insert(
            content_hash=content_hash,
            documents=[doc]
        )
        
        # Check if ID exists
        assert firestore_db.id_exists(doc.id)
        assert not firestore_db.id_exists("non_existent_id")
    
    def test_name_exists(self, firestore_db, sample_documents):
        """Test checking if document name exists"""
        # Insert test data with name
        content_hash = "test_hash_name"
        doc = Document(
            id="named_doc",
            name="TestName",
            content="Document with a name",
            meta_data={"category": "test"}
        )
        firestore_db.insert(
            content_hash=content_hash,
            documents=[doc]
        )
        
        # Check if name exists
        assert firestore_db.name_exists("TestName")
        assert not firestore_db.name_exists("NonExistentName")
    
    def test_delete_by_id(self, firestore_db, sample_documents):
        """Test deleting a document by ID"""
        # Insert test data
        content_hash = "test_hash_delete"
        doc = sample_documents[0]
        firestore_db.insert(
            content_hash=content_hash,
            documents=[doc]
        )
        
        # Verify insertion
        assert firestore_db.id_exists(doc.id)
        
        # Delete the document
        result = firestore_db.delete_by_id(doc.id)
        
        assert result is True
        
        # Verify deletion
        assert not firestore_db.id_exists(doc.id)
    
    def test_delete_by_metadata(self, firestore_db, sample_documents):
        """Test deleting documents by metadata"""
        # Insert test data
        content_hash = "test_hash_delete_meta"
        firestore_db.insert(
            content_hash=content_hash,
            documents=sample_documents
        )
        
        # Delete by metadata
        result = firestore_db.delete_by_metadata({"category": "testing"})
        
        assert result is True
    
    def test_exists(self, firestore_db, sample_documents):
        """Test checking if collection has any documents"""
        # Collection should exist after previous tests or be empty
        # Insert a document to ensure it exists
        content_hash = "test_hash_collection"
        firestore_db.insert(
            content_hash=content_hash,
            documents=[sample_documents[0]]
        )
        
        assert firestore_db.exists() is True


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

# Made with Bob
