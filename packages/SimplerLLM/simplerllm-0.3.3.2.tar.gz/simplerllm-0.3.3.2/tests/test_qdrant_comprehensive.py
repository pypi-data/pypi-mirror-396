"""
Comprehensive Unit Tests for Qdrant Vector Database Integration

This test suite provides thorough testing of all Qdrant functionality using mocked clients.
No live Qdrant server is required for these tests.

Test Coverage:
- Connection & Initialization
- Vector CRUD Operations
- Search & Retrieval
- Data Integrity
- Database Management
- Edge Cases & Error Handling
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch, call
import uuid

# Import Qdrant components
from SimplerLLM.vectors.qdrant_vector_db import QdrantVectorDB
from SimplerLLM.vectors.vector_providers import VectorProvider


class MockQdrantPoint:
    """Mock Qdrant Point for testing"""
    def __init__(self, id, vector, payload, score=None):
        self.id = id
        self.vector = vector
        self.payload = payload
        self.score = score


class MockCollectionInfo:
    """Mock Qdrant Collection Info"""
    def __init__(self, name, points_count=0, status="green"):
        self.name = name
        self.points_count = points_count
        self.status = status


class MockCollectionsResponse:
    """Mock Qdrant Collections Response"""
    def __init__(self, collection_names):
        self.collections = [MockCollectionInfo(name) for name in collection_names]


@pytest.fixture
def mock_qdrant_client():
    """Create a mocked Qdrant client"""
    with patch('SimplerLLM.vectors.qdrant_vector_db.QdrantClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock default responses
        mock_client.get_collections.return_value = MockCollectionsResponse(['default_collection'])
        mock_client.create_collection.return_value = True
        mock_client.upsert.return_value = True
        mock_client.delete.return_value = True
        mock_client.get_collection.return_value = MockCollectionInfo('default_collection', points_count=0)

        yield mock_client


@pytest.fixture
def vector_db(mock_qdrant_client):
    """Create QdrantVectorDB instance with mocked client"""
    db = QdrantVectorDB(
        provider=VectorProvider.QDRANT,
        url='localhost',
        port=6333,
        collection_name='test_collection',
        dimension=128
    )
    return db


# ============================================================================
# CONNECTION & INITIALIZATION TESTS
# ============================================================================

class TestConnectionAndInitialization:
    """Test Qdrant connection and initialization scenarios"""

    def test_init_with_local_connection(self, mock_qdrant_client):
        """Test initialization with local host connection"""
        db = QdrantVectorDB(
            provider=VectorProvider.QDRANT,
            url='localhost',
            port=6333,
            collection_name='test_collection',
            dimension=128
        )

        assert db.url == 'localhost'
        assert db.port == 6333
        assert db.collection_name == 'test_collection'
        assert db.dimension == 128

    def test_init_with_api_key(self, mock_qdrant_client):
        """Test initialization with API key for cloud instance"""
        with patch('SimplerLLM.vectors.qdrant_vector_db.QdrantClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get_collections.return_value = MockCollectionsResponse(['test_collection'])

            db = QdrantVectorDB(
                provider=VectorProvider.QDRANT,
                url='https://my-qdrant.cloud',
                port=443,
                api_key='test_api_key_123',
                collection_name='test_collection',
                dimension=256
            )

            # Verify client was created with API key
            mock_client_class.assert_called_once_with(
                url='https://my-qdrant.cloud',
                port=443,
                api_key='test_api_key_123',
                timeout=10
            )

    def test_collection_auto_creation(self, mock_qdrant_client):
        """Test that collection is auto-created if it doesn't exist"""
        mock_qdrant_client.get_collections.return_value = MockCollectionsResponse([])

        db = QdrantVectorDB(
            provider=VectorProvider.QDRANT,
            url='localhost',
            port=6333,
            collection_name='new_collection',
            dimension=128
        )

        # Should attempt to create collection since it doesn't exist
        mock_qdrant_client.create_collection.assert_called_once()

    def test_collection_exists_no_creation(self, mock_qdrant_client):
        """Test that existing collection is not recreated"""
        mock_qdrant_client.get_collections.return_value = MockCollectionsResponse(['existing_collection'])

        db = QdrantVectorDB(
            provider=VectorProvider.QDRANT,
            url='localhost',
            port=6333,
            collection_name='existing_collection',
            dimension=128
        )

        # Should not create collection since it exists
        mock_qdrant_client.create_collection.assert_not_called()

    def test_dimension_none_deferred_creation(self, mock_qdrant_client):
        """Test that collection creation is deferred when dimension is None"""
        mock_qdrant_client.get_collections.return_value = MockCollectionsResponse([])

        db = QdrantVectorDB(
            provider=VectorProvider.QDRANT,
            url='localhost',
            port=6333,
            collection_name='new_collection',
            dimension=None  # Dimension unknown
        )

        # Should not create collection yet
        mock_qdrant_client.create_collection.assert_not_called()


