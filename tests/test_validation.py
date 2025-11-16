"""Tests for input validation utilities."""

from wirepusher_official.validation import normalize_tags


class TestNormalizeTags:
    """Test tag normalization functionality."""

    def test_none_input(self):
        """Test that None input returns None."""
        assert normalize_tags(None) is None

    def test_empty_list(self):
        """Test that empty list returns None."""
        assert normalize_tags([]) is None

    def test_single_tag(self):
        """Test normalization of single tag."""
        assert normalize_tags(["Production"]) == ["production"]

    def test_lowercase_conversion(self):
        """Test tags are converted to lowercase."""
        assert normalize_tags(["PROD", "STAGING", "Test"]) == ["prod", "staging", "test"]

    def test_whitespace_trimming(self):
        """Test whitespace is trimmed from tags."""
        assert normalize_tags(["  production  ", "release  ", "  deploy"]) == [
            "production",
            "release",
            "deploy",
        ]

    def test_duplicate_removal(self):
        """Test duplicate tags are removed (case-insensitive)."""
        assert normalize_tags(["production", "Production", "PRODUCTION"]) == ["production"]
        assert normalize_tags(["deploy", "release", "deploy"]) == ["deploy", "release"]

    def test_empty_string_removal(self):
        """Test empty strings are filtered out."""
        assert normalize_tags(["", "production", "  ", "release"]) == [
            "production",
            "release",
        ]

    def test_invalid_characters_filtered(self):
        """Test tags with invalid characters are filtered out."""
        # Valid: alphanumeric, hyphens, underscores
        assert normalize_tags(["prod-1", "staging_2", "test123"]) == [
            "prod-1",
            "staging_2",
            "test123",
        ]

        # Invalid: special characters
        assert normalize_tags(["prod@", "test!", "deploy#"]) is None
        assert normalize_tags(["prod.env", "test(1)", "deploy[2]"]) is None

    def test_mixed_valid_invalid(self):
        """Test filtering when mixing valid and invalid tags."""
        assert normalize_tags(["production", "test@invalid", "release", "bad!"]) == [
            "production",
            "release",
        ]

    def test_non_string_values_filtered(self):
        """Test non-string values are filtered out."""
        assert normalize_tags([123, "production", None, "release"]) == [  # type: ignore
            "production",
            "release",
        ]

    def test_all_filtered_returns_none(self):
        """Test that if all tags are filtered out, None is returned."""
        assert normalize_tags(["", "  ", "invalid!", "@#$"]) is None
        assert normalize_tags([123, None, 456]) is None  # type: ignore

    def test_order_preserved(self):
        """Test that order of tags is preserved."""
        assert normalize_tags(["zebra", "alpha", "beta"]) == ["zebra", "alpha", "beta"]

    def test_duplicates_keep_first(self):
        """Test that duplicates keep the first occurrence."""
        assert normalize_tags(["production", "release", "production"]) == [
            "production",
            "release",
        ]

    def test_complex_scenario(self):
        """Test complex real-world scenario."""
        tags = [
            "  PRODUCTION  ",
            "Release",
            "production",  # duplicate
            "deploy-v2",
            "test@invalid",
            "",
            "  ",
            "RELEASE",  # duplicate
            "v1_0_0",
            "bad!tag",
        ]
        expected = ["production", "release", "deploy-v2", "v1_0_0"]
        assert normalize_tags(tags) == expected

    def test_hyphen_underscore_allowed(self):
        """Test that hyphens and underscores are allowed."""
        assert normalize_tags(["feature-branch", "version_1_0", "test-123_abc"]) == [
            "feature-branch",
            "version_1_0",
            "test-123_abc",
        ]

    def test_numbers_allowed(self):
        """Test that numbers are allowed."""
        assert normalize_tags(["v123", "2024", "release-2"]) == ["v123", "2024", "release-2"]

    def test_unicode_filtered(self):
        """Test that unicode characters are filtered out."""
        assert normalize_tags(["production", "test-émoji", "release"]) == [
            "production",
            "release",
        ]
