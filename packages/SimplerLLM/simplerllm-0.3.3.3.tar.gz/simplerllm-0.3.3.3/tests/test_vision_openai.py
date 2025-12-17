"""
Tests for OpenAI vision capabilities in SimplerLLM.

These tests verify that the vision functionality works correctly with
the OpenAI provider for vision-capable models like GPT-4o and GPT-4 Vision.

Note: These tests require a valid OPENAI_API_KEY environment variable.
They make actual API calls and will consume API credits.
"""

import pytest
import os
from SimplerLLM.language.llm import LLM, LLMProvider
from SimplerLLM.tools.image_helpers import (
    encode_image_to_base64,
    is_url,
    validate_image_source,
    prepare_image_content,
    prepare_vision_content,
    get_image_mime_type
)


class TestImageHelpers:
    """Test the image helper utility functions."""

    def test_is_url_with_valid_url(self):
        """Test URL detection with a valid URL."""
        assert is_url("https://example.com/image.jpg") is True
        assert is_url("http://example.com/image.png") is True

    def test_is_url_with_file_path(self):
        """Test URL detection with a file path."""
        assert is_url("/path/to/image.jpg") is False
        assert is_url("C:\\path\\to\\image.png") is False
        assert is_url("./relative/path/image.jpg") is False

    def test_is_url_with_invalid_input(self):
        """Test URL detection with invalid input."""
        assert is_url("not a url or path") is False
        assert is_url("") is False

    def test_get_image_mime_type(self):
        """Test MIME type detection for different image formats."""
        assert get_image_mime_type("/path/to/image.jpg") == "image/jpeg"
        assert get_image_mime_type("/path/to/image.jpeg") == "image/jpeg"
        assert get_image_mime_type("/path/to/image.png") == "image/png"
        assert get_image_mime_type("/path/to/image.gif") == "image/gif"
        assert get_image_mime_type("/path/to/image.webp") == "image/webp"
        assert get_image_mime_type("/path/to/image.unknown") == "image/jpeg"  # Default

    def test_prepare_image_content_with_url(self):
        """Test preparing image content from a URL."""
        url = "https://example.com/image.jpg"
        result = prepare_image_content(url, detail="high")

        assert result["type"] == "image_url"
        assert result["image_url"]["url"] == url
        assert result["image_url"]["detail"] == "high"

    def test_prepare_image_content_with_invalid_detail(self):
        """Test that invalid detail parameter raises ValueError."""
        with pytest.raises(ValueError, match="Invalid detail level"):
            prepare_image_content("https://example.com/image.jpg", detail="invalid")

    def test_prepare_vision_content(self):
        """Test preparing multi-part vision content."""
        text = "What's in this image?"
        images = ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
        result = prepare_vision_content(text, images, detail="auto")

        assert len(result) == 3  # 1 text + 2 images
        assert result[0]["type"] == "text"
        assert result[0]["text"] == text
        assert result[1]["type"] == "image_url"
        assert result[2]["type"] == "image_url"


class TestOpenAIVisionIntegration:
    """Integration tests for OpenAI vision functionality.

    These tests require a valid OPENAI_API_KEY and will make actual API calls.
    They are marked as integration tests and can be skipped during unit testing.
    """

    @pytest.fixture
    def llm_instance(self):
        """Create an OpenAI LLM instance for testing."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        return LLM.create(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o",  # Vision-capable model
            api_key=api_key
        )

    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_vision_with_public_url(self, llm_instance):
        """Test vision functionality with a public image URL."""
        # Using a simple test image URL
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
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_vision_with_detail_parameter(self, llm_instance):
        """Test vision functionality with different detail levels."""
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

        # Test with low detail
        response_low = llm_instance.generate_response(
            prompt="What do you see?",
            images=[image_url],
            detail="low",
            max_tokens=50
        )

        # Test with high detail
        response_high = llm_instance.generate_response(
            prompt="What do you see?",
            images=[image_url],
            detail="high",
            max_tokens=50
        )

        assert response_low is not None
        assert response_high is not None
        assert isinstance(response_low, str)
        assert isinstance(response_high, str)

    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_vision_with_multiple_images(self, llm_instance):
        """Test vision functionality with multiple images."""
        # Using two public domain images
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
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
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
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
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
        assert response.input_token_count > 0  # Vision requests consume more tokens

    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
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


class TestErrorHandling:
    """Test error handling for vision functionality."""

    def test_file_not_found_error(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        with pytest.raises(FileNotFoundError):
            encode_image_to_base64("/path/to/nonexistent/image.jpg")

    def test_invalid_detail_parameter(self):
        """Test that invalid detail parameter raises ValueError."""
        with pytest.raises(ValueError):
            prepare_image_content("https://example.com/image.jpg", detail="invalid_detail")

    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_non_vision_model_error(self):
        """Test error handling when using images with a non-vision model.

        Note: This test expects the API to return an error or reject the request.
        We're letting the API handle the error as per the design decision.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        llm = LLM.create(
            provider=LLMProvider.OPENAI,
            model_name="gpt-3.5-turbo",  # Non-vision model
            api_key=api_key
        )

        # This should fail at the API level
        with pytest.raises(Exception):
            llm.generate_response(
                prompt="What's in this image?",
                images=["https://example.com/image.jpg"],
                max_tokens=50
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