# ============================================================================
# VECTOR CRUD OPERATIONS TESTS
# ============================================================================

class TestVectorCRUDOperations:
    """Test Create, Read, Update, Delete operations for vectors"""

    def test_add_vector_basic(self, vector_db, mock_qdrant_client):
        """Test adding a single vector with metadata"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = {"text": "test document", "category": "test"}

        vector_id = vector_db.add_vector(vector, metadata, normalize=True)

        assert vector_id is not None
        assert isinstance(vector_id, str)
        mock_qdrant_client.upsert.assert_called_once()

    def test_add_vector_custom_id(self, vector_db, mock_qdrant_client):
        """Test adding vector with custom ID"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = {"text": "test"}
        custom_id = "custom_id_123"

        vector_id = vector_db.add_vector(vector, metadata, normalize=False, id=custom_id)

        assert vector_id == custom_id

    def test_add_vector_normalization(self, vector_db, mock_qdrant_client):
        """Test that vectors are normalized when requested"""
        vector = np.array([3.0, 4.0] + [0.0] * 126, dtype=np.float32)
        metadata = {"test": "data"}

        vector_db.add_vector(vector, metadata, normalize=True)

        # Get the call arguments
        call_args = mock_qdrant_client.upsert.call_args
        points = call_args[1]['points']
        stored_vector = np.array(points[0].vector)

        # Check if normalized (magnitude should be 1.0)
        magnitude = np.linalg.norm(stored_vector)
        assert np.isclose(magnitude, 1.0, atol=1e-6)

    def test_add_vector_without_normalization(self, vector_db, mock_qdrant_client):
        """Test adding vector without normalization"""
        vector = np.array([3.0, 4.0] + [0.0] * 126, dtype=np.float32)
        metadata = {"test": "data"}

        vector_db.add_vector(vector, metadata, normalize=False)

        call_args = mock_qdrant_client.upsert.call_args
        points = call_args[1]['points']
        stored_vector = np.array(points[0].vector)

        # Should match original (magnitude is 5.0)
        assert np.allclose(stored_vector[:2], [3.0, 4.0])

    def test_add_vector_non_dict_metadata(self, vector_db, mock_qdrant_client):
        """Test adding vector with non-dict metadata"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = "string metadata"

        vector_db.add_vector(vector, metadata)

        call_args = mock_qdrant_client.upsert.call_args
        points = call_args[1]['points']
        payload = points[0].payload

        # Should be wrapped in metadata key
        assert payload == {"metadata": "string metadata"}

    def test_add_vectors_batch(self, vector_db, mock_qdrant_client):
        """Test batch insertion of vectors"""
        vectors_with_meta = [
            (np.random.rand(128), {"id": 1, "text": "doc1"}),
            (np.random.rand(128), {"id": 2, "text": "doc2"}),
            (np.random.rand(128), {"id": 3, "text": "doc3"}),
        ]

        ids = vector_db.add_vectors_batch(vectors_with_meta, normalize=True)

        assert len(ids) == 3
        assert all(isinstance(id, str) for id in ids)
        mock_qdrant_client.upsert.assert_called_once()

    def test_add_vectors_batch_with_custom_ids(self, vector_db, mock_qdrant_client):
        """Test batch insertion with custom IDs"""
        vectors_with_meta = [
            (np.random.rand(128), {"text": "doc1"}, "id1"),
            (np.random.rand(128), {"text": "doc2"}, "id2"),
            (np.random.rand(128), {"text": "doc3"}, "id3"),
        ]

        ids = vector_db.add_vectors_batch(vectors_with_meta)

        assert ids == ["id1", "id2", "id3"]

    def test_add_text_with_embedding(self, vector_db, mock_qdrant_client):
        """Test adding text with embedding"""
        text = "This is a test document"
        embedding = np.random.rand(128).astype(np.float32)
        metadata = {"category": "test"}

        vector_id = vector_db.add_text_with_embedding(text, embedding, metadata)

        call_args = mock_qdrant_client.upsert.call_args
        points = call_args[1]['points']
        payload = points[0].payload

        # Should include text in metadata
        assert payload['text'] == text
        assert payload['category'] == 'test'

    def test_delete_vector(self, vector_db, mock_qdrant_client):
        """Test deleting a vector by ID"""
        vector_id = "test_id_123"

        result = vector_db.delete_vector(vector_id)

        assert result is True
        mock_qdrant_client.delete.assert_called_once()

    def test_delete_vector_error_handling(self, vector_db, mock_qdrant_client):
        """Test error handling when deleting vector fails"""
        mock_qdrant_client.delete.side_effect = Exception("Delete failed")

        result = vector_db.delete_vector("nonexistent_id")

        assert result is False

    def test_update_vector_data(self, vector_db, mock_qdrant_client):
        """Test updating vector data"""
        vector_id = "test_id"
        existing_vector = np.random.rand(128).astype(np.float32)
        existing_payload = {"text": "old text"}

        mock_qdrant_client.retrieve.return_value = [
            MockQdrantPoint(vector_id, existing_vector.tolist(), existing_payload)
        ]

        new_vector = np.random.rand(128).astype(np.float32)
        result = vector_db.update_vector(vector_id, new_vector=new_vector)

        assert result is True
        mock_qdrant_client.upsert.assert_called_once()

    def test_update_vector_metadata(self, vector_db, mock_qdrant_client):
        """Test updating vector metadata only"""
        vector_id = "test_id"
        existing_vector = np.random.rand(128).astype(np.float32)
        existing_payload = {"text": "old text"}

        mock_qdrant_client.retrieve.return_value = [
            MockQdrantPoint(vector_id, existing_vector.tolist(), existing_payload)
        ]

        new_metadata = {"text": "new text", "category": "updated"}
        result = vector_db.update_vector(vector_id, new_metadata=new_metadata)

        assert result is True
        call_args = mock_qdrant_client.upsert.call_args
        points = call_args[1]['points']
        assert points[0].payload == new_metadata

    def test_update_nonexistent_vector(self, vector_db, mock_qdrant_client):
        """Test updating vector that doesn't exist"""
        mock_qdrant_client.retrieve.return_value = []

        result = vector_db.update_vector("nonexistent_id", new_metadata={"test": "data"})

        assert result is False


