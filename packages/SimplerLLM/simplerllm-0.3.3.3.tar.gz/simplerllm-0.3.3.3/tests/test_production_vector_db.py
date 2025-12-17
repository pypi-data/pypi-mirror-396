"""
Production-Ready Vector Database Interface Test Suite

This comprehensive test suite validates the unified vector database interface
across all available providers (LOCAL and QDRANT) to ensure production readiness.

Test Categories:
1. Cross-Provider Basic Operations
2. Cross-Provider Search Operations
3. Data Consistency Tests
4. Edge Cases
5. Error Handling
6. Provider-Specific Features
7. Performance & Accuracy
8. Provider Switching

Usage:
    # Run all tests
    pytest test_production_vector_db.py -v

    # Run only LOCAL tests
    pytest test_production_vector_db.py -v -m "not qdrant"

    # Run only fast tests
    pytest test_production_vector_db.py -v -m "not slow"
"""

import pytest
import numpy as np
import tempfile
import shutil
import time
from typing import List, Tuple, Any
from SimplerLLM.vectors.vector_db import (
    VectorDB, DimensionMismatchError, VectorDBOperationError,
    VectorDBConnectionError, VectorNotFoundError
)
from SimplerLLM.vectors.vector_providers import VectorProvider


# ==================== Test Fixtures ====================

