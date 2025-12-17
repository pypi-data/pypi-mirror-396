"""
Integration Tests for Qdrant Vector Database with Live Server

These tests require a running Qdrant instance.

SETUP INSTRUCTIONS:
-------------------
1. Start a local Qdrant instance using Docker:
   docker run -p 6333:6333 qdrant/qdrant

2. Or use Qdrant Cloud:
   - Set environment variables: QDRANT_URL, QDRANT_PORT, QDRANT_API_KEY

3. Run tests:
   pytest tests/test_qdrant_integration_live.py -v

SKIP TESTS:
-----------
Set environment variable SKIP_LIVE_TESTS=1 to skip these tests:
   SKIP_LIVE_TESTS=1 pytest tests/test_qdrant_integration_live.py

Test Coverage:
- Real connection to Qdrant server
- Full CRUD operations with actual data persistence
- Search accuracy validation
- Performance benchmarks
- Error recovery scenarios
"""

import pytest
import numpy as np
import os
import time
from typing import List, Tuple

from SimplerLLM.vectors.qdrant_vector_db import QdrantVectorDB
from SimplerLLM.vectors.vector_providers import VectorProvider


# Check if live tests should be skipped
SKIP_LIVE_TESTS = os.getenv('SKIP_LIVE_TESTS', '0') == '1'
skip_if_no_server = pytest.mark.skipif(
    SKIP_LIVE_TESTS,
    reason="Live Qdrant server tests are disabled. Set SKIP_LIVE_TESTS=0 to enable."
)


def get_qdrant_config():
    """Get Qdrant configuration from environment or defaults"""
    return {
        'url': os.getenv('QDRANT_URL', 'localhost'),
        'port': int(os.getenv('QDRANT_PORT', '6333')),
        'api_key': os.getenv('QDRANT_API_KEY', None),
    }


@pytest.fixture
def live_vector_db():
    """Create a live QdrantVectorDB instance for testing"""
    config = get_qdrant_config()

    db = QdrantVectorDB(
        provider=VectorProvider.QDRANT,
        collection_name='test_live_collection',
        dimension=128,
        **config
    )

    yield db

    # Cleanup: delete test collection
    try:
        db.clear_database()
    except:
        pass


@pytest.fixture
def sample_vectors():
    """Generate sample vectors for testing"""
    np.random.seed(42)  # For reproducibility

    vectors_with_meta = []
    for i in range(10):
        vector = np.random.rand(128).astype(np.float32)
        metadata = {
            "text": f"Document {i}",
            "category": "A" if i % 2 == 0 else "B",
            "id": i,
            "score": i * 10.5
        }
        vectors_with_meta.append((vector, metadata))

    return vectors_with_meta


# ============================================================================
# CONNECTION TESTS
# ============================================================================

@skip_if_no_server
class TestLiveConnection:
    """Test actual connection to Qdrant server"""

    def test_successful_connection(self):
        """Test that we can connect to Qdrant server"""
        config = get_qdrant_config()

        db = QdrantVectorDB(
            provider=VectorProvider.QDRANT,
            collection_name='connection_test',
            dimension=128,
            **config
        )

        assert db.client is not None

        # Cleanup
        try:
            db.clear_database()
        except:
            pass

    def test_collection_creation(self, live_vector_db):
        """Test that collection is created successfully"""
        stats = live_vector_db.get_stats()

        assert stats['collection_name'] == 'test_live_collection'
        assert stats['dimension'] == 128
        assert stats['status'] in ['green', 'yellow']  # Yellow during initialization

    def test_invalid_credentials(self):
        """Test connection with invalid credentials"""
        if os.getenv('QDRANT_API_KEY'):
            # Only test if we're using API key authentication
            with pytest.raises(Exception):
                db = QdrantVectorDB(
                    provider=VectorProvider.QDRANT,
                    url='https://invalid.qdrant.cloud',
                    port=443,
                    api_key='invalid_key_123',
                    collection_name='test',
                    dimension=128
                )
                # Try to perform an operation
                db.get_vector_count()


