"""
Tests for LLM-based clustering and retrieval modules.

These tests verify the core functionality of the clustering and retrieval system.
"""

import pytest
from SimplerLLM.language.llm_clustering import (
    LLMClusterer,
    ChunkReference,
    ClusteringConfig,
    TreeConfig,
    Cluster,
    ClusterMetadata
)
from SimplerLLM.language.llm_retrieval import (
    LLMRetriever,
    RetrievalConfig
)


# Sample test data
SAMPLE_CHUNKS = [
    "Neural networks are composed of layers of interconnected nodes that process information.",
    "The transformer architecture uses self-attention mechanisms for processing sequences.",
    "AI safety focuses on ensuring AI systems behave in beneficial ways.",
    "Value alignment ensures AI goals match human values and intentions.",
    "Convolutional neural networks are specialized for image processing tasks.",
    "Supervised learning trains models on labeled data to make predictions.",
    "The alignment problem is central to AI safety research.",
    "Backpropagation computes gradients for training neural networks.",
]


class MockLLM:
    """Mock LLM for testing without API calls."""

    def __init__(self):
        self.call_count = 0

    def generate_response(self, model, prompt, max_tokens=None):
        """Mock generate_response that returns structured outputs."""
        self.call_count += 1

        # Import models here to avoid circular imports
        from SimplerLLM.language.llm_clustering.models import (
            ChunkMatchingResult,
            ClusterMetadata,
            ClusterMatch
        )

        # Simple logic to simulate clustering behavior
        if "EXISTING CLUSTERS" in prompt:
            # This is a chunk matching request
            if "neural network" in prompt.lower():
                # Match to neural networks cluster
                return ChunkMatchingResult(
                    matches=[
                        ClusterMatch(
                            cluster_id="cluster_1",
                            cluster_name="Neural Networks",
                            confidence=0.85,
                            reasoning="Discusses neural network concepts"
                        )
                    ],
                    create_new_cluster=False,
                    confidence_threshold_used=0.7
                )
            elif "safety" in prompt.lower() or "alignment" in prompt.lower():
                # Match to AI safety cluster
                return ChunkMatchingResult(
                    matches=[
                        ClusterMatch(
                            cluster_id="cluster_2",
                            cluster_name="AI Safety",
                            confidence=0.82,
                            reasoning="Discusses AI safety concepts"
                        )
                    ],
                    create_new_cluster=False,
                    confidence_threshold_used=0.7
                )
            else:
                # Create new cluster
                return ChunkMatchingResult(
                    matches=[],
                    create_new_cluster=True,
                    new_cluster_metadata=ClusterMetadata(
                        canonical_name="General Topics",
                        canonical_tags=["general", "ml"],
                        canonical_keywords=["machine learning", "AI"],
                        description="General machine learning topics"
                    ),
                    confidence_threshold_used=0.7
                )
        else:
            # This is a metadata generation request
            return ClusterMetadata(
                canonical_name="Test Cluster",
                canonical_tags=["test", "cluster"],
                canonical_keywords=["test", "keyword"],
                description="Test cluster description",
                topic="Test Topic"
            )


class TestChunkReference:
    """Test ChunkReference model."""

    def test_chunk_reference_creation(self):
        chunk = ChunkReference(
            chunk_id=0,
            text="Test chunk text",
            metadata={"source": "test.txt"}
        )
        assert chunk.chunk_id == 0
        assert chunk.text == "Test chunk text"
        assert chunk.metadata["source"] == "test.txt"

    def test_chunk_reference_validation(self):
        with pytest.raises(ValueError):
            ChunkReference(chunk_id=0, text="")  # Empty text should fail


class TestClusteringConfig:
    """Test ClusteringConfig model."""

    def test_default_config(self):
        config = ClusteringConfig()
        assert config.confidence_threshold == 0.7
        assert config.max_clusters_per_chunk == 3
        assert config.max_total_clusters == 30
        assert config.batch_size == 5

    def test_custom_config(self):
        config = ClusteringConfig(
            confidence_threshold=0.8,
            max_clusters_per_chunk=2,
            batch_size=10
        )
        assert config.confidence_threshold == 0.8
        assert config.max_clusters_per_chunk == 2
        assert config.batch_size == 10


class TestCluster:
    """Test Cluster model."""

    def test_cluster_creation(self):
        metadata = ClusterMetadata(
            canonical_name="Test Cluster",
            canonical_tags=["test"],
            canonical_keywords=["keyword"],
            description="Test description"
        )

        chunk = ChunkReference(chunk_id=0, text="Test")

        cluster = Cluster(
            id="cluster_1",
            level=0,
            metadata=metadata,
            chunks=[chunk]
        )

        assert cluster.id == "cluster_1"
        assert cluster.level == 0
        assert cluster.is_leaf()
        assert not cluster.is_parent()
        assert len(cluster.chunks) == 1

    def test_add_chunk(self):
        metadata = ClusterMetadata(
            canonical_name="Test",
            canonical_tags=[],
            canonical_keywords=[],
            description=""
        )

        cluster = Cluster(id="test", level=0, metadata=metadata)
        chunk = ChunkReference(chunk_id=0, text="Test")

        cluster.add_chunk(chunk)
        assert cluster.chunk_count == 1
        assert len(cluster.chunks) == 1

    def test_parent_cluster(self):
        metadata = ClusterMetadata(
            canonical_name="Parent",
            canonical_tags=[],
            canonical_keywords=[],
            description=""
        )

        cluster = Cluster(
            id="parent",
            level=1,
            metadata=metadata,
            child_clusters=["child_1", "child_2"]
        )

        assert cluster.is_parent()
        assert not cluster.is_leaf()
        assert len(cluster.child_clusters) == 2


