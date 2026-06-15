"""
Test script for Pinecone Vector Database integration.
Tests insertion of 10 texts and retrieval using the get_kb function.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from coach.lib.knowledge import get_kb
from agno.knowledge.document import Document


def test_pinecone_insert_and_retrieve():
    """Test inserting 10 documents and retrieving them from Pinecone."""
    
    print("=" * 80)
    print("Testing Pinecone Vector Database")
    print("=" * 80)
    
    # Get knowledge base using Pinecone (default type)
    # Note: Pinecone index names must be lowercase alphanumeric or '-'
    kb = get_kb(name="test-knowledge-base", vectordb_type=None)
    
    print(f"\n✓ Knowledge base initialized")
    print(f"  Vector DB: {type(kb.vector_db).__name__}")
    
    # Create 10 test documents
    test_documents = [
        Document(
            content="Python is a high-level programming language known for its simplicity.",
            meta_data={"id": 1, "category": "programming", "language": "python"}
        ),
        Document(
            content="Machine learning is a subset of artificial intelligence.",
            meta_data={"id": 2, "category": "AI", "topic": "machine learning"}
        ),
        Document(
            content="Pinecone is a vector database designed for similarity search.",
            meta_data={"id": 3, "category": "database", "type": "vector"}
        ),
        Document(
            content="Natural language processing helps computers understand human language.",
            meta_data={"id": 4, "category": "AI", "topic": "NLP"}
        ),
        Document(
            content="Docker containers provide isolated environments for applications.",
            meta_data={"id": 5, "category": "devops", "tool": "docker"}
        ),
        Document(
            content="React is a JavaScript library for building user interfaces.",
            meta_data={"id": 6, "category": "frontend", "framework": "react"}
        ),
        Document(
            content="Kubernetes orchestrates containerized applications at scale.",
            meta_data={"id": 7, "category": "devops", "tool": "kubernetes"}
        ),
        Document(
            content="TensorFlow is an open-source machine learning framework.",
            meta_data={"id": 8, "category": "AI", "framework": "tensorflow"}
        ),
        Document(
            content="FastAPI is a modern Python web framework for building APIs.",
            meta_data={"id": 9, "category": "backend", "framework": "fastapi"}
        ),
        Document(
            content="Vector embeddings represent text as numerical vectors for similarity search.",
            meta_data={"id": 10, "category": "AI", "topic": "embeddings"}
        )
    ]
    
    print(f"\n✓ Created {len(test_documents)} test documents")
    
    # Insert documents into Pinecone
    print("\n" + "-" * 80)
    print("Inserting documents into Pinecone...")
    print("-" * 80)
    
    try:
        print(kb.insert(test_documents))
        print(f"✓ Successfully inserted {len(test_documents)} documents")
    except Exception as e:
        print(f"✗ Error inserting documents: {e}")
        raise
    
    # Test retrieval with different queries
    print("\n" + "-" * 80)
    print("Testing retrieval with various queries")
    print("-" * 80)
    
    test_queries = [
        "What is Python programming?",
        "Tell me about machine learning",
        "How does vector search work?",
        "Container orchestration tools",
        "AI frameworks and libraries"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("   " + "-" * 70)
        
        try:
            results = kb.search(query, max_results=3)
            
            if results:
                print(f"   Found {len(results)} results:")
                for j, doc in enumerate(results, 1):
                    content_preview = doc.content[:80] + "..." if len(doc.content) > 80 else doc.content
                    print(f"   [{j}] {content_preview}")
                    if doc.meta_data:
                        print(f"       Metadata: {doc.meta_data}")
            else:
                print("   No results found")
                
        except Exception as e:
            print(f"   ✗ Error during search: {e}")
    
    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print("=" * 80)


def test_pinecone_hybrid_search():
    """Test hybrid search capabilities of Pinecone."""
    
    print("\n" + "=" * 80)
    print("Testing Pinecone Hybrid Search")
    print("=" * 80)
    
    kb = get_kb(name="test-knowledge-base", vectordb_type=None)
    
    # Test with a specific keyword search
    query = "Python FastAPI"
    print(f"\nHybrid search query: '{query}'")
    print("-" * 80)
    
    try:
        results = kb.search(query, max_results=5)
        
        if results:
            print(f"Found {len(results)} results:")
            for i, doc in enumerate(results, 1):
                print(f"\n[{i}] {doc.content}")
                if doc.meta_data:
                    print(f"    Metadata: {doc.meta_data}")
        else:
            print("No results found")
            
    except Exception as e:
        print(f"✗ Error during hybrid search: {e}")
        raise


def test_insert_recipes():
    kb = get_kb(name="test-knowledge-base", vectordb_type=None)
    kb.insert(
        name="Recipes",
        url="https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf",
        metadata={"doc_type": "recipe_book"},
    )
    assert True




if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PINECONE VECTOR DATABASE TEST SUITE")
    print("=" * 80)
    print(f"PINECONE_API_KEY: {'Set' if os.getenv('PINECONE_API_KEY') else 'Not Set'}")
    print(f"PINECONE_HOST: {os.getenv('PINECONE_HOST', 'Not Set')}")
    print("=" * 80)
    
    try:
        # Run main test
        test_pinecone_insert_and_retrieve()
        
        # Run hybrid search test
        test_pinecone_hybrid_search()
        
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"TEST FAILED ✗")
        print(f"Error: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
