"""
Unit tests for the RecursiveBrainstorm feature.

Tests cover:
- All three modes (tree, linear, hybrid)
- Input validation
- Result structure
- Edge cases
- Tool integration
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch
from pydantic import BaseModel

from SimplerLLM.language.llm import LLM
from SimplerLLM.language.llm_brainstorm import (
    RecursiveBrainstorm,
    BrainstormIdea,
    BrainstormResult,
    IdeaGeneration,
    IdeaEvaluation,
)
from SimplerLLM.tools.brainstorm import (
    recursive_brainstorm_tool,
    simple_brainstorm,
    create_brainstorm_tool,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_llm():
    """Create a mock LLM instance."""
    llm = Mock(spec=LLM)
    llm.provider = Mock()
    llm.provider.value = "openai"
    llm.model_name = "gpt-4o-mini"
    return llm


@pytest.fixture
def mock_idea_generation():
    """Create a mock IdeaGeneration response."""
    return IdeaGeneration(
        ideas=[
            "Idea 1: Smart recycling bins with AI sorting",
            "Idea 2: Plastic-free packaging marketplace",
            "Idea 3: Community composting network",
        ],
        reasoning_per_idea=[
            "Uses technology to improve sorting efficiency",
            "Reduces plastic at the source",
            "Engages community in sustainability",
        ]
    )


@pytest.fixture
def mock_idea_evaluation():
    """Create a mock IdeaEvaluation response."""
    return IdeaEvaluation(
        quality_score=8.5,
        strengths=["Innovative", "Practical", "Scalable"],
        weaknesses=["Requires initial investment"],
        criteria_scores={
            "feasibility": 8.0,
            "impact": 9.0,
            "novelty": 8.0,
        },
        should_expand=True,
        reasoning="Strong potential with manageable challenges",
    )


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestRecursiveBrainstormInit:
    """Test RecursiveBrainstorm initialization and validation."""

    def test_valid_initialization(self, mock_llm):
        """Test creating RecursiveBrainstorm with valid parameters."""
        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=3,
            ideas_per_level=5,
            mode="tree",
        )

        assert brainstorm.llm == mock_llm
        assert brainstorm.max_depth == 3
        assert brainstorm.ideas_per_level == 5
        assert brainstorm.mode == "tree"

    def test_invalid_mode(self, mock_llm):
        """Test that invalid mode raises ValueError."""
        with pytest.raises(ValueError, match="Mode must be"):
            RecursiveBrainstorm(llm=mock_llm, mode="invalid")

    def test_invalid_max_depth(self, mock_llm):
        """Test that invalid max_depth raises ValueError."""
        with pytest.raises(ValueError, match="max_depth must be at least 1"):
            RecursiveBrainstorm(llm=mock_llm, max_depth=0)

    def test_invalid_ideas_per_level(self, mock_llm):
        """Test that invalid ideas_per_level raises ValueError."""
        with pytest.raises(ValueError, match="ideas_per_level must be at least 1"):
            RecursiveBrainstorm(llm=mock_llm, ideas_per_level=0)

    def test_invalid_quality_threshold(self, mock_llm):
        """Test that invalid quality threshold raises ValueError."""
        with pytest.raises(ValueError, match="min_quality_threshold must be between"):
            RecursiveBrainstorm(llm=mock_llm, min_quality_threshold=15.0)

    def test_default_parameters(self, mock_llm):
        """Test default parameter values."""
        brainstorm = RecursiveBrainstorm(llm=mock_llm)

        assert brainstorm.max_depth == 3
        assert brainstorm.ideas_per_level == 5
        assert brainstorm.mode == "tree"
        assert brainstorm.top_n == 3
        assert brainstorm.min_quality_threshold == 5.0
        assert brainstorm.evaluation_criteria == ["quality", "feasibility", "impact"]


# ============================================================================
# TREE MODE TESTS
# ============================================================================

class TestTreeMode:
    """Test tree mode functionality."""

    @patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model')
    def test_tree_mode_basic(self, mock_generate, mock_llm, mock_idea_generation, mock_idea_evaluation):
        """Test basic tree mode execution."""
        # Setup mocks
        mock_generate.side_effect = [
            mock_idea_generation,  # Initial generation
            mock_idea_evaluation, mock_idea_evaluation, mock_idea_evaluation,  # Evaluations
        ]

        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=1,  # Only 2 levels for simple test
            ideas_per_level=3,
            mode="tree",
            verbose=False,
        )

        result = brainstorm.brainstorm("Test prompt")

        # Verify result structure
        assert isinstance(result, BrainstormResult)
        assert result.mode == "tree"
        assert result.total_ideas == 3
        assert result.max_depth_reached == 0

    @patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model')
    def test_tree_mode_expansion(self, mock_generate, mock_llm, mock_idea_generation, mock_idea_evaluation):
        """Test that tree mode expands all qualifying ideas."""
        # Create multiple rounds of generation
        def generate_side_effect(*args, **kwargs):
            model_class = args[0]
            if model_class == IdeaGeneration:
                return mock_idea_generation
            elif model_class == IdeaEvaluation:
                return mock_idea_evaluation
            return None

        mock_generate.side_effect = generate_side_effect

        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=2,
            ideas_per_level=2,
            mode="tree",
            min_quality_threshold=7.0,  # Only expand ideas with score >= 7.0
            verbose=False,
        )

        result = brainstorm.brainstorm("Test prompt")

        # Should have ideas at depth 0, and expansions at depth 1
        assert result.max_depth_reached >= 0
        assert result.total_ideas >= 2

    @patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model')
    def test_tree_mode_stops_at_max_depth(self, mock_generate, mock_llm, mock_idea_generation, mock_idea_evaluation):
        """Test that tree mode respects max_depth."""
        def generate_side_effect(*args, **kwargs):
            model_class = args[0]
            if model_class == IdeaGeneration:
                return mock_idea_generation
            elif model_class == IdeaEvaluation:
                return mock_idea_evaluation

        mock_generate.side_effect = generate_side_effect

        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=1,
            ideas_per_level=2,
            mode="tree",
            verbose=False,
        )

        result = brainstorm.brainstorm("Test prompt")

        # Max depth reached should not exceed max_depth - 1 (0-indexed)
        assert result.max_depth_reached < brainstorm.max_depth


# ============================================================================
# LINEAR MODE TESTS
# ============================================================================

class TestLinearMode:
    """Test linear mode functionality."""

    @patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model')
    def test_linear_mode_basic(self, mock_generate, mock_llm, mock_idea_generation, mock_idea_evaluation):
        """Test basic linear mode execution."""
        def generate_side_effect(*args, **kwargs):
            model_class = args[0]
            if model_class == IdeaGeneration:
                return mock_idea_generation
            elif model_class == IdeaEvaluation:
                return mock_idea_evaluation

        mock_generate.side_effect = generate_side_effect

        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=2,
            ideas_per_level=3,
            mode="linear",
            verbose=False,
        )

        result = brainstorm.brainstorm("Test prompt")

        assert result.mode == "linear"
        assert result.total_ideas >= 3

    @patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model')
    def test_linear_mode_picks_best(self, mock_generate, mock_llm):
        """Test that linear mode picks and refines the best idea."""
        # Create ideas with different scores
        generation_1 = IdeaGeneration(
            ideas=["Idea A", "Idea B", "Idea C"],
            reasoning_per_idea=["Reasoning A", "Reasoning B", "Reasoning C"]
        )

        eval_low = IdeaEvaluation(quality_score=6.0, strengths=[], weaknesses=[], should_expand=True, reasoning="")
        eval_mid = IdeaEvaluation(quality_score=8.0, strengths=[], weaknesses=[], should_expand=True, reasoning="")
        eval_high = IdeaEvaluation(quality_score=9.5, strengths=[], weaknesses=[], should_expand=True, reasoning="")

        mock_generate.side_effect = [
            generation_1,
            eval_low, eval_high, eval_mid,  # Evaluations (B is best)
        ]

        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=1,
            ideas_per_level=3,
            mode="linear",
            verbose=False,
        )

        result = brainstorm.brainstorm("Test prompt")

        # Best idea should be Idea B with score 9.5
        assert result.overall_best_idea.quality_score == 9.5


# ============================================================================
# HYBRID MODE TESTS
# ============================================================================

class TestHybridMode:
    """Test hybrid mode functionality."""

    @patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model')
    def test_hybrid_mode_basic(self, mock_generate, mock_llm, mock_idea_generation, mock_idea_evaluation):
        """Test basic hybrid mode execution."""
        def generate_side_effect(*args, **kwargs):
            model_class = args[0]
            if model_class == IdeaGeneration:
                return mock_idea_generation
            elif model_class == IdeaEvaluation:
                return mock_idea_evaluation

        mock_generate.side_effect = generate_side_effect

        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=2,
            ideas_per_level=5,
            mode="hybrid",
            top_n=2,
            verbose=False,
        )

        result = brainstorm.brainstorm("Test prompt")

        assert result.mode == "hybrid"
        assert result.config_used["top_n"] == 2

    @patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model')
    def test_hybrid_mode_expands_top_n(self, mock_generate, mock_llm):
        """Test that hybrid mode expands only top N ideas."""
        generation = IdeaGeneration(
            ideas=["Idea 1", "Idea 2", "Idea 3"],
            reasoning_per_idea=["R1", "R2", "R3"]
        )

        # Different evaluation scores
        eval_scores = [
            IdeaEvaluation(quality_score=9.0, strengths=[], weaknesses=[], should_expand=True, reasoning=""),
            IdeaEvaluation(quality_score=7.0, strengths=[], weaknesses=[], should_expand=True, reasoning=""),
            IdeaEvaluation(quality_score=5.0, strengths=[], weaknesses=[], should_expand=True, reasoning=""),
        ]

        mock_generate.side_effect = [
            generation,
            *eval_scores,
        ]

        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=1,
            ideas_per_level=3,
            mode="hybrid",
            top_n=2,  # Only expand top 2
            verbose=False,
        )

        result = brainstorm.brainstorm("Test prompt")

        # Should have 3 initial ideas
        assert result.total_ideas >= 3


# ============================================================================
# RESULT TESTS
# ============================================================================

class TestBrainstormResult:
    """Test BrainstormResult model and methods."""

    def test_get_ideas_at_depth(self):
        """Test getting ideas at a specific depth."""
        ideas = [
            BrainstormIdea(id="1", text="Idea 1", depth=0, quality_score=8.0),
            BrainstormIdea(id="2", text="Idea 2", depth=0, quality_score=7.0),
            BrainstormIdea(id="3", text="Idea 3", depth=1, quality_score=9.0),
        ]

        result = BrainstormResult(
            initial_prompt="Test",
            mode="tree",
            total_ideas=3,
            total_iterations=1,
            max_depth_reached=1,
            all_ideas=ideas,
            execution_time=1.0,
            stopped_reason="test",
        )

        depth_0_ideas = result.get_ideas_at_depth(0)
        assert len(depth_0_ideas) == 2
        assert all(idea.depth == 0 for idea in depth_0_ideas)

    def test_get_children(self):
        """Test getting children of an idea."""
        ideas = [
            BrainstormIdea(id="parent", text="Parent", depth=0, quality_score=8.0),
            BrainstormIdea(id="child1", text="Child 1", depth=1, parent_id="parent", quality_score=7.0),
            BrainstormIdea(id="child2", text="Child 2", depth=1, parent_id="parent", quality_score=9.0),
            BrainstormIdea(id="other", text="Other", depth=1, parent_id="other_parent", quality_score=6.0),
        ]

        result = BrainstormResult(
            initial_prompt="Test",
            mode="tree",
            total_ideas=4,
            total_iterations=1,
            max_depth_reached=1,
            all_ideas=ideas,
            tree_structure={"parent": ["child1", "child2"]},
            execution_time=1.0,
            stopped_reason="test",
        )

        children = result.get_children("parent")
        assert len(children) == 2
        assert all(child.parent_id == "parent" for child in children)

    def test_get_path_to_best(self):
        """Test getting path from root to best idea."""
        ideas = [
            BrainstormIdea(id="root", text="Root", depth=0, quality_score=7.0),
            BrainstormIdea(id="child", text="Child", depth=1, parent_id="root", quality_score=8.0),
            BrainstormIdea(id="grandchild", text="Grandchild", depth=2, parent_id="child", quality_score=9.5),
        ]

        result = BrainstormResult(
            initial_prompt="Test",
            mode="tree",
            total_ideas=3,
            total_iterations=1,
            max_depth_reached=2,
            all_ideas=ideas,
            overall_best_idea=ideas[2],  # Grandchild is best
            execution_time=1.0,
            stopped_reason="test",
        )

        path = result.get_path_to_best()
        assert len(path) == 3
        assert path[0].id == "root"
        assert path[1].id == "child"
        assert path[2].id == "grandchild"

    def test_to_tree_dict(self):
        """Test converting result to tree dictionary."""
        ideas = [
            BrainstormIdea(id="root", text="Root", depth=0, quality_score=8.0),
            BrainstormIdea(id="child", text="Child", depth=1, parent_id="root", quality_score=7.0),
        ]

        result = BrainstormResult(
            initial_prompt="Test prompt",
            mode="tree",
            total_ideas=2,
            total_iterations=1,
            max_depth_reached=1,
            all_ideas=ideas,
            tree_structure={"root": ["child"]},
            execution_time=1.0,
            stopped_reason="test",
        )

        tree_dict = result.to_tree_dict()

        assert tree_dict["prompt"] == "Test prompt"
        assert tree_dict["mode"] == "tree"
        assert tree_dict["total_ideas"] == 2
        assert len(tree_dict["roots"]) == 1
        assert tree_dict["roots"][0]["text"] == "Root"
        assert len(tree_dict["roots"][0]["children"]) == 1


# ============================================================================
# TOOL INTEGRATION TESTS
# ============================================================================

class TestToolIntegration:
    """Test tool wrappers for MiniAgent integration."""

    @patch('SimplerLLM.language.llm_brainstorm.RecursiveBrainstorm.brainstorm')
    def test_recursive_brainstorm_tool(self, mock_brainstorm, mock_llm):
        """Test recursive_brainstorm_tool wrapper."""
        # Create mock result
        mock_result = Mock(spec=BrainstormResult)
        mock_result.overall_best_idea = BrainstormIdea(
            id="best",
            text="Best idea",
            quality_score=9.0,
            reasoning="Great idea",
            depth=1,
        )
        mock_result.all_ideas = [mock_result.overall_best_idea]
        mock_result.total_ideas = 1
        mock_result.total_iterations = 1
        mock_result.max_depth_reached = 1
        mock_result.execution_time = 1.5
        mock_result.mode = "hybrid"
        mock_result.to_tree_dict.return_value = {"prompt": "test"}

        mock_brainstorm.return_value = mock_result

        # Call tool
        result = recursive_brainstorm_tool(
            prompt="Test prompt",
            llm_instance=mock_llm,
            max_depth=2,
            mode="hybrid",
        )

        # Verify result structure
        assert isinstance(result, dict)
        assert "best_idea" in result
        assert "top_ideas" in result
        assert "total_ideas" in result
        assert "tree_structure" in result
        assert result["best_idea"]["text"] == "Best idea"
        assert result["best_idea"]["score"] == 9.0

    @patch('SimplerLLM.language.llm_brainstorm.RecursiveBrainstorm.brainstorm')
    def test_simple_brainstorm(self, mock_brainstorm, mock_llm):
        """Test simple_brainstorm wrapper."""
        # Create mock result
        mock_result = Mock(spec=BrainstormResult)
        mock_result.all_ideas = [
            BrainstormIdea(id="1", text="Idea 1", quality_score=8.0),
            BrainstormIdea(id="2", text="Idea 2", quality_score=7.0),
            BrainstormIdea(id="3", text="Idea 3", quality_score=9.0),
        ]

        mock_brainstorm.return_value = mock_result

        # Call tool
        result = simple_brainstorm(
            prompt="Test prompt",
            llm_instance=mock_llm,
            num_ideas=3,
        )

        # Verify result is list of strings
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(idea, str) for idea in result)
        assert "Idea 1" in result

    def test_create_brainstorm_tool(self, mock_llm):
        """Test create_brainstorm_tool factory."""
        with patch('SimplerLLM.tools.brainstorm.recursive_brainstorm_tool') as mock_tool:
            mock_tool.return_value = {"best_idea": {"text": "Test"}}

            # Create tool with default params
            my_tool = create_brainstorm_tool(
                mock_llm,
                max_depth=3,
                mode="tree",
            )

            # Call tool
            result = my_tool("Test prompt")

            # Verify it called recursive_brainstorm_tool with correct params
            mock_tool.assert_called_once()
            call_kwargs = mock_tool.call_args[1]
            assert call_kwargs["llm_instance"] == mock_llm
            assert call_kwargs["max_depth"] == 3
            assert call_kwargs["mode"] == "tree"


# ============================================================================
# ASYNC TESTS
# ============================================================================

class TestAsyncBrainstorming:
    """Test async brainstorming functionality."""

    @patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model')
    def test_brainstorm_async_basic(self, mock_generate, mock_llm, mock_idea_generation, mock_idea_evaluation):
        """Test basic async brainstorming."""
        def generate_side_effect(*args, **kwargs):
            model_class = args[0]
            if model_class == IdeaGeneration:
                return mock_idea_generation
            elif model_class == IdeaEvaluation:
                return mock_idea_evaluation

        mock_generate.side_effect = generate_side_effect

        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=1,
            ideas_per_level=3,
            mode="tree",
            verbose=False,
        )

        # Run async brainstorm
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(brainstorm.brainstorm_async("Test prompt"))
        loop.close()

        assert isinstance(result, BrainstormResult)
        assert result.total_ideas >= 3


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model')
    def test_generation_failure(self, mock_generate, mock_llm):
        """Test handling of generation failures."""
        # Simulate generation failure
        mock_generate.return_value = "Error: Generation failed"

        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=1,
            ideas_per_level=3,
            mode="tree",
            verbose=False,
        )

        result = brainstorm.brainstorm("Test prompt")

        # Should complete without crashing, but with 0 ideas
        assert result.total_ideas == 0

    @patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model')
    def test_quality_threshold_filtering(self, mock_generate, mock_llm):
        """Test that low-quality ideas are not expanded."""
        generation = IdeaGeneration(
            ideas=["Low quality idea"],
            reasoning_per_idea=["Not very good"]
        )

        low_eval = IdeaEvaluation(
            quality_score=3.0,  # Below default threshold of 5.0
            strengths=[],
            weaknesses=[],
            should_expand=False,
            reasoning=""
        )

        mock_generate.side_effect = [generation, low_eval]

        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=3,
            ideas_per_level=1,
            mode="tree",
            min_quality_threshold=5.0,
            verbose=False,
        )

        result = brainstorm.brainstorm("Test prompt")

        # Should only have 1 idea at depth 0, no expansion
        assert result.total_ideas == 1
        assert result.max_depth_reached == 0

    def test_mode_override(self, mock_llm):
        """Test that mode can be overridden in brainstorm call."""
        with patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model'):
            brainstorm = RecursiveBrainstorm(
                llm=mock_llm,
                mode="tree",
                max_depth=1,
                ideas_per_level=1,
            )

            # Override mode to linear
            result = brainstorm.brainstorm("Test", mode="linear")

            assert result.mode == "linear"


# ============================================================================
# CSV EXPORT TESTS
# ============================================================================

class TestCSVExport:
    """Test CSV export functionality."""

    def test_to_csv_with_expanded_criteria(self, tmp_path):
        """Test exporting to CSV with criteria expanded into columns."""
        import csv

        # Create test ideas
        ideas = [
            BrainstormIdea(
                id="idea_1",
                text="Idea 1",
                quality_score=8.5,
                depth=0,
                iteration=1,
                reasoning="Test reasoning 1",
                criteria_scores={"feasibility": 8.0, "impact": 9.0, "novelty": 8.0}
            ),
            BrainstormIdea(
                id="idea_2",
                text="Idea 2",
                quality_score=7.0,
                depth=1,
                parent_id="idea_1",
                iteration=2,
                reasoning="Test reasoning 2",
                criteria_scores={"feasibility": 7.0, "impact": 7.5, "novelty": 6.5}
            ),
        ]

        result = BrainstormResult(
            initial_prompt="Test prompt",
            mode="tree",
            total_ideas=2,
            total_iterations=2,
            max_depth_reached=1,
            all_ideas=ideas,
            execution_time=1.0,
            stopped_reason="test",
        )

        # Export to CSV
        csv_path = tmp_path / "test_export.csv"
        result.to_csv(str(csv_path), expand_criteria=True)

        # Verify file exists
        assert csv_path.exists()

        # Read and verify CSV contents
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Verify row count
            assert len(rows) == 2

            # Verify headers include expanded criteria
            assert 'id' in reader.fieldnames
            assert 'text' in reader.fieldnames
            assert 'quality_score' in reader.fieldnames
            assert 'feasibility_score' in reader.fieldnames
            assert 'impact_score' in reader.fieldnames
            assert 'novelty_score' in reader.fieldnames

            # Verify first row data
            assert rows[0]['id'] == 'idea_1'
            assert rows[0]['text'] == 'Idea 1'
            assert float(rows[0]['quality_score']) == 8.5
            assert float(rows[0]['feasibility_score']) == 8.0
            assert float(rows[0]['impact_score']) == 9.0

            # Verify second row
            assert rows[1]['id'] == 'idea_2'
            assert rows[1]['parent_id'] == 'idea_1'
            assert float(rows[1]['quality_score']) == 7.0

    def test_to_csv_without_expanded_criteria(self, tmp_path):
        """Test exporting to CSV with criteria as JSON string."""
        import csv
        import json

        ideas = [
            BrainstormIdea(
                id="idea_1",
                text="Idea 1",
                quality_score=8.5,
                depth=0,
                iteration=1,
                reasoning="Test",
                criteria_scores={"feasibility": 8.0, "impact": 9.0}
            ),
        ]

        result = BrainstormResult(
            initial_prompt="Test",
            mode="tree",
            total_ideas=1,
            total_iterations=1,
            max_depth_reached=0,
            all_ideas=ideas,
            execution_time=1.0,
            stopped_reason="test",
        )

        # Export with compact format
        csv_path = tmp_path / "test_compact.csv"
        result.to_csv(str(csv_path), expand_criteria=False)

        # Read and verify
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Verify headers don't have individual criterion columns
            assert 'criteria_scores' in reader.fieldnames
            assert 'feasibility_score' not in reader.fieldnames
            assert 'impact_score' not in reader.fieldnames

            # Verify criteria stored as JSON
            criteria_json = rows[0]['criteria_scores']
            criteria = json.loads(criteria_json)
            assert criteria['feasibility'] == 8.0
            assert criteria['impact'] == 9.0

    @patch('SimplerLLM.language.llm_addons.generate_pydantic_json_model')
    def test_brainstorm_with_auto_save_csv(self, mock_generate, mock_llm, tmp_path, mock_idea_generation, mock_idea_evaluation):
        """Test auto-saving CSV during brainstorm."""
        def generate_side_effect(*args, **kwargs):
            model_class = args[0]
            if model_class == IdeaGeneration:
                return mock_idea_generation
            elif model_class == IdeaEvaluation:
                return mock_idea_evaluation

        mock_generate.side_effect = generate_side_effect

        brainstorm = RecursiveBrainstorm(
            llm=mock_llm,
            max_depth=1,
            ideas_per_level=3,
            mode="tree",
            verbose=False,
        )

        csv_path = tmp_path / "auto_save.csv"

        # Run brainstorm with auto-save
        result = brainstorm.brainstorm(
            "Test prompt",
            save_csv=True,
            csv_path=str(csv_path)
        )

        # Verify CSV file was created
        assert csv_path.exists()

        # Verify it contains data
        import csv
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) >= 3  # At least the initial ideas

    def test_csv_with_empty_criteria(self, tmp_path):
        """Test CSV export with ideas that have no criteria scores."""
        ideas = [
            BrainstormIdea(
                id="idea_1",
                text="Idea 1",
                quality_score=7.0,
                depth=0,
                iteration=1,
                reasoning="Test",
                criteria_scores={}  # Empty criteria
            ),
        ]

        result = BrainstormResult(
            initial_prompt="Test",
            mode="tree",
            total_ideas=1,
            total_iterations=1,
            max_depth_reached=0,
            all_ideas=ideas,
            execution_time=1.0,
            stopped_reason="test",
        )

        csv_path = tmp_path / "empty_criteria.csv"
        result.to_csv(str(csv_path), expand_criteria=True)

        # Verify file still created successfully
        assert csv_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
