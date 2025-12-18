"""Comprehensive coverage tests for runtime/locale_context.py.

Targets remaining uncovered lines:
- Line 54: LocaleValidationError.__str__()
- Lines 165-170: LocaleContext.create_or_raise() ValueError path
"""

from __future__ import annotations

import pytest

from ftllexbuffer.runtime.locale_context import LocaleContext, LocaleValidationError

# ============================================================================
# LINE 54: LocaleValidationError.__str__()
# ============================================================================


class TestLocaleValidationErrorString:
    """Test LocaleValidationError.__str__() (line 54)."""

    def test_locale_validation_error_str(self) -> None:
        """Verify LocaleValidationError.__str__() formats correctly (line 54)."""
        error = LocaleValidationError(
            locale_code="invalid-locale",
            error_message="Test error message",
        )

        # Call __str__ method (line 54)
        result = str(error)

        assert "Invalid locale 'invalid-locale'" in result
        assert "Test error message" in result

    def test_locale_validation_error_str_with_special_chars(self) -> None:
        """Test LocaleValidationError.__str__() with special characters."""
        error = LocaleValidationError(
            locale_code="zh-Hans-CN",
            error_message="Contains special: <>[]{}",
        )

        result = str(error)

        assert "zh-Hans-CN" in result
        assert "special: <>[]" in result

    def test_locale_validation_error_str_empty_message(self) -> None:
        """Test LocaleValidationError.__str__() with empty error message."""
        error = LocaleValidationError(
            locale_code="test",
            error_message="",
        )

        result = str(error)

        assert "Invalid locale 'test'" in result


# ============================================================================
# LINES 165-170: LocaleContext.create_or_raise() ValueError Path
# ============================================================================


class TestLocaleContextCreateOrRaiseErrorPath:
    """Test LocaleContext.create_or_raise() error handling (lines 165-170).

    Since v0.14.0, create_or_raise() does its own validation and raises
    ValueError directly for invalid locales.
    """

    def test_create_or_raise_with_unknown_locale_raises(self) -> None:
        """Test create_or_raise() raises ValueError for unknown locale."""
        with pytest.raises(ValueError, match=r"Unknown locale identifier"):
            LocaleContext.create_or_raise("xx-INVALID")

    def test_create_or_raise_with_malformed_locale_raises(self) -> None:
        """Test create_or_raise() raises ValueError for malformed locale."""
        with pytest.raises(ValueError, match=r"locale"):
            LocaleContext.create_or_raise("not-a-valid-locale-at-all")

    def test_create_or_raise_error_contains_locale_code(self) -> None:
        """Test create_or_raise() error message includes locale code."""
        test_locales = [
            "bad-locale",
            "xyz-123",
        ]

        for locale_code in test_locales:
            with pytest.raises(ValueError, match="locale") as exc_info:
                LocaleContext.create_or_raise(locale_code)

            assert locale_code in str(exc_info.value)

    def test_create_or_raise_success_path_returns_context(self) -> None:
        """Verify create_or_raise() returns LocaleContext on success."""
        # This tests the normal path where LocaleContext is returned
        ctx = LocaleContext.create_or_raise("en_US")

        assert isinstance(ctx, LocaleContext)
        assert ctx.locale_code == "en_US"


# ============================================================================
# LocaleContext.create() fallback behavior tests
# ============================================================================


class TestLocaleContextCreateFallback:
    """Test LocaleContext.create() graceful fallback behavior (v0.14.0+).

    Since v0.14.0, create() always returns LocaleContext with en_US fallback
    for invalid locales instead of returning LocaleValidationError.
    """

    def test_create_with_unknown_locale_returns_context(self) -> None:
        """create() returns LocaleContext for unknown locale."""
        result = LocaleContext.create("xx-UNKNOWN")

        assert isinstance(result, LocaleContext)
        # Original locale_code preserved
        assert result.locale_code == "xx-UNKNOWN"

    def test_create_with_invalid_locale_uses_en_us_formatting(self) -> None:
        """create() uses en_US formatting for invalid locales."""
        ctx = LocaleContext.create("invalid-locale-xyz")

        # Should format like en_US (comma grouping)
        formatted = ctx.format_number(1234.5, use_grouping=True)
        assert "1,234" in formatted or "1234" in formatted

    def test_create_never_returns_locale_validation_error(self) -> None:
        """create() never returns LocaleValidationError (v0.14.0+)."""
        test_cases = ["xx-YY", "invalid", "", "123", "not-a-locale"]

        for locale in test_cases:
            result = LocaleContext.create(locale)
            assert isinstance(result, LocaleContext)


# ============================================================================
# Integration Tests
# ============================================================================


class TestLocaleValidationErrorIntegration:
    """Integration tests for LocaleValidationError."""

    def test_locale_validation_error_is_dataclass(self) -> None:
        """LocaleValidationError is a proper dataclass."""
        error = LocaleValidationError(
            locale_code="test-locale",
            error_message="Test error",
        )

        # Dataclass fields accessible
        assert error.locale_code == "test-locale"
        assert error.error_message == "Test error"

        # __str__ works
        assert "test-locale" in str(error)

    def test_locale_validation_error_repr(self) -> None:
        """Test LocaleValidationError can be represented properly."""
        error = LocaleValidationError(
            locale_code="repr-test",
            error_message="Test repr",
        )

        # Verify repr works (uses default dataclass repr)
        repr_str = repr(error)
        assert "LocaleValidationError" in repr_str
        assert "repr-test" in repr_str
        assert "Test repr" in repr_str

    def test_locale_validation_error_equality(self) -> None:
        """Test LocaleValidationError equality comparison."""
        error1 = LocaleValidationError(
            locale_code="test",
            error_message="Same",
        )
        error2 = LocaleValidationError(
            locale_code="test",
            error_message="Same",
        )
        error3 = LocaleValidationError(
            locale_code="different",
            error_message="Same",
        )

        # Dataclass should provide __eq__
        assert error1 == error2
        assert error1 != error3


class TestLocaleContextBehaviorConsistency:
    """Test that create() and create_or_raise() have consistent validation logic."""

    def test_valid_locale_accepted_by_both(self) -> None:
        """Valid locale accepted by both create() and create_or_raise()."""
        locales = ["en-US", "de-DE", "lv-LV", "fr-FR"]

        for locale in locales:
            # create() should return context
            ctx1 = LocaleContext.create(locale)
            assert isinstance(ctx1, LocaleContext)

            # create_or_raise() should return context
            ctx2 = LocaleContext.create_or_raise(locale)
            assert isinstance(ctx2, LocaleContext)

    def test_invalid_locale_handled_differently(self) -> None:
        """Invalid locale: create() falls back, create_or_raise() raises."""
        locale = "xx-INVALID"

        # create() should return context with fallback
        ctx = LocaleContext.create(locale)
        assert isinstance(ctx, LocaleContext)
        assert ctx.locale_code == locale

        # create_or_raise() should raise
        with pytest.raises(ValueError, match="locale"):
            LocaleContext.create_or_raise(locale)
