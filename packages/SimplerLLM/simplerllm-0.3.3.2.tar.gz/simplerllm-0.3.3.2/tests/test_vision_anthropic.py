"""
Tests for Anthropic vision capabilities in SimplerLLM.

These tests verify that the vision functionality works correctly with
the Anthropic provider for vision-capable Claude models.

Note: These tests require a valid ANTHROPIC_API_KEY environment variable.
They make actual API calls and will consume API credits.
"""

import pytest
import os
from SimplerLLM.language.llm import LLM, LLMProvider
from SimplerLLM.tools.image_helpers import (
    prepare_image_content_anthropic,
    prepare_vision_content_anthropic,
    validate_image_size
)


class TestAnthropicImageHelpers:
    """Test the Anthropic-specific image helper utility functions."""

    def test_prepare_image_content_anthropic_with_url(self):
        """Test preparing image content from a URL."""
        url = "https://example.com/image.jpg"
        result = prepare_image_content_anthropic(url)

        assert result["type"] == "image"
        assert result["source"]["type"] == "url"
        assert result["source"]["url"] == url

    def test_prepare_vision_content_anthropic_ordering(self):
        """Test that images come BEFORE text in Anthropic format."""
        text = "What's in these images?"
        images = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ]
        result = prepare_vision_content_anthropic(text, images)

        # Should have 3 parts: 2 images + 1 text
        assert len(result) == 3

        # First two should be images
        assert result[0]["type"] == "image"
        assert result[1]["type"] == "image"

        # Last should be text (Anthropic best practice: images before text)
        assert result[2]["type"] == "text"
        assert result[2]["text"] == text

    def test_validate_image_size(self):
        """Test image size validation."""
        # This will just test that the function doesn't crash
        # Actual file validation requires real files
        is_valid, warning = validate_image_size("/nonexistent/file.jpg")
        # Should return tuple
        assert isinstance(is_valid, bool)


class TestAnthropicVisionIntegration:
    """Integration tests for Anthropic vision functionality.

    These tests require a valid ANTHROPIC_API_KEY and will make actual API calls.
    They are marked as integration tests and can be skipped during unit testing.
    """

    @pytest.fixture
    def llm_instance(self):
        """Create an Anthropic LLM instance for testing."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set")

        return LLM.create(
            provider=LLMProvider.ANTHROPIC,
            model_name="claude-sonnet-4-5",  # Latest vision-capable model
            api_key=api_key
        )

    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
    def test_vision_with_public_url(self, llm_instance):
        """Test vision functionality with a public image URL."""
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

        response = llm_instance.generate_response(
            prompt="Describe this image in one sentence.",
            images=[image_url],
            max_tokens=100
        )

        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)

    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
    def test_vision_with_multiple_images(self, llm_instance):
        """Test vision functionality with multiple images."""
        images = [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/1024px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1024px-Cat03.jpg"
        ]

        response = llm_instance.generate_response(
            prompt="Briefly describe what you see in these images.",
            images=images,
            max_tokens=150
        )

        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)

    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
    def test_backward_compatibility_text_only(self, llm_instance):
        """Test that text-only requests still work (backward compatibility)."""
        response = llm_instance.generate_response(
            prompt="Say hello in one word.",
            max_tokens=10
        )

        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)

    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
    def test_full_response_with_vision(self, llm_instance):
        """Test that full_response mode works with vision."""
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1024px-Cat03.jpg"

        response = llm_instance.generate_response(
            prompt="What animal is in this image?",
            images=[image_url],
            max_tokens=50,
            full_response=True
        )

        assert response is not None
        assert hasattr(response, 'generated_text')
        assert hasattr(response, 'model')
        assert hasattr(response, 'input_token_count')
        assert hasattr(response, 'output_token_count')
        assert response.input_token_count > 0  # Vision requests consume tokens

    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
    async def test_async_vision_request(self, llm_instance):
        """Test asynchronous vision requests."""
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1024px-Cat03.jpg"

        response = await llm_instance.generate_response_async(
            prompt="Describe this image in one word.",
            images=[image_url],
            max_tokens=10
        )

        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)

    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
    def test_no_detail_parameter(self, llm_instance):
        """Test that Anthropic doesn't have a detail parameter (unlike OpenAI)."""
        import inspect
        sig = inspect.signature(llm_instance.generate_response)
        params = list(sig.parameters.keys())

        # Should have 'images' parameter
        assert 'images' in params

        # Should NOT have 'detail' parameter (that's OpenAI-specific)
        assert 'detail' not in params


class TestErrorHandling:
    """Test error handling for Anthropic vision functionality."""

    def test_file_not_found_error(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        from SimplerLLM.tools.image_helpers import encode_image_to_base64

        with pytest.raises(FileNotFoundError):
            encode_image_to_base64("/path/to/nonexistent/image.jpg")


class TestImageOrdering:
    """Test that Anthropic follows its best practice of images before text."""

    def test_images_before_text_ordering(self):
        """Verify that images are placed before text in content array."""
        text = "Describe this"
        images = ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]

        content = prepare_vision_content_anthropic(text, images)

        # Check ordering: all images should come before text
        image_indices = [i for i, item in enumerate(content) if item["type"] == "image"]
        text_indices = [i for i, item in enumerate(content) if item["type"] == "text"]

        # All image indices should be less than all text indices
        assert all(img_idx < text_idx for img_idx in image_indices for text_idx in text_indices)

    def test_single_image_before_text(self):
        """Test with a single image."""
        text = "What is this?"
        images = ["https://example.com/image.jpg"]

        content = prepare_vision_content_anthropic(text, images)

        assert content[0]["type"] == "image"  # Image first
        assert content[1]["type"] == "text"   # Text last


class TestAnthropicSpecificFormat:
    """Test Anthropic-specific content format requirements."""

    def test_anthropic_uses_image_type_not_image_url(self):
        """Anthropic uses 'image' type, not 'image_url' like OpenAI."""
        url = "https://example.com/image.jpg"
        content = prepare_image_content_anthropic(url)

        assert content["type"] == "image"  # Not "image_url"
        assert "source" in content  # Has "source" field
        assert content["source"]["type"] == "url"

    def test_anthropic_base64_format(self):
        """Test that Anthropic uses different base64 format than OpenAI."""
        # This test just verifies the structure, not actual encoding
        # since we'd need a real file for that

        # The key difference: Anthropic uses separate fields for media_type and data
        # OpenAI uses a data URI: "data:image/jpeg;base64,..."

        # We can test the URL format to verify structure
        url_content = prepare_image_content_anthropic("https://example.com/test.jpg")

        assert url_content["source"]["type"] == "url"
        assert "url" in url_content["source"]
        # Should NOT have OpenAI-style nested "image_url" object
        assert "image_url" not in url_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
