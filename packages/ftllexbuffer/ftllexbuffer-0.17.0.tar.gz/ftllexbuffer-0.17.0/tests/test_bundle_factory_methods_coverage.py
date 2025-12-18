"""Coverage tests for FluentBundle factory methods and untested paths.

Targets:
- Lines 232-238: FluentBundle.create() validation errors
- Lines 276-301: FluentBundle.for_system_locale()
- Other missing branches in bundle.py
"""

import os
from unittest.mock import patch

import pytest

from ftllexbuffer.runtime.bundle import FluentBundle


class TestFluentBundleCreateMethod:
    """Test FluentBundle.create() factory method."""

    def test_create_with_valid_locale(self) -> None:
        """Test create() with valid locale."""
        bundle = FluentBundle.create("en_US")

        assert bundle.locale == "en_US"

    def test_create_rejects_empty_locale(self) -> None:
        """Test create() rejects empty locale (lines 232-234)."""
        with pytest.raises(ValueError, match="Locale code cannot be empty"):
            FluentBundle.create("")

    def test_create_rejects_invalid_locale_format(self) -> None:
        """Test create() rejects invalid locale format (lines 236-238)."""
        with pytest.raises(ValueError, match="Invalid locale code format"):
            FluentBundle.create("en US")  # Space not allowed

    def test_create_rejects_locale_with_special_chars(self) -> None:
        """Test create() rejects locales with special characters (lines 236-238)."""
        invalid_locales = [
            "en@US",
            "en.US",
            "en/US",
            "en\\US",
        ]

        for invalid_locale in invalid_locales:
            with pytest.raises(ValueError, match="Invalid locale code format"):
                FluentBundle.create(invalid_locale)

    def test_create_accepts_valid_locale_formats(self) -> None:
        """Test create() accepts various valid locale formats."""
        valid_locales = [
            "en",
            "en_US",
            "en-US",
            "zh_CN",
            "pt-BR",
            "sr_Cyrl_RS",
        ]

        for locale in valid_locales:
            bundle = FluentBundle.create(locale)
            assert bundle.locale == locale

    def test_create_with_cache_enabled(self) -> None:
        """Test create() with caching enabled."""
        bundle = FluentBundle.create("lv", enable_cache=True, cache_size=500)

        assert bundle.cache_enabled
        assert bundle.cache_size == 500


class TestFluentBundleForSystemLocale:
    """Test FluentBundle.for_system_locale() factory method."""

    def test_for_system_locale_with_valid_system_locale(self) -> None:
        """Test for_system_locale() when system locale is available (lines 276-301)."""
        with patch("locale.getlocale", return_value=("en_US", "UTF-8")):
            bundle = FluentBundle.for_system_locale()

            assert bundle.locale == "en_US"

    def test_for_system_locale_falls_back_to_env_vars(self) -> None:
        """Test for_system_locale() uses env vars when getlocale fails (lines 281-287)."""
        with (
            patch("locale.getlocale", return_value=(None, None)),
            patch.dict(os.environ, {"LC_ALL": "fr_FR"}),
        ):
            bundle = FluentBundle.for_system_locale()

            assert bundle.locale == "fr_FR"

    def test_for_system_locale_tries_lc_messages(self) -> None:
        """Test for_system_locale() tries LC_MESSAGES env var (lines 285-287)."""
        with (
            patch("locale.getlocale", return_value=(None, None)),
            patch.dict(os.environ, {"LC_MESSAGES": "de_DE"}, clear=True),
        ):
            bundle = FluentBundle.for_system_locale()

            assert bundle.locale == "de_DE"

    def test_for_system_locale_tries_lang_var(self) -> None:
        """Test for_system_locale() tries LANG env var (lines 285-287)."""
        with (
            patch("locale.getlocale", return_value=(None, None)),
            patch.dict(os.environ, {"LANG": "es_ES"}, clear=True),
        ):
            bundle = FluentBundle.for_system_locale()

            assert bundle.locale == "es_ES"

    def test_for_system_locale_raises_when_no_locale_found(self) -> None:
        """Test for_system_locale() raises RuntimeError when no locale found (lines 289-294)."""
        with (
            patch("locale.getlocale", return_value=(None, None)),
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(
                RuntimeError,
                match="Could not determine system locale",
            ),
        ):
            FluentBundle.for_system_locale()

    def test_for_system_locale_strips_encoding(self) -> None:
        """Test for_system_locale() removes encoding suffix (lines 298-299)."""
        with patch("locale.getlocale", return_value=("en_GB.UTF-8", "UTF-8")):
            bundle = FluentBundle.for_system_locale()

            assert bundle.locale == "en_GB"
            assert ".UTF-8" not in bundle.locale

    def test_for_system_locale_with_cache_options(self) -> None:
        """Test for_system_locale() with caching options (lines 301-306)."""
        with patch("locale.getlocale", return_value=("ja_JP", "UTF-8")):
            bundle = FluentBundle.for_system_locale(
                enable_cache=True,
                cache_size=2000,
                use_isolating=False,
            )

            assert bundle.locale == "ja_JP"
            assert bundle.cache_enabled
            assert bundle.cache_size == 2000
            assert not bundle.use_isolating