# ============================================================================
# CRUD OPERATION TESTS
# ============================================================================

@skip_if_no_server
class TestLiveCRUDOperations:
    """Test CRUD operations with live server"""

    def test_add_single_vector(self, live_vector_db):
        """Test adding a single vector to live server"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = {"text": "test document", "category": "test"}

        vector_id = live_vector_db.add_vector(vector, metadata, normalize=True)

        assert vector_id is not None

        # Verify it was added
        count = live_vector_db.get_vector_count()
        assert count >= 1

    def test_add_and_retrieve_vector(self, live_vector_db):
        """Test adding and retrieving the same vector"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = {"text": "retrieve test", "id": 999}

        # Add
        vector_id = live_vector_db.add_vector(vector, metadata, normalize=False)

        # Small delay for indexing
        time.sleep(0.1)

        # Retrieve
        result = live_vector_db.get_vector_by_id(vector_id)

        assert result is not None
        retrieved_vector, retrieved_metadata = result
        assert np.allclose(retrieved_vector, vector, atol=1e-5)
        assert retrieved_metadata["text"] == "retrieve test"
        assert retrieved_metadata["id"] == 999

    def test_batch_insertion(self, live_vector_db, sample_vectors):
        """Test batch insertion of vectors"""
        ids = live_vector_db.add_vectors_batch(sample_vectors[:5], normalize=True)

        assert len(ids) == 5

        # Verify count
        time.sleep(0.1)
        count = live_vector_db.get_vector_count()
        assert count >= 5

    def test_update_vector_data(self, live_vector_db):
        """Test updating vector data on live server"""
        # Add original
        original_vector = np.array([1.0] * 128, dtype=np.float32)
        metadata = {"version": 1}
        vector_id = live_vector_db.add_vector(original_vector, metadata, normalize=False)

        time.sleep(0.1)

        # Update vector
        new_vector = np.array([2.0] * 128, dtype=np.float32)
        result = live_vector_db.update_vector(vector_id, new_vector=new_vector, normalize=False)

        assert result is True

        time.sleep(0.1)

        # Verify update
        retrieved = live_vector_db.get_vector_by_id(vector_id)
        assert retrieved is not None
        updated_vector, _ = retrieved
        assert np.allclose(updated_vector, new_vector, atol=1e-5)

    def test_update_metadata(self, live_vector_db):
        """Test updating only metadata"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = {"text": "original", "version": 1}

        vector_id = live_vector_db.add_vector(vector, metadata)
        time.sleep(0.1)

        # Update metadata
        new_metadata = {"text": "updated", "version": 2, "modified": True}
        result = live_vector_db.update_vector(vector_id, new_metadata=new_metadata)

        assert result is True
        time.sleep(0.1)

        # Verify
        retrieved = live_vector_db.get_vector_by_id(vector_id)
        _, retrieved_metadata = retrieved
        assert retrieved_metadata["text"] == "updated"
        assert retrieved_metadata["version"] == 2
        assert retrieved_metadata["modified"] is True

    def test_delete_vector(self, live_vector_db):
        """Test deleting a vector"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = {"text": "to be deleted"}

        vector_id = live_vector_db.add_vector(vector, metadata)
        time.sleep(0.1)

        # Verify it exists
        result = live_vector_db.get_vector_by_id(vector_id)
        assert result is not None

        # Delete
        delete_result = live_vector_db.delete_vector(vector_id)
        assert delete_result is True

        time.sleep(0.1)

        # Verify it's gone
        result = live_vector_db.get_vector_by_id(vector_id)
        assert result is None


# ============================================================================
# SEARCH OPERATION TESTS
# ============================================================================