# ============================================================================
# SEARCH & RETRIEVAL TESTS
# ============================================================================

class TestSearchAndRetrieval:
    """Test search and retrieval operations"""

    def test_top_cosine_similarity_basic(self, vector_db, mock_qdrant_client):
        """Test basic cosine similarity search"""
        query_vector = np.random.rand(128).astype(np.float32)

        # Mock search results
        mock_results = [
            MockQdrantPoint("id1", [0.1] * 128, {"text": "doc1"}, score=0.95),
            MockQdrantPoint("id2", [0.2] * 128, {"text": "doc2"}, score=0.85),
            MockQdrantPoint("id3", [0.3] * 128, {"text": "doc3"}, score=0.75),
        ]
        mock_qdrant_client.search.return_value = mock_results

        results = vector_db.top_cosine_similarity(query_vector, top_n=3)

        assert len(results) == 3
        assert results[0][0] == "id1"  # ID
        assert results[0][1] == {"text": "doc1"}  # Metadata
        assert results[0][2] == 0.95  # Score

    def test_top_cosine_similarity_with_filter(self, vector_db, mock_qdrant_client):
        """Test cosine similarity search with filter function"""
        query_vector = np.random.rand(128).astype(np.float32)

        mock_results = [
            MockQdrantPoint("id1", [0.1] * 128, {"text": "doc1", "category": "A"}, score=0.95),
            MockQdrantPoint("id2", [0.2] * 128, {"text": "doc2", "category": "B"}, score=0.85),
            MockQdrantPoint("id3", [0.3] * 128, {"text": "doc3", "category": "A"}, score=0.75),
        ]
        mock_qdrant_client.search.return_value = mock_results

        # Filter for category A only
        filter_func = lambda id, meta: meta.get("category") == "A"
        results = vector_db.top_cosine_similarity(query_vector, top_n=2, filter_func=filter_func)

        assert len(results) == 2
        assert all(r[1]["category"] == "A" for r in results)

    def test_search_by_text(self, vector_db, mock_qdrant_client):
        """Test text-based search with embedding generation"""
        query_text = "test query"

        # Mock embeddings LLM
        mock_embeddings_llm = Mock()
        mock_embeddings_llm.generate_embeddings.return_value = np.random.rand(128).tolist()

        mock_results = [
            MockQdrantPoint("id1", [0.1] * 128, {"text": "result1"}, score=0.9),
        ]
        mock_qdrant_client.search.return_value = mock_results

        results = vector_db.search_by_text(query_text, mock_embeddings_llm, top_n=1)

        assert len(results) == 1
        mock_embeddings_llm.generate_embeddings.assert_called_once_with(query_text)

    def test_search_by_text_empty_query(self, vector_db, mock_qdrant_client):
        """Test text search with empty query"""
        mock_embeddings_llm = Mock()

        results = vector_db.search_by_text("", mock_embeddings_llm)

        assert results == []

    def test_get_vector_by_id(self, vector_db, mock_qdrant_client):
        """Test retrieving vector by ID"""
        vector_id = "test_id"
        expected_vector = np.random.rand(128).astype(np.float32)
        expected_metadata = {"text": "test document"}

        mock_qdrant_client.retrieve.return_value = [
            MockQdrantPoint(vector_id, expected_vector.tolist(), expected_metadata)
        ]

        result = vector_db.get_vector_by_id(vector_id)

        assert result is not None
        vector, metadata = result
        assert np.allclose(vector, expected_vector)
        assert metadata == expected_metadata

    def test_get_vector_by_id_not_found(self, vector_db, mock_qdrant_client):
        """Test retrieving non-existent vector"""
        mock_qdrant_client.retrieve.return_value = []

        result = vector_db.get_vector_by_id("nonexistent_id")

        assert result is None

    def test_query_by_metadata(self, vector_db, mock_qdrant_client):
        """Test querying vectors by metadata"""
        mock_results = [
            MockQdrantPoint("id1", [0.1] * 128, {"category": "test", "text": "doc1"}),
            MockQdrantPoint("id2", [0.2] * 128, {"category": "test", "text": "doc2"}),
        ]
        mock_qdrant_client.scroll.return_value = (mock_results, None)

        results = vector_db.query_by_metadata(category="test")

        assert len(results) == 2
        assert all(r[2]["category"] == "test" for r in results)

    def test_query_by_metadata_no_conditions(self, vector_db, mock_qdrant_client):
        """Test metadata query with no conditions"""
        results = vector_db.query_by_metadata()

        assert results == []

    def test_list_all_ids(self, vector_db, mock_qdrant_client):
        """Test listing all vector IDs"""
        mock_points = [
            MockQdrantPoint("id1", None, None),
            MockQdrantPoint("id2", None, None),
            MockQdrantPoint("id3", None, None),
        ]
        mock_qdrant_client.scroll.return_value = (mock_points, None)

        ids = vector_db.list_all_ids()

        assert ids == ["id1", "id2", "id3"]

    def test_list_all_ids_pagination(self, vector_db, mock_qdrant_client):
        """Test listing IDs with pagination"""
        # First page
        mock_points_page1 = [MockQdrantPoint(f"id{i}", None, None) for i in range(1000)]
        # Second page
        mock_points_page2 = [MockQdrantPoint(f"id{i}", None, None) for i in range(1000, 1500)]

        mock_qdrant_client.scroll.side_effect = [
            (mock_points_page1, "offset_token"),
            (mock_points_page2, None)
        ]

        ids = vector_db.list_all_ids()

        assert len(ids) == 1500
        assert mock_qdrant_client.scroll.call_count == 2