class TestLLMClusterer:
    """Test LLMClusterer functionality."""

    def test_clusterer_initialization(self):
        mock_llm = MockLLM()
        clusterer = LLMClusterer(mock_llm)

        assert clusterer.llm == mock_llm
        assert isinstance(clusterer.clustering_config, ClusteringConfig)
        assert isinstance(clusterer.tree_config, TreeConfig)

    def test_flat_clustering(self):
        """Test basic flat clustering without hierarchy."""
        mock_llm = MockLLM()
        config = ClusteringConfig(
            batch_size=2,
            max_total_clusters=10
        )

        clusterer = LLMClusterer(mock_llm, clustering_config=config)

        # Create test chunks
        chunks = [
            ChunkReference(chunk_id=i, text=text)
            for i, text in enumerate(SAMPLE_CHUNKS[:4])
        ]

        result = clusterer.cluster_flat_only(chunks)

        assert result is not None
        assert len(result.clusters) > 0
        assert result.total_chunks_processed == len(chunks)
        assert result.total_llm_calls > 0

    def test_chunk_to_cluster_mapping(self):
        """Test that chunk-to-cluster mapping is created correctly."""
        mock_llm = MockLLM()
        clusterer = LLMClusterer(mock_llm)

        chunks = [
            ChunkReference(chunk_id=i, text=text)
            for i, text in enumerate(SAMPLE_CHUNKS[:3])
        ]

        result = clusterer.cluster_flat_only(chunks)

        # Check that each chunk is mapped to at least one cluster
        for chunk in chunks:
            assert chunk.chunk_id in result.chunk_to_clusters
            cluster_ids = result.chunk_to_clusters[chunk.chunk_id]
            assert len(cluster_ids) > 0


class TestRetrievalConfig:
    """Test RetrievalConfig model."""

    def test_default_config(self):
        config = RetrievalConfig()
        assert config.top_k == 3
        assert config.confidence_threshold == 0.7
        assert config.include_reasoning is True

    def test_custom_config(self):
        config = RetrievalConfig(
            top_k=5,
            confidence_threshold=0.8,
            explore_multiple_paths=True
        )
        assert config.top_k == 5
        assert config.confidence_threshold == 0.8
        assert config.explore_multiple_paths is True


class TestTreeConfig:
    """Test TreeConfig model."""

    def test_default_config(self):
        config = TreeConfig()
        assert config.max_children_per_parent == 10
        assert config.max_clusters_per_level == 10
        assert config.auto_depth is True
        assert config.max_depth == 4


class TestClusterTree:
    """Test ClusterTree model."""

    def test_tree_creation(self):
        tree = TreeConfig()
        assert tree.max_children_per_parent == 10

    def test_add_and_get_cluster(self):
        from SimplerLLM.language.llm_clustering.models import ClusterTree

        tree = ClusterTree()
        metadata = ClusterMetadata(
            canonical_name="Test",
            canonical_tags=[],
            canonical_keywords=[],
            description=""
        )

        cluster = Cluster(id="test_1", level=0, metadata=metadata)
        tree.add_cluster(cluster)

        retrieved = tree.get_cluster("test_1")
        assert retrieved is not None
        assert retrieved.id == "test_1"

    def test_get_clusters_at_level(self):
        from SimplerLLM.language.llm_clustering.models import ClusterTree

        tree = ClusterTree()
        metadata = ClusterMetadata(
            canonical_name="Test",
            canonical_tags=[],
            canonical_keywords=[],
            description=""
        )

        # Add clusters at different levels
        cluster0 = Cluster(id="c0", level=0, metadata=metadata)
        cluster1 = Cluster(id="c1", level=1, metadata=metadata)
        cluster2 = Cluster(id="c2", level=0, metadata=metadata)

        tree.add_cluster(cluster0)
        tree.add_cluster(cluster1)
        tree.add_cluster(cluster2)

        level_0_clusters = tree.get_clusters_at_level(0)
        assert len(level_0_clusters) == 2

        level_1_clusters = tree.get_clusters_at_level(1)
        assert len(level_1_clusters) == 1


# Integration test would require real LLM, skip for now
@pytest.mark.skip(reason="Requires real LLM instance and API key")
class TestIntegration:
    """Integration tests with real LLM (skipped by default)."""

    def test_full_clustering_and_retrieval(self):
        """Full end-to-end test with real LLM."""
        # This would test the full pipeline with a real LLM
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