@skip_if_no_server
class TestLiveSearchOperations:
    """Test search operations with live server"""

    def test_cosine_similarity_search(self, live_vector_db):
        """Test cosine similarity search accuracy"""
        # Create vectors with known similarities
        base_vector = np.array([1.0] + [0.0] * 127, dtype=np.float32)

        # Add base vector
        base_id = live_vector_db.add_vector(base_vector, {"label": "base"}, normalize=True)

        # Add similar vectors
        similar_vector = np.array([0.9, 0.1] + [0.0] * 126, dtype=np.float32)
        live_vector_db.add_vector(similar_vector, {"label": "similar"}, normalize=True)

        # Add dissimilar vector
        dissimilar_vector = np.array([0.0, 0.0, 1.0] + [0.0] * 125, dtype=np.float32)
        live_vector_db.add_vector(dissimilar_vector, {"label": "dissimilar"}, normalize=True)

        time.sleep(0.2)

        # Search with base vector
        results = live_vector_db.top_cosine_similarity(base_vector, top_n=3)

        assert len(results) >= 2
        # First result should be the base vector itself (or very similar)
        assert results[0][2] > 0.9  # High similarity score

    def test_search_with_filter(self, live_vector_db, sample_vectors):
        """Test search with filter function"""
        # Add vectors
        live_vector_db.add_vectors_batch(sample_vectors, normalize=True)
        time.sleep(0.2)

        # Search with category filter
        query_vector = sample_vectors[0][0]
        filter_func = lambda id, meta: meta.get("category") == "A"

        results = live_vector_db.top_cosine_similarity(query_vector, top_n=5, filter_func=filter_func)

        # All results should be category A
        for _, metadata, _ in results:
            assert metadata.get("category") == "A"

    def test_metadata_query(self, live_vector_db, sample_vectors):
        """Test querying by metadata fields"""
        live_vector_db.add_vectors_batch(sample_vectors, normalize=True)
        time.sleep(0.2)

        # Query by category
        results = live_vector_db.query_by_metadata(category="B")

        assert len(results) > 0
        for _, _, metadata in results:
            assert metadata["category"] == "B"

    def test_empty_search(self, live_vector_db):
        """Test search on empty collection"""
        # Clear database
        live_vector_db.clear_database()
        time.sleep(0.1)

        query_vector = np.random.rand(128).astype(np.float32)
        results = live_vector_db.top_cosine_similarity(query_vector, top_n=5)

        assert results == []

    def test_list_all_ids(self, live_vector_db, sample_vectors):
        """Test listing all vector IDs"""
        ids = live_vector_db.add_vectors_batch(sample_vectors, normalize=True)
        time.sleep(0.2)

        all_ids = live_vector_db.list_all_ids()

        assert len(all_ids) >= len(ids)
        # Verify our IDs are in the list
        for id in ids:
            assert id in all_ids


# ============================================================================
# DATA INTEGRITY TESTS
# ============================================================================

@skip_if_no_server
class TestDataIntegrity:
    """Test data integrity and persistence"""

    def test_vector_normalization_persistence(self, live_vector_db):
        """Test that normalized vectors are stored correctly"""
        # Non-normalized vector
        vector = np.array([3.0, 4.0] + [0.0] * 126, dtype=np.float32)

        vector_id = live_vector_db.add_vector(vector, {"test": "norm"}, normalize=True)
        time.sleep(0.1)

        # Retrieve
        result = live_vector_db.get_vector_by_id(vector_id)
        retrieved_vector, _ = result

        # Check normalization (magnitude should be 1.0)
        magnitude = np.linalg.norm(retrieved_vector)
        assert np.isclose(magnitude, 1.0, atol=1e-5)

    def test_metadata_types_preservation(self, live_vector_db):
        """Test that different metadata types are preserved"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = {
            "string": "test",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "nested": {"key": "value"}
        }

        vector_id = live_vector_db.add_vector(vector, metadata)
        time.sleep(0.1)

        # Retrieve
        _, retrieved_metadata = live_vector_db.get_vector_by_id(vector_id)

        assert retrieved_metadata["string"] == "test"
        assert retrieved_metadata["integer"] == 42
        assert abs(retrieved_metadata["float"] - 3.14) < 0.001
        assert retrieved_metadata["boolean"] is True
        assert retrieved_metadata["list"] == [1, 2, 3]
        assert retrieved_metadata["nested"]["key"] == "value"

    def test_special_characters_in_metadata(self, live_vector_db):
        """Test special characters in metadata"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = {
            "text": "Special: é, ñ, 中文, 🚀",
            "symbols": "!@#$%^&*()",
        }

        vector_id = live_vector_db.add_vector(vector, metadata)
        time.sleep(0.1)

        _, retrieved_metadata = live_vector_db.get_vector_by_id(vector_id)

        assert retrieved_metadata["text"] == "Special: é, ñ, 中文, 🚀"
        assert retrieved_metadata["symbols"] == "!@#$%^&*()"

    def test_large_metadata(self, live_vector_db):
        """Test large metadata storage"""
        vector = np.random.rand(128).astype(np.float32)
        large_text = "Lorem ipsum " * 1000  # ~12KB of text
        metadata = {"large_text": large_text}

        vector_id = live_vector_db.add_vector(vector, metadata)
        time.sleep(0.1)

        _, retrieved_metadata = live_vector_db.get_vector_by_id(vector_id)
        assert retrieved_metadata["large_text"] == large_text