# ============================================================================
# DATABASE MANAGEMENT TESTS
# ============================================================================

class TestDatabaseManagement:
    """Test database management operations"""

    def test_get_vector_count(self, vector_db, mock_qdrant_client):
        """Test getting vector count"""
        mock_qdrant_client.get_collection.return_value = MockCollectionInfo(
            'test_collection', points_count=42
        )

        count = vector_db.get_vector_count()

        assert count == 42

    def test_get_vector_count_error(self, vector_db, mock_qdrant_client):
        """Test vector count with error"""
        mock_qdrant_client.get_collection.side_effect = Exception("Connection error")

        count = vector_db.get_vector_count()

        assert count == 0

    def test_clear_database(self, vector_db, mock_qdrant_client):
        """Test clearing database"""
        vector_db.clear_database()

        mock_qdrant_client.delete_collection.assert_called_once_with('test_collection')
        # create_collection is called during init + clear_database = 2 times
        assert mock_qdrant_client.create_collection.call_count == 2

    def test_get_stats(self, vector_db, mock_qdrant_client):
        """Test getting database statistics"""
        mock_qdrant_client.get_collection.return_value = MockCollectionInfo(
            'test_collection', points_count=100, status="green"
        )

        stats = vector_db.get_stats()

        assert stats['total_vectors'] == 100
        assert stats['dimension'] == 128
        assert stats['collection_name'] == 'test_collection'
        assert stats['status'] == 'green'

    def test_get_stats_error(self, vector_db, mock_qdrant_client):
        """Test getting stats with error"""
        mock_qdrant_client.get_collection.side_effect = Exception("Error")

        stats = vector_db.get_stats()

        assert stats['total_vectors'] == 0
        assert stats['status'] == 'error'

    def test_compress_vectors_not_supported(self, vector_db):
        """Test that compression returns 1.0 (not supported)"""
        ratio = vector_db.compress_vectors(bits=16)

        assert ratio == 1.0

    def test_save_to_disk_auto_handled(self, vector_db):
        """Test that save_to_disk is auto-handled"""
        # Should not raise exception
        vector_db.save_to_disk('test_collection')

    def test_load_from_disk(self, vector_db, mock_qdrant_client):
        """Test loading collection from disk"""
        vector_db.load_from_disk('loaded_collection')

        assert vector_db.collection_name == 'loaded_collection'


