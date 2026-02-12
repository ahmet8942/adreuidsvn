"""
Tests for the CAPTCHA image generator.
"""

import io
import pytest
from PIL import Image

from bot.captcha.generator import generate_captcha


class TestCaptchaGenerator:
    """Tests for generate_captcha()."""

    def test_returns_tuple(self):
        """Should return (BytesIO, str) tuple."""
        result = generate_captcha()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_code_is_digits(self):
        """Code should contain only digits."""
        _, code = generate_captcha()
        assert code.isdigit()

    def test_default_code_length(self):
        """Default code length should be 5."""
        _, code = generate_captcha()
        assert len(code) == 5

    def test_custom_code_length(self):
        """Should respect custom length parameter."""
        _, code = generate_captcha(length=4)
        assert len(code) == 4

        _, code = generate_captcha(length=8)
        assert len(code) == 8

    def test_image_is_valid_png(self):
        """The returned BytesIO should contain a valid PNG image."""
        img_bytes, _ = generate_captcha()
        assert isinstance(img_bytes, io.BytesIO)

        img = Image.open(img_bytes)
        assert img.format == "PNG"

    def test_image_dimensions(self):
        """Image should match the requested dimensions."""
        img_bytes, _ = generate_captcha(width=300, height=120)
        img = Image.open(img_bytes)
        assert img.size == (300, 120)

    def test_default_dimensions(self):
        """Default dimensions should be 280x100."""
        img_bytes, _ = generate_captcha()
        img = Image.open(img_bytes)
        assert img.size == (280, 100)

    def test_codes_are_random(self):
        """Multiple calls should produce different codes (with high probability)."""
        codes = set()
        for _ in range(20):
            _, code = generate_captcha()
            codes.add(code)
        # At least some should be different
        assert len(codes) > 1

    def test_image_is_rgb(self):
        """Image should be in RGB mode."""
        img_bytes, _ = generate_captcha()
        img = Image.open(img_bytes)
        assert img.mode == "RGB"

    def test_bytesio_is_seeked_to_start(self):
        """BytesIO should be seeked to position 0 for reading."""
        img_bytes, _ = generate_captcha()
        assert img_bytes.tell() == 0

    def test_image_has_content(self):
        """Image should have actual content (not blank)."""
        img_bytes, _ = generate_captcha()
        data = img_bytes.read()
        assert len(data) > 1000  # A real PNG with content should be > 1KB