@pytest.fixture
def temp_dir():
    """Create temporary directory for LOCAL provider."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def local_db(temp_dir):
    """Create fresh LOCAL vector database."""
    db = VectorDB.create(provider=VectorProvider.LOCAL, db_folder=temp_dir)
    yield db
    # Cleanup
    try:
        db.clear_database()
    except:
        pass


@pytest.fixture
def qdrant_db():
    """Create fresh QDRANT vector database (skip if not available)."""
    try:
        db = VectorDB.create(
            provider=VectorProvider.QDRANT,
            url='localhost',
            port=6333,
            collection_name=f'test_collection_{int(time.time())}',
            dimension=3
        )
        yield db
        # Cleanup
        try:
            db.clear_database()
        except:
            pass
    except (VectorDBConnectionError, Exception) as e:
        pytest.skip(f"Qdrant not available: {e}")


@pytest.fixture
def all_providers(local_db, qdrant_db):
    """Provide both LOCAL and QDRANT databases."""
    return [
        ("LOCAL", local_db),
        ("QDRANT", qdrant_db)
    ]


@pytest.fixture
def sample_vectors():
    """Generate sample test vectors with known relationships."""
    return {
        'v1': np.array([1.0, 0.0, 0.0], dtype=np.float32),
        'v2': np.array([0.9, 0.1, 0.0], dtype=np.float32),  # Similar to v1
        'v3': np.array([0.0, 1.0, 0.0], dtype=np.float32),  # Orthogonal to v1
        'v4': np.array([0.0, 0.0, 1.0], dtype=np.float32),  # Orthogonal to v1, v3
        'v5': np.array([0.5, 0.5, 0.0], dtype=np.float32),  # Between v1 and v3
    }


@pytest.fixture
def sample_metadata():
    """Generate sample metadata for testing."""
    return [
        {"text": "first document", "category": "A", "score": 10},
        {"text": "second document", "category": "A", "score": 20},
        {"text": "third document", "category": "B", "score": 30},
        {"text": "fourth document", "category": "B", "score": 40},
        {"text": "fifth document", "category": "C", "score": 50},
    ]


# ==================== Helper Functions ====================

def normalize_vector(v):
    """Normalize a vector to unit length."""
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v


def cosine_similarity(v1, v2):
    """Calculate cosine similarity between two vectors."""
    v1_norm = normalize_vector(v1)
    v2_norm = normalize_vector(v2)
    return float(np.dot(v1_norm, v2_norm))


def compare_search_results(results1, results2, tolerance=0.01):
    """
    Compare search results from two providers.
    Returns True if results are consistent within tolerance.
    """
    if len(results1) != len(results2):
        return False

    for (id1, meta1, score1), (id2, meta2, score2) in zip(results1, results2):
        # Scores should be within tolerance
        if abs(score1 - score2) > tolerance:
            return False

    return True


def assert_stats_valid(stats, provider_name):
    """Validate stats dictionary structure."""
    required_fields = ['total_vectors', 'dimension', 'provider']
    for field in required_fields:
        assert field in stats, f"{provider_name}: Missing required field '{field}' in stats"

    assert isinstance(stats['total_vectors'], int), f"{provider_name}: total_vectors must be int"
    assert stats['provider'] in ['local', 'qdrant'], f"{provider_name}: Invalid provider name"


# ==================== Test Suite 1: Cross-Provider Basic Operations ====================

@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_provider_initialization(provider_fixture, request):
    """Test that both providers initialize correctly."""
    db = request.getfixturevalue(provider_fixture)
    assert db is not None
    assert hasattr(db, 'provider')
    assert db.get_vector_count() == 0


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_add_single_vector_all_providers(provider_fixture, request, sample_vectors):
    """Test adding a single vector to both providers."""
    db = request.getfixturevalue(provider_fixture)

    vector = sample_vectors['v1']
    metadata = {"text": "test vector"}

    vector_id = db.add_vector(vector, metadata, normalize=True)

    assert vector_id is not None
    assert isinstance(vector_id, str)
    assert db.get_vector_count() == 1

    # Verify retrieval
    retrieved = db.get_vector_by_id(vector_id)
    assert retrieved is not None
    vec, meta = retrieved
    assert np.allclose(normalize_vector(vector), vec, atol=0.001)
    assert meta['text'] == "test vector"


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_add_batch_vectors_all_providers(provider_fixture, request, sample_vectors, sample_metadata):
    """Test batch vector addition on both providers."""
    db = request.getfixturevalue(provider_fixture)

    vectors_with_meta = [
        (sample_vectors['v1'], sample_metadata[0]),
        (sample_vectors['v2'], sample_metadata[1]),
        (sample_vectors['v3'], sample_metadata[2]),
    ]

    ids = db.add_vectors_batch(vectors_with_meta, normalize=True)

    assert len(ids) == 3
    assert all(isinstance(id, str) for id in ids)
    assert db.get_vector_count() == 3

    # Verify all vectors retrievable
    for vec_id in ids:
        assert db.get_vector_by_id(vec_id) is not None


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_add_text_with_embedding_all_providers(provider_fixture, request, sample_vectors):
    """Test add_text_with_embedding on both providers."""
    db = request.getfixturevalue(provider_fixture)

    text = "This is a test document"
    embedding = sample_vectors['v1']
    metadata = {"source": "test"}

    vector_id = db.add_text_with_embedding(text, embedding, metadata, normalize=True)

    assert vector_id is not None
    retrieved = db.get_vector_by_id(vector_id)
    assert retrieved is not None
    vec, meta = retrieved

    # Text should be in metadata
    assert 'text' in meta
    assert meta['text'] == text
    assert meta['source'] == "test"


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_update_vector_all_providers(provider_fixture, request, sample_vectors):
    """Test vector update on both providers."""
    db = request.getfixturevalue(provider_fixture)

    # Add initial vector
    vec_id = db.add_vector(sample_vectors['v1'], {"version": 1}, normalize=True)

    # Update vector
    success = db.update_vector(vec_id, new_vector=sample_vectors['v2'], normalize=True)
    assert success is True

    # Verify update
    vec, meta = db.get_vector_by_id(vec_id)
    assert np.allclose(normalize_vector(sample_vectors['v2']), vec, atol=0.001)

    # Update metadata only
    success = db.update_vector(vec_id, new_metadata={"version": 2})
    assert success is True

    vec, meta = db.get_vector_by_id(vec_id)
    assert meta['version'] == 2


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_delete_vector_all_providers(provider_fixture, request, sample_vectors):
    """Test vector deletion on both providers."""
    db = request.getfixturevalue(provider_fixture)

    # Add vector
    vec_id = db.add_vector(sample_vectors['v1'], {"test": "data"})
    assert db.get_vector_count() == 1

    # Delete vector
    success = db.delete_vector(vec_id)
    assert success is True
    assert db.get_vector_count() == 0

    # Verify deletion
    assert db.get_vector_by_id(vec_id) is None


# ==================== Test Suite 2: Cross-Provider Search Operations ====================

@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_cosine_similarity_all_providers(provider_fixture, request, sample_vectors, sample_metadata):
    """Test cosine similarity search on both providers."""
    db = request.getfixturevalue(provider_fixture)

    # Add vectors
    db.add_vector(sample_vectors['v1'], sample_metadata[0], normalize=True)
    db.add_vector(sample_vectors['v2'], sample_metadata[1], normalize=True)
    db.add_vector(sample_vectors['v3'], sample_metadata[2], normalize=True)

    # Search for similar to v1
    results = db.top_cosine_similarity(sample_vectors['v1'], top_n=2)

    assert len(results) == 2
    # First result should be v1 itself or v2 (very similar)
    assert results[0][2] > 0.9  # High similarity score

    # Verify score descending order
    assert results[0][2] >= results[1][2]


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_metadata_query_all_providers(provider_fixture, request, sample_vectors, sample_metadata):
    """Test metadata querying on both providers."""
    db = request.getfixturevalue(provider_fixture)

    # Add vectors with metadata
    for i, (key, vec) in enumerate(list(sample_vectors.items())[:5]):
        db.add_vector(vec, sample_metadata[i], normalize=True)

    # Query by category
    results = db.query_by_metadata(category="A")
    assert len(results) == 2  # Two documents with category A

    # Query by score
    results = db.query_by_metadata(score=30)
    assert len(results) == 1
    assert results[0][2]['score'] == 30


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_filter_functions_all_providers(provider_fixture, request, sample_vectors, sample_metadata):
    """Test custom filter functions on both providers."""
    db = request.getfixturevalue(provider_fixture)

    # Add vectors
    for i, (key, vec) in enumerate(list(sample_vectors.items())[:5]):
        db.add_vector(vec, sample_metadata[i], normalize=True)

    # Filter by score > 20
    def filter_high_score(vec_id, metadata):
        return metadata.get('score', 0) > 20

    results = db.top_cosine_similarity(
        sample_vectors['v1'],
        top_n=10,
        filter_func=filter_high_score
    )

    # All results should have score > 20
    for vec_id, meta, score in results:
        assert meta['score'] > 20


# ==================== Test Suite 3: Data Consistency Tests ====================

def test_same_data_same_results(local_db, qdrant_db, sample_vectors, sample_metadata):
    """Verify both providers return consistent results for same data."""
    # Add same data to both providers
    for i, (key, vec) in enumerate(list(sample_vectors.items())[:5]):
        local_db.add_vector(vec, sample_metadata[i], normalize=True)
        qdrant_db.add_vector(vec, sample_metadata[i], normalize=True)

    # Search both
    query = sample_vectors['v1']
    local_results = local_db.top_cosine_similarity(query, top_n=3)
    qdrant_results = qdrant_db.top_cosine_similarity(query, top_n=3)

    # Compare results
    assert len(local_results) == len(qdrant_results)

    # Scores should be very close
    for (_, _, local_score), (_, _, qdrant_score) in zip(local_results, qdrant_results):
        assert abs(local_score - qdrant_score) < 0.01


def test_stats_consistency(local_db, qdrant_db, sample_vectors):
    """Verify stats report correct values on both providers."""
    # Add same data to both
    for vec in list(sample_vectors.values())[:3]:
        local_db.add_vector(vec, {"test": "data"}, normalize=True)
        qdrant_db.add_vector(vec, {"test": "data"}, normalize=True)

    local_stats = local_db.get_stats()
    qdrant_stats = qdrant_db.get_stats()

    # Validate structure
    assert_stats_valid(local_stats, "LOCAL")
    assert_stats_valid(qdrant_stats, "QDRANT")

    # Same counts
    assert local_stats['total_vectors'] == 3
    assert qdrant_stats['total_vectors'] == 3

    # Same dimension
    assert local_stats['dimension'] == qdrant_stats['dimension']


# ==================== Test Suite 4: Edge Cases ====================

@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_empty_database_operations(provider_fixture, request, sample_vectors):
    """Test operations on empty database."""
    db = request.getfixturevalue(provider_fixture)

    # Search on empty DB
    results = db.top_cosine_similarity(sample_vectors['v1'], top_n=5)
    assert len(results) == 0

    # Get stats on empty DB
    stats = db.get_stats()
    assert stats['total_vectors'] == 0

    # List IDs on empty DB
    ids = db.list_all_ids()
    assert len(ids) == 0

    # Get count on empty DB
    count = db.get_vector_count()
    assert count == 0


@pytest.mark.slow
@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_large_batch_operations(provider_fixture, request):
    """Test with large batch of vectors (1000+)."""
    db = request.getfixturevalue(provider_fixture)

    # Generate 1000 random vectors
    batch_size = 1000
    vectors_with_meta = [
        (np.random.randn(128).astype(np.float32), {"index": i})
        for i in range(batch_size)
    ]

    start_time = time.time()
    ids = db.add_vectors_batch(vectors_with_meta, normalize=True)
    elapsed = time.time() - start_time

    assert len(ids) == batch_size
    assert db.get_vector_count() == batch_size

    print(f"\n  {provider_fixture}: Added {batch_size} vectors in {elapsed:.2f}s ({batch_size/elapsed:.0f} ops/sec)")


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_high_dimensional_vectors(provider_fixture, request):
    """Test with high-dimensional vectors (OpenAI embedding size)."""
    db = request.getfixturevalue(provider_fixture)

    # 1536-dimensional vector (OpenAI ada-002 size)
    high_dim_vector = np.random.randn(1536).astype(np.float32)

    vec_id = db.add_vector(high_dim_vector, {"test": "high_dim"}, normalize=True)
    assert vec_id is not None

    # Search
    results = db.top_cosine_similarity(high_dim_vector, top_n=1)
    assert len(results) == 1
    assert results[0][2] > 0.99  # Should find itself


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_zero_vectors(provider_fixture, request):
    """Test with zero vectors."""
    db = request.getfixturevalue(provider_fixture)

    zero_vec = np.zeros(3, dtype=np.float32)

    # Should handle zero vector (normalization returns zero for zero vector)
    vec_id = db.add_vector(zero_vec, {"test": "zero"}, normalize=True)
    assert vec_id is not None


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_special_metadata_characters(provider_fixture, request, sample_vectors):
    """Test metadata with special characters and Unicode."""
    db = request.getfixturevalue(provider_fixture)

    special_metadata = {
        "text": "Unicode test: 中文, العربية, עברית, 日本語",
        "special_chars": "!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/~`",
        "emoji": "😀🎉🚀",
        "newlines": "line1\nline2\nline3"
    }

    vec_id = db.add_vector(sample_vectors['v1'], special_metadata, normalize=True)

    # Retrieve and verify
    vec, meta = db.get_vector_by_id(vec_id)
    assert meta['emoji'] == "😀🎉🚀"
    assert "中文" in meta['text']


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_empty_metadata(provider_fixture, request, sample_vectors):
    """Test with empty and None metadata."""
    db = request.getfixturevalue(provider_fixture)

    # Empty dict
    vec_id1 = db.add_vector(sample_vectors['v1'], {}, normalize=True)
    assert vec_id1 is not None

    # None metadata - should be handled
    vec_id2 = db.add_vector(sample_vectors['v2'], None, normalize=True)
    assert vec_id2 is not None


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_non_dict_metadata(provider_fixture, request, sample_vectors):
    """Test with non-dictionary metadata."""
    db = request.getfixturevalue(provider_fixture)

    # String metadata
    vec_id1 = db.add_vector(sample_vectors['v1'], "string metadata", normalize=True)
    assert vec_id1 is not None

    # Number metadata
    vec_id2 = db.add_vector(sample_vectors['v2'], 42, normalize=True)
    assert vec_id2 is not None

    # List metadata
    vec_id3 = db.add_vector(sample_vectors['v3'], ["item1", "item2"], normalize=True)
    assert vec_id3 is not None


# ==================== Test Suite 5: Error Handling ====================

@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_dimension_mismatch_all_providers(provider_fixture, request):
    """Test DimensionMismatchError is raised correctly."""
    db = request.getfixturevalue(provider_fixture)

    # Add first vector (3D)
    db.add_vector(np.array([1.0, 0.0, 0.0], dtype=np.float32), {"test": "data"})

    # Try to add 2D vector (should fail)
    with pytest.raises(DimensionMismatchError):
        db.add_vector(np.array([1.0, 0.0], dtype=np.float32), {"test": "data"})

    # Try to search with wrong dimension
    with pytest.raises(DimensionMismatchError):
        db.top_cosine_similarity(np.array([1.0, 0.0], dtype=np.float32))


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_nonexistent_vector_operations(provider_fixture, request, sample_vectors):
    """Test operations on non-existent vectors."""
    db = request.getfixturevalue(provider_fixture)

    fake_id = "nonexistent-id-12345"

    # Get non-existent
    result = db.get_vector_by_id(fake_id)
    assert result is None

    # Update non-existent
    success = db.update_vector(fake_id, new_vector=sample_vectors['v1'])
    assert success is False

    # Delete non-existent (should not raise, just return False or succeed silently)
    # Behavior may vary, but shouldn't crash
    try:
        db.delete_vector(fake_id)
    except Exception as e:
        # Should be a VectorDB exception, not a crash
        assert isinstance(e, (VectorDBOperationError, VectorNotFoundError))


# ==================== Test Suite 6: Provider-Specific Features ====================

def test_local_compression(local_db, sample_vectors):
    """Test LOCAL provider compression feature."""
    # Add vectors
    for vec in sample_vectors.values():
        local_db.add_vector(vec, {"test": "data"}, normalize=True)

    # Compress to float16
    ratio = local_db.compress_vectors(bits=16)

    # Should have compression ratio > 1
    assert ratio >= 1.0

    # Data should still be accessible
    assert local_db.get_vector_count() == len(sample_vectors)


def test_local_save_load_persistence(temp_dir, sample_vectors):
    """Test LOCAL provider save/load cycle."""
    # Create DB and add data
    db1 = VectorDB.create(provider=VectorProvider.LOCAL, db_folder=temp_dir)

    for vec in sample_vectors.values():
        db1.add_vector(vec, {"test": "data"}, normalize=True)

    # Save
    db1.save_to_disk("test_collection")

    # Create new DB and load
    db2 = VectorDB.create(provider=VectorProvider.LOCAL, db_folder=temp_dir)
    db2.load_from_disk("test_collection")

    # Verify data persisted
    assert db2.get_vector_count() == len(sample_vectors)


@pytest.mark.qdrant
def test_qdrant_optional_features(qdrant_db, sample_vectors):
    """Test QDRANT optional features behavior."""
    # compress_vectors should return 1.0 (not supported)
    ratio = qdrant_db.compress_vectors(bits=16)
    assert ratio == 1.0

    # save_to_disk/load_from_disk should not crash
    qdrant_db.save_to_disk("test")
    qdrant_db.load_from_disk("test")


# ==================== Test Suite 7: Performance & Accuracy ====================

@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_normalization_consistency(provider_fixture, request):
    """Verify normalized vectors behave correctly."""
    db = request.getfixturevalue(provider_fixture)

    # Add unnormalized vector with normalization
    unnormalized = np.array([3.0, 4.0, 0.0], dtype=np.float32)  # Length = 5
    vec_id = db.add_vector(unnormalized, {"test": "data"}, normalize=True)

    # Retrieve
    vec, meta = db.get_vector_by_id(vec_id)

    # Should be normalized (length ≈ 1)
    length = np.linalg.norm(vec)
    assert abs(length - 1.0) < 0.01


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_search_accuracy(provider_fixture, request):
    """Test search returns accurate similarity scores."""
    db = request.getfixturevalue(provider_fixture)

    # Create orthogonal vectors
    v1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v2 = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    v3 = np.array([0.0, 0.0, 1.0], dtype=np.float32)

    db.add_vector(v1, {"name": "v1"}, normalize=True)
    db.add_vector(v2, {"name": "v2"}, normalize=True)
    db.add_vector(v3, {"name": "v3"}, normalize=True)

    # Search for v1
    results = db.top_cosine_similarity(v1, top_n=3)

    # First result should be v1 itself (similarity ≈ 1.0)
    assert results[0][2] > 0.99

    # Other results should have lower similarity (orthogonal = 0)
    assert results[1][2] < 0.1
    assert results[2][2] < 0.1


@pytest.mark.parametrize("provider_fixture", ["local_db", "qdrant_db"])
def test_batch_vs_single_consistency(provider_fixture, request, sample_vectors, sample_metadata):
    """Verify batch add produces same results as individual adds."""
    db = request.getfixturevalue(provider_fixture)

    # Add via batch
    vectors_with_meta = [
        (sample_vectors['v1'], sample_metadata[0]),
        (sample_vectors['v2'], sample_metadata[1]),
    ]
    batch_ids = db.add_vectors_batch(vectors_with_meta, normalize=True)

    # Search
    batch_results = db.top_cosine_similarity(sample_vectors['v1'], top_n=2)

    # Clear and add individually
    db.clear_database()

    individual_ids = []
    for vec, meta in vectors_with_meta:
        vec_id = db.add_vector(vec, meta, normalize=True)
        individual_ids.append(vec_id)

    # Search again
    individual_results = db.top_cosine_similarity(sample_vectors['v1'], top_n=2)

    # Results should be consistent
    assert len(batch_results) == len(individual_results)
    for (_, _, score1), (_, _, score2) in zip(batch_results, individual_results):
        assert abs(score1 - score2) < 0.01


# ==================== Test Suite 8: Provider Switching ====================

def test_factory_pattern_switching(temp_dir):
    """Test switching between providers via factory."""
    # Create LOCAL
    db_local = VectorDB.create(provider=VectorProvider.LOCAL, db_folder=temp_dir)
    assert db_local.provider == VectorProvider.LOCAL

    # Try to create QDRANT (may skip if not available)
    try:
        db_qdrant = VectorDB.create(
            provider=VectorProvider.QDRANT,
            url='localhost',
            collection_name='test'
        )
        assert db_qdrant.provider == VectorProvider.QDRANT
    except (VectorDBConnectionError, Exception):
        pytest.skip("Qdrant not available for switching test")


# ==================== Production Readiness Summary ====================

def test_production_readiness_checklist(local_db, sample_vectors):
    """Comprehensive checklist for production readiness."""
    print("\n" + "="*60)
    print("PRODUCTION READINESS CHECKLIST")
    print("="*60)

    checks = []

    # 1. Basic CRUD operations
    try:
        vec_id = local_db.add_vector(sample_vectors['v1'], {"test": "data"})
        local_db.update_vector(vec_id, new_metadata={"test": "updated"})
        local_db.delete_vector(vec_id)
        checks.append(("Basic CRUD operations", True))
    except Exception as e:
        checks.append(("Basic CRUD operations", False))

    # 2. Search operations
    try:
        for vec in list(sample_vectors.values())[:3]:
            local_db.add_vector(vec, {"test": "data"}, normalize=True)
        results = local_db.top_cosine_similarity(sample_vectors['v1'], top_n=2)
        checks.append(("Search operations", len(results) > 0))
    except Exception as e:
        checks.append(("Search operations", False))

    # 3. Error handling
    try:
        local_db.add_vector(np.array([1.0, 0.0], dtype=np.float32), {"test": "data"})
        checks.append(("Dimension validation", False))  # Should have raised error
    except DimensionMismatchError:
        checks.append(("Dimension validation", True))

    # 4. Stats reporting
    try:
        stats = local_db.get_stats()
        assert_stats_valid(stats, "LOCAL")
        checks.append(("Stats reporting", True))
    except Exception as e:
        checks.append(("Stats reporting", False))

    # Print results
    print("\n")
    for check_name, passed in checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {check_name}")

    print("\n" + "="*60)

    all_passed = all(passed for _, passed in checks)
    if all_passed:
        print("STATUS: PRODUCTION READY")
    else:
        print("STATUS: NOT READY - Issues found")
    print("="*60 + "\n")

    assert all_passed, "Production readiness check failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