# ============================================================================
# EDGE CASES & ERROR HANDLING TESTS
# ============================================================================

class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling"""

    def test_empty_vector(self, vector_db, mock_qdrant_client):
        """Test handling of empty vector"""
        empty_vector = np.array([], dtype=np.float32)
        metadata = {"test": "data"}

        # Should handle gracefully
        vector_id = vector_db.add_vector(empty_vector, metadata, normalize=False)
        assert vector_id is not None

    def test_zero_vector_normalization(self, vector_db, mock_qdrant_client):
        """Test normalization of zero vector"""
        zero_vector = np.zeros(128, dtype=np.float32)
        metadata = {"test": "data"}

        # Should not divide by zero
        vector_id = vector_db.add_vector(zero_vector, metadata, normalize=True)

        call_args = mock_qdrant_client.upsert.call_args
        points = call_args[1]['points']
        stored_vector = np.array(points[0].vector)

        # Should remain zeros
        assert np.all(stored_vector == 0)

    def test_large_batch_operations(self, vector_db, mock_qdrant_client):
        """Test large batch insertion"""
        large_batch = [
            (np.random.rand(128), {"id": i})
            for i in range(10000)
        ]

        ids = vector_db.add_vectors_batch(large_batch)

        assert len(ids) == 10000

    def test_dimension_mismatch_detection(self, mock_qdrant_client):
        """Test handling of dimension mismatch"""
        db = QdrantVectorDB(
            provider=VectorProvider.QDRANT,
            url='localhost',
            port=6333,
            collection_name='test_collection',
            dimension=128
        )

        # Try to add vector with different dimension
        wrong_dim_vector = np.random.rand(256).astype(np.float32)
        metadata = {"test": "data"}

        # Should still proceed (Qdrant will handle validation)
        vector_id = db.add_vector(wrong_dim_vector, metadata)
        assert vector_id is not None

    def test_none_metadata(self, vector_db, mock_qdrant_client):
        """Test handling of None metadata"""
        vector = np.random.rand(128).astype(np.float32)

        vector_id = vector_db.add_vector(vector, None)

        call_args = mock_qdrant_client.upsert.call_args
        points = call_args[1]['points']
        payload = points[0].payload

        assert payload == {"metadata": None}

    def test_special_characters_in_metadata(self, vector_db, mock_qdrant_client):
        """Test metadata with special characters"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = {
            "text": "Special chars: é, ñ, 中文, 🚀",
            "symbols": "!@#$%^&*()",
            "quotes": 'He said "hello"'
        }

        vector_id = vector_db.add_vector(vector, metadata)

        call_args = mock_qdrant_client.upsert.call_args
        points = call_args[1]['points']
        stored_payload = points[0].payload

        assert stored_payload == metadata

    def test_numeric_metadata_values(self, vector_db, mock_qdrant_client):
        """Test metadata with various numeric types"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = {
            "int_val": 42,
            "float_val": 3.14,
            "bool_val": True,
            "list_val": [1, 2, 3],
            "nested": {"key": "value"}
        }

        vector_id = vector_db.add_vector(vector, metadata)

        call_args = mock_qdrant_client.upsert.call_args
        points = call_args[1]['points']
        stored_payload = points[0].payload

        assert stored_payload == metadata

    def test_uuid_generation_uniqueness(self, vector_db, mock_qdrant_client):
        """Test that auto-generated UUIDs are unique"""
        vector = np.random.rand(128).astype(np.float32)
        metadata = {"test": "data"}

        ids = set()
        for _ in range(100):
            vector_id = vector_db.add_vector(vector, metadata)
            ids.add(vector_id)

        # All IDs should be unique
        assert len(ids) == 100

    def test_search_empty_database(self, vector_db, mock_qdrant_client):
        """Test search on empty database"""
        mock_qdrant_client.search.return_value = []

        query_vector = np.random.rand(128).astype(np.float32)
        results = vector_db.top_cosine_similarity(query_vector)

        assert results == []

    def test_connection_timeout_handling(self, mock_qdrant_client):
        """Test that timeout is set correctly"""
        with patch('SimplerLLM.vectors.qdrant_vector_db.QdrantClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get_collections.return_value = MockCollectionsResponse(['test'])

            db = QdrantVectorDB(
                provider=VectorProvider.QDRANT,
                url='localhost',
                port=6333,
                collection_name='test',
                dimension=128
            )

            # Check that client was initialized with timeout
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs['timeout'] == 10


# ============================================================================
# INTEGRATION WORKFLOW TESTS
# ============================================================================

class TestIntegrationWorkflows:
    """Test complete workflows combining multiple operations"""

    def test_full_crud_workflow(self, vector_db, mock_qdrant_client):
        """Test complete Create-Read-Update-Delete workflow"""
        # 1. Create
        vector = np.random.rand(128).astype(np.float32)
        metadata = {"text": "original", "version": 1}
        vector_id = vector_db.add_vector(vector, metadata)
        assert vector_id is not None

        # 2. Read
        mock_qdrant_client.retrieve.return_value = [
            MockQdrantPoint(vector_id, vector.tolist(), metadata)
        ]
        result = vector_db.get_vector_by_id(vector_id)
        assert result is not None

        # 3. Update
        new_metadata = {"text": "updated", "version": 2}
        mock_qdrant_client.retrieve.return_value = [
            MockQdrantPoint(vector_id, vector.tolist(), metadata)
        ]
        update_result = vector_db.update_vector(vector_id, new_metadata=new_metadata)
        assert update_result is True

        # 4. Delete
        delete_result = vector_db.delete_vector(vector_id)
        assert delete_result is True

    def test_batch_insert_and_search_workflow(self, vector_db, mock_qdrant_client):
        """Test batch insertion followed by search"""
        # Batch insert
        vectors_with_meta = [
            (np.random.rand(128), {"text": f"doc{i}", "id": i})
            for i in range(10)
        ]
        ids = vector_db.add_vectors_batch(vectors_with_meta, normalize=True)
        assert len(ids) == 10

        # Search
        query_vector = np.random.rand(128).astype(np.float32)
        mock_results = [
            MockQdrantPoint(ids[i], [0.1] * 128, {"text": f"doc{i}"}, score=0.9 - i*0.1)
            for i in range(5)
        ]
        mock_qdrant_client.search.return_value = mock_results

        results = vector_db.top_cosine_similarity(query_vector, top_n=5)
        assert len(results) == 5

    def test_metadata_filtering_workflow(self, vector_db, mock_qdrant_client):
        """Test adding vectors and filtering by metadata"""
        # Add vectors with different categories
        for i in range(5):
            vector = np.random.rand(128).astype(np.float32)
            metadata = {"category": "A" if i % 2 == 0 else "B", "id": i}
            vector_db.add_vector(vector, metadata)

        # Query by metadata
        mock_results = [
            MockQdrantPoint(f"id{i}", [0.1]*128, {"category": "A", "id": i})
            for i in [0, 2, 4]
        ]
        mock_qdrant_client.scroll.return_value = (mock_results, None)

        results = vector_db.query_by_metadata(category="A")
        assert len(results) == 3
        assert all(r[2]["category"] == "A" for r in results)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
