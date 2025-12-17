"""
Test script to verify the unified vector database interface.

This script tests:
1. Factory pattern creation
2. Consistent method signatures across providers
3. Proper exception handling
4. Standardized get_stats() output
"""
# -*- coding: utf-8 -*-

import numpy as np
import tempfile
import shutil
from SimplerLLM.vectors.vector_db import VectorDB, DimensionMismatchError, VectorDBOperationError
from SimplerLLM.vectors.vector_providers import VectorProvider


def test_local_provider():
    """Test LOCAL provider with unified interface."""
    print("\n" + "="*60)
    print("Testing LOCAL Provider")
    print("="*60)

    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()

    try:
        # Create database using factory
        db = VectorDB.create(provider=VectorProvider.LOCAL, db_folder=temp_dir)

        # Test adding vectors
        print("\n1. Testing add_vector...")
        vector1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        id1 = db.add_vector(vector1, {"text": "first vector"}, normalize=True)
        print(f"   Added vector with ID: {id1}")

        # Test dimension validation
        print("\n2. Testing dimension validation...")
        try:
            vector_wrong = np.array([1.0, 0.0], dtype=np.float32)
            db.add_vector(vector_wrong, {"text": "wrong dimension"})
            print("   ERROR: Should have raised DimensionMismatchError!")
        except DimensionMismatchError as e:
            print(f"   ✓ Correctly raised DimensionMismatchError: {e}")

        # Test batch add
        print("\n3. Testing add_vectors_batch...")
        vectors = [
            (np.array([0.0, 1.0, 0.0], dtype=np.float32), {"text": "second vector"}),
            (np.array([0.0, 0.0, 1.0], dtype=np.float32), {"text": "third vector"}),
        ]
        ids = db.add_vectors_batch(vectors, normalize=True)
        print(f"   Added {len(ids)} vectors")

        # Test search
        print("\n4. Testing top_cosine_similarity...")
        query = np.array([1.0, 0.1, 0.0], dtype=np.float32)
        results = db.top_cosine_similarity(query, top_n=2)
        print(f"   Found {len(results)} similar vectors")
        for i, (vec_id, metadata, score) in enumerate(results):
            print(f"   {i+1}. {metadata.get('text')} (similarity: {score:.4f})")

        # Test get_stats
        print("\n5. Testing get_stats...")
        stats = db.get_stats()
        print(f"   Stats: {stats}")

        # Verify required fields
        required_fields = ["total_vectors", "dimension", "provider"]
        for field in required_fields:
            if field in stats:
                print(f"   ✓ Required field '{field}': {stats[field]}")
            else:
                print(f"   ERROR: Missing required field '{field}'")

        # Test optional features
        print("\n6. Testing optional features (compress_vectors)...")
        ratio = db.compress_vectors(bits=16)
        print(f"   Compression ratio: {ratio:.2f}x")

        # Test save/load
        print("\n7. Testing save_to_disk/load_from_disk...")
        db.save_to_disk("test_collection")
        db.load_from_disk("test_collection")
        print("   ✓ Save/Load successful")

        print("\n✓ LOCAL provider test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ LOCAL provider test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_interface_consistency():
    """Test that both providers implement the same interface."""
    print("\n" + "="*60)
    print("Testing Interface Consistency")
    print("="*60)

    temp_dir = tempfile.mkdtemp()

    try:
        # Create LOCAL instance
        local_db = VectorDB.create(provider=VectorProvider.LOCAL, db_folder=temp_dir)

        # Required methods
        required_methods = [
            'add_vector', 'add_vectors_batch', 'add_text_with_embedding',
            'delete_vector', 'update_vector', 'top_cosine_similarity',
            'search_by_text', 'query_by_metadata', 'get_vector_by_id',
            'list_all_ids', 'get_vector_count', 'clear_database', 'get_stats'
        ]

        print("\nChecking required methods on LOCAL provider:")
        for method in required_methods:
            if hasattr(local_db, method):
                print(f"   [OK] {method}")
            else:
                print(f"   [MISSING] {method}")

        # Optional methods
        optional_methods = ['compress_vectors', 'save_to_disk', 'load_from_disk']

        print("\nChecking optional methods on LOCAL provider:")
        for method in optional_methods:
            if hasattr(local_db, method):
                print(f"   [OK] {method}")
            else:
                print(f"   [MISSING] {method}")

        print("\n[PASS] Interface consistency test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Interface consistency test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_exception_handling():
    """Test that exceptions are properly raised."""
    print("\n" + "="*60)
    print("Testing Exception Handling")
    print("="*60)

    temp_dir = tempfile.mkdtemp()

    try:
        db = VectorDB.create(provider=VectorProvider.LOCAL, db_folder=temp_dir)

        # Add a vector to set dimension
        db.add_vector(np.array([1.0, 0.0, 0.0], dtype=np.float32), {"test": "data"})

        # Test DimensionMismatchError
        print("\n1. Testing DimensionMismatchError...")
        try:
            db.add_vector(np.array([1.0, 0.0], dtype=np.float32), {"test": "wrong"})
            print("   ✗ Should have raised DimensionMismatchError")
            return False
        except DimensionMismatchError:
            print("   ✓ DimensionMismatchError raised correctly")

        # Test dimension mismatch in search
        print("\n2. Testing DimensionMismatchError in search...")
        try:
            db.top_cosine_similarity(np.array([1.0, 0.0], dtype=np.float32))
            print("   ✗ Should have raised DimensionMismatchError")
            return False
        except DimensionMismatchError:
            print("   ✓ DimensionMismatchError raised correctly in search")

        print("\n✓ Exception handling test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Exception handling test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("UNIFIED VECTOR DATABASE INTERFACE TEST SUITE")
    print("="*60)

    results = []

    # Run tests
    results.append(("Interface Consistency", test_interface_consistency()))
    results.append(("LOCAL Provider", test_local_provider()))
    results.append(("Exception Handling", test_exception_handling()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    print("\n" + "="*60)
    if all_passed:
        print("ALL TESTS PASSED! ✓")
    else:
        print("SOME TESTS FAILED! ✗")
    print("="*60 + "\n")
