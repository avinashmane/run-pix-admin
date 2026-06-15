# Firestore Vector Database Test Suite

## Overview
Comprehensive test suite for `src/coach/lib/firestore_vectordb.py` covering storage, retrieval, vector search, and edge cases.

## Test File
`tests/test_firestore_vectordb.py`

## Test Coverage

### 1. Initialization Tests (`TestFirestoreVectorKnowledgeInitialization`)
- **test_initialization_with_valid_params**: Verifies successful initialization with valid collection name and embedding model
- **test_initialization_creates_firestore_client**: Ensures Firestore client is properly instantiated

### 2. Document Insertion Tests (`TestDocumentInsertion`)
- **test_insert_single_document**: Tests inserting a single document with content and metadata
- **test_insert_multiple_documents**: Validates batch insertion of multiple documents
- **test_insert_document_with_empty_metadata**: Handles documents with null/empty metadata
- **test_insert_document_with_complex_metadata**: Tests nested and complex metadata structures
- **test_insert_empty_document_list**: Edge case for empty document list

### 3. Vector Search Tests (`TestVectorSearch`)
- **test_search_returns_documents**: Verifies search returns properly formatted Document objects
- **test_search_with_no_results**: Handles empty search results
- **test_search_uses_cosine_distance**: Confirms COSINE distance measure is used
- **test_search_limit_default**: Validates default limit of 5 results
- **test_search_uses_correct_vector_field**: Ensures "embedding" field is queried
- **test_search_with_missing_text_field**: Handles documents without text field
- **test_search_with_missing_metadata_field**: Handles documents without metadata field

### 4. Collection Operations Tests (`TestCollectionOperations`)
- **test_uses_correct_collection_name**: Verifies correct collection name is used
- **test_different_collection_names**: Tests multiple instances with different collections

### 5. Embedding Generation Tests (`TestEmbeddingGeneration`)
- **test_embedding_called_for_insert**: Confirms embeddings are generated during insert
- **test_embedding_called_for_search**: Confirms embeddings are generated during search
- **test_different_embeddings_for_different_content**: Validates unique embeddings per content

### 6. Error Handling Tests (`TestErrorHandling`)
- **test_insert_with_firestore_error**: Tests Firestore write error handling
- **test_search_with_firestore_error**: Tests Firestore search error handling
- **test_insert_with_embedding_error**: Tests embedding generation error during insert
- **test_search_with_embedding_error**: Tests embedding generation error during search

### 7. Integration Scenarios (`TestIntegrationScenarios`)
- **test_insert_and_search_workflow**: Complete workflow from insert to search
- **test_multiple_searches_same_instance**: Multiple searches on same instance
- **test_batch_insert_operations**: Large batch insertion (100 documents)

## Key Features Tested

### Storage Operations
- ✅ Single document insertion
- ✅ Batch document insertion
- ✅ Document with metadata
- ✅ Document without metadata
- ✅ Complex nested metadata
- ✅ Empty document list handling

### Retrieval Operations
- ✅ Vector similarity search
- ✅ COSINE distance measure
- ✅ Result limit (default: 5)
- ✅ Empty results handling
- ✅ Missing field handling
- ✅ Document formatting

### Vector Search Configuration
- ✅ Query vector generation
- ✅ Vector field name: "embedding"
- ✅ Distance measure: "COSINE"
- ✅ Result limit: 5
- ✅ Proper Document object creation

### Error Scenarios
- ✅ Firestore connection errors
- ✅ Write operation failures
- ✅ Search operation failures
- ✅ Embedding generation failures

## Running the Tests

### Run all tests:
```bash
pytest tests/test_firestore_vectordb.py -v
```

### Run specific test class:
```bash
pytest tests/test_firestore_vectordb.py::TestVectorSearch -v
```

### Run specific test:
```bash
pytest tests/test_firestore_vectordb.py::TestVectorSearch::test_search_returns_documents -v
```

### Run with coverage:
```bash
pytest tests/test_firestore_vectordb.py --cov=src.coach.lib.firestore_vectordb --cov-report=html
```

## Test Fixtures

### `mock_embedding_model`
- Returns consistent 768-dimensional vectors
- Simulates embedding model behavior
- Used across all tests

### `mock_firestore_client`
- Mocks Firestore client operations
- Provides collection and document mocking
- Prevents actual Firestore calls

### `firestore_vector_knowledge`
- Pre-configured FirestoreVectorKnowledge instance
- Uses mocked dependencies
- Ready for testing

## Mocking Strategy

All tests use mocking to:
1. **Avoid external dependencies**: No actual Firestore connection required
2. **Ensure test isolation**: Each test is independent
3. **Speed up execution**: No network calls
4. **Predictable results**: Controlled test data

## Test Data

### Sample Documents
- Simple text content
- Complex metadata structures
- Nested metadata
- Missing fields
- Large batches (100+ documents)

### Sample Embeddings
- 768-dimensional vectors (standard for many models)
- Consistent values for predictability
- Different values for different content

## Expected Behavior

### Insert Operation
1. Generate embedding from content
2. Create Firestore document reference
3. Store: text, embedding, metadata
4. Return success

### Search Operation
1. Generate embedding from query
2. Call Firestore find_nearest with:
   - vector_field: "embedding"
   - query_vector: generated embedding
   - distance_measure: "COSINE"
   - limit: 5
3. Convert results to Document objects
4. Return list of Documents

## Edge Cases Covered

- ✅ Empty document lists
- ✅ Null metadata
- ✅ Missing text fields
- ✅ Missing metadata fields
- ✅ Complex nested structures
- ✅ Large batch operations
- ✅ Multiple searches
- ✅ Error conditions

## Integration with Agno Framework

Tests verify compatibility with:
- `agno.knowledge.document.Document`
- `agno.knowledge.knowledge.Knowledge` (base class)
- Agno embedding models interface

## Future Enhancements

Potential additions:
- [ ] Test different distance measures (EUCLIDEAN, DOT_PRODUCT)
- [ ] Test custom result limits
- [ ] Test pagination
- [ ] Test filtering with metadata
- [ ] Test update operations
- [ ] Test delete operations
- [ ] Performance benchmarks
- [ ] Integration tests with real Firestore

## Notes

- All tests use mocking to avoid external dependencies
- Tests follow AAA pattern (Arrange, Act, Assert)
- Comprehensive coverage of happy paths and error cases
- Tests are independent and can run in any order
- Mock data is realistic and representative

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'src'`, ensure:
- Tests are run from project root
- `conftest.py` adds `./src` to path
- Import paths use `coach.lib.firestore_vectordb` (not `src.coach...`)

### Firestore Client Errors
If tests try to connect to real Firestore:
- Verify mocking is properly applied
- Check patch paths match actual import paths
- Ensure fixtures are used correctly

## Made with Bob