# ============================================================================
# DATABASE MANAGEMENT TESTS
# ============================================================================

@skip_if_no_server
class TestLiveDatabaseManagement:
    """Test database management operations"""

    def test_get_accurate_vector_count(self, live_vector_db, sample_vectors):
        """Test accurate vector count"""
        # Clear first
        live_vector_db.clear_database()
        time.sleep(0.1)

        # Add known number of vectors
        live_vector_db.add_vectors_batch(sample_vectors[:7], normalize=True)
        time.sleep(0.2)

        count = live_vector_db.get_vector_count()
        assert count == 7

    def test_clear_database(self, live_vector_db, sample_vectors):
        """Test clearing database"""
        # Add vectors
        live_vector_db.add_vectors_batch(sample_vectors, normalize=True)
        time.sleep(0.1)

        # Verify they exist
        count_before = live_vector_db.get_vector_count()
        assert count_before > 0

        # Clear
        live_vector_db.clear_database()
        time.sleep(0.1)

        # Verify empty
        count_after = live_vector_db.get_vector_count()
        assert count_after == 0

    def test_get_stats(self, live_vector_db, sample_vectors):
        """Test getting database statistics"""
        live_vector_db.add_vectors_batch(sample_vectors, normalize=True)
        time.sleep(0.1)

        stats = live_vector_db.get_stats()

        assert stats['total_vectors'] >= len(sample_vectors)
        assert stats['dimension'] == 128
        assert stats['collection_name'] == 'test_live_collection'
        assert stats['status'] in ['green', 'yellow']


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@skip_if_no_server
class TestPerformance:
    """Test performance benchmarks"""

    def test_batch_insert_performance(self, live_vector_db):
        """Test batch insertion performance"""
        # Create 1000 vectors
        vectors_with_meta = [
            (np.random.rand(128).astype(np.float32), {"id": i})
            for i in range(1000)
        ]

        start_time = time.time()
        live_vector_db.add_vectors_batch(vectors_with_meta, normalize=True)
        end_time = time.time()

        duration = end_time - start_time

        # Should complete in reasonable time (adjust threshold as needed)
        assert duration < 10.0, f"Batch insert took {duration:.2f}s, expected < 10s"

        print(f"\n✓ Batch insert of 1000 vectors: {duration:.2f}s ({1000/duration:.0f} vectors/sec)")

    def test_search_performance(self, live_vector_db):
        """Test search performance"""
        # Add some vectors
        vectors_with_meta = [
            (np.random.rand(128).astype(np.float32), {"id": i})
            for i in range(100)
        ]
        live_vector_db.add_vectors_batch(vectors_with_meta, normalize=True)
        time.sleep(0.2)

        # Perform multiple searches
        query_vector = np.random.rand(128).astype(np.float32)

        start_time = time.time()
        for _ in range(100):
            live_vector_db.top_cosine_similarity(query_vector, top_n=10)
        end_time = time.time()

        duration = end_time - start_time
        avg_search_time = duration / 100

        assert avg_search_time < 0.1, f"Average search took {avg_search_time:.4f}s, expected < 0.1s"

        print(f"\n✓ Average search time (100 queries): {avg_search_time*1000:.2f}ms")


# ============================================================================
# ERROR RECOVERY TESTS
# ============================================================================

@skip_if_no_server
class TestErrorRecovery:
    """Test error handling and recovery"""

    def test_update_nonexistent_vector(self, live_vector_db):
        """Test updating non-existent vector"""
        result = live_vector_db.update_vector("nonexistent_id_12345", new_metadata={"test": "data"})

        assert result is False

    def test_delete_nonexistent_vector(self, live_vector_db):
        """Test deleting non-existent vector"""
        # Should not raise exception
        result = live_vector_db.delete_vector("nonexistent_id_67890")

        # May return True or False depending on Qdrant behavior
        assert isinstance(result, bool)

    def test_get_nonexistent_vector(self, live_vector_db):
        """Test retrieving non-existent vector"""
        result = live_vector_db.get_vector_by_id("nonexistent_id_xyz")

        assert result is None

    def test_query_empty_metadata(self, live_vector_db):
        """Test metadata query with no matching results"""
        results = live_vector_db.query_by_metadata(nonexistent_field="value")

        assert results == []


# ============================================================================
# FULL INTEGRATION WORKFLOW
# ============================================================================

@skip_if_no_server
class TestFullIntegrationWorkflow:
    """Test complete end-to-end workflows"""

    def test_document_storage_and_retrieval_workflow(self, live_vector_db):
        """Test realistic document storage and retrieval scenario"""
        # Simulate storing document embeddings
        documents = [
            ("Machine learning is a subset of AI", np.random.rand(128)),
            ("Deep learning uses neural networks", np.random.rand(128)),
            ("Python is a programming language", np.random.rand(128)),
            ("Natural language processing handles text", np.random.rand(128)),
        ]

        # Store documents
        doc_ids = []
        for text, embedding in documents:
            vector_id = live_vector_db.add_text_with_embedding(
                text=text,
                embedding=embedding,
                metadata={"category": "tech"},
                normalize=True
            )
            doc_ids.append(vector_id)

        time.sleep(0.2)

        # Verify storage
        assert len(doc_ids) == 4
        count = live_vector_db.get_vector_count()
        assert count >= 4

        # Search for similar documents
        query_embedding = documents[0][1]
        results = live_vector_db.top_cosine_similarity(query_embedding, top_n=3)

        assert len(results) > 0
        assert all('text' in metadata for _, metadata, _ in results)

        # Update a document
        update_result = live_vector_db.update_vector(
            doc_ids[0],
            new_metadata={"text": documents[0][0], "category": "tech", "updated": True}
        )
        assert update_result is True

        time.sleep(0.1)

        # Verify update
        retrieved = live_vector_db.get_vector_by_id(doc_ids[0])
        _, metadata = retrieved
        assert metadata.get("updated") is True

        # Query by category
        category_results = live_vector_db.query_by_metadata(category="tech")
        assert len(category_results) >= 4

        # Cleanup - delete documents
        for doc_id in doc_ids:
            live_vector_db.delete_vector(doc_id)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("QDRANT LIVE INTEGRATION TESTS")
    print("="*70)
    print("\nThese tests require a running Qdrant instance.")
    print("\nTo run tests:")
    print("  1. Start Qdrant: docker run -p 6333:6333 qdrant/qdrant")
    print("  2. Run: pytest tests/test_qdrant_integration_live.py -v")
    print("\nTo skip: SKIP_LIVE_TESTS=1 pytest tests/test_qdrant_integration_live.py")
    print("="*70 + "\n")

    pytest.main([__file__, "-v", "--tb=short", "-s"])
