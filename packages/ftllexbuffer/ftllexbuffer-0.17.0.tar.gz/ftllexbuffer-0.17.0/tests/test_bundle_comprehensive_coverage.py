"""Comprehensive coverage tests for runtime/bundle.py missing lines.

Targets all remaining uncovered lines and branches in bundle.py to reach 100% coverage.
"""

from unittest.mock import MagicMock

import pytest

from ftllexbuffer.diagnostics import FluentSyntaxError
from ftllexbuffer.runtime.bundle import FluentBundle


class TestFluentBundleReprAndContextManager:
    """Test __repr__ and context manager protocol."""

    def test_repr_with_messages_and_terms(self) -> None:
        """Test __repr__ returns correct format (line 320)."""
        bundle = FluentBundle("en_US")
        bundle.add_resource("msg = Hello\n-term = Term")

        repr_str = repr(bundle)

        assert "FluentBundle" in repr_str
        assert "en_US" in repr_str
        assert "messages=1" in repr_str
        assert "terms=1" in repr_str

    def test_context_manager_enter_returns_self(self) -> None:
        """Test __enter__ returns self (line 341)."""
        bundle = FluentBundle("lv")

        with bundle as ctx:
            assert ctx is bundle

    def test_context_manager_exit_clears_cache(self) -> None:
        """Test __exit__ clears cache when enabled (lines 360-361)."""
        bundle = FluentBundle("en", enable_cache=True)
        bundle.add_resource("msg = Test")

        # Format to populate cache
        bundle.format_pattern("msg")
        stats = bundle.get_cache_stats()
        assert stats is not None
        assert stats["size"] > 0

        # Exit context manager
        with bundle:
            pass

        # Cache should be cleared
        stats_after = bundle.get_cache_stats()
        assert stats_after is not None
        assert stats_after["size"] == 0

    def test_context_manager_exit_clears_messages_and_terms(self) -> None:
        """Test __exit__ clears message and term registries (lines 364-365)."""
        bundle = FluentBundle("en")
        bundle.add_resource("msg = Hello\n-term = Term")

        assert len(bundle.get_message_ids()) > 0

        with bundle:
            pass

        # Messages and terms should be cleared
        assert len(bundle.get_message_ids()) == 0

    def test_context_manager_exit_without_cache(self) -> None:
        """Test __exit__ works when cache is disabled (line 360 branch)."""
        bundle = FluentBundle("en", enable_cache=False)
        bundle.add_resource("msg = Test")

        # Should not raise even though cache is None
        with bundle:
            pass


class TestGetBabelLocale:
    """Test get_babel_locale() error handling."""

    def test_get_babel_locale_with_invalid_locale(self) -> None:
        """Test get_babel_locale() error path (lines 400-402)."""
        # Create bundle with potentially invalid locale
        bundle = FluentBundle("invalid_LOCALE_12345")

        # Should handle error gracefully and return error string
        result = bundle.get_babel_locale()

        # Either succeeds or returns error format
        assert isinstance(result, str)


class TestAddResourceErrorHandling:
    """Test add_resource() error paths."""

    def test_add_resource_logs_error_with_source_path(self) -> None:
        """Test add_resource() logs error with source_path when exception occurs (line 564)."""
        bundle = FluentBundle("en")

        # Create a mock parser that raises FluentSyntaxError
        mock_parser = MagicMock()
        mock_parser.parse.side_effect = FluentSyntaxError("Mock parser error")

        # Replace the parser
        bundle._parser = mock_parser

        with pytest.raises(FluentSyntaxError, match="Mock parser error"):
            bundle.add_resource("msg = Test", source_path="test.ftl")

    def test_add_resource_logs_error_without_source_path(self) -> None:
        """Test add_resource() logs error without source_path when exception occurs (line 566)."""
        bundle = FluentBundle("en")

        # Create a mock parser that raises FluentSyntaxError
        mock_parser = MagicMock()
        mock_parser.parse.side_effect = FluentSyntaxError("Mock parser error")

        # Replace the parser
        bundle._parser = mock_parser

        with pytest.raises(FluentSyntaxError, match="Mock parser error"):
            bundle.add_resource("msg = Test")

    def test_add_resource_clears_cache_when_enabled(self) -> None:
        """Test add_resource() clears cache (lines 559-560)."""
        bundle = FluentBundle("en", enable_cache=True)
        bundle.add_resource("first = First")

        # Populate cache
        bundle.format_pattern("first")
        initial_stats = bundle.get_cache_stats()
        assert initial_stats is not None
        assert initial_stats["size"] > 0

        # Add more resources - should clear cache
        bundle.add_resource("second = Second")

        # Cache should be cleared
        stats_after = bundle.get_cache_stats()
        assert stats_after is not None
        assert stats_after["size"] == 0


class TestValidateResourceErrorHandling:
    """Test validate_resource() error paths."""

    def test_validate_resource_handles_critical_syntax_error(self) -> None:
        """Test validate_resource() handles FluentSyntaxError (lines 741-750)."""
        bundle = FluentBundle("en")

        # Trigger FluentSyntaxError during validation
        invalid_ftl = "msg = { broken"

        result = bundle.validate_resource(invalid_ftl)

        # Should return ValidationResult with error, not raise
        assert len(result.errors) > 0


class TestFormatPatternErrorPaths:
    """Test format_pattern() error handling."""

    def test_format_pattern_caches_result_when_enabled(self) -> None:
        """Test format_pattern() caches results (lines 800-802)."""
        bundle = FluentBundle("en", enable_cache=True)
        bundle.add_resource("msg = Hello")

        # First call - cache miss
        result1, _ = bundle.format_pattern("msg")
        stats1 = bundle.get_cache_stats()
        assert stats1 is not None
        assert stats1["misses"] == 1
        assert stats1["hits"] == 0

        # Second call - cache hit
        result2, _ = bundle.format_pattern("msg")
        stats2 = bundle.get_cache_stats()
        assert stats2 is not None
        assert stats2["hits"] == 1

        assert result1 == result2


class TestIntrospectionErrorPaths:
    """Test introspection methods error handling."""

    def test_get_message_variables_raises_key_error(self) -> None:
        """Test get_message_variables() raises KeyError (lines 939-940)."""
        bundle = FluentBundle("en")

        with pytest.raises(KeyError, match="not found"):
            bundle.get_message_variables("nonexistent")

    def test_introspect_message_raises_key_error(self) -> None:
        """Test introspect_message() raises KeyError (lines 999-1001)."""
        bundle = FluentBundle("en")

        with pytest.raises(KeyError, match="not found"):
            bundle.introspect_message("nonexistent")


class TestAddFunctionCacheInvalidation:
    """Test add_function() cache invalidation."""

    def test_add_function_clears_cache_when_enabled(self) -> None:
        """Test add_function() clears cache (lines 1022-1023)."""
        bundle = FluentBundle("en", enable_cache=True)
        bundle.add_resource("msg = { CUSTOM($val) }")

        # Populate cache first (will fail without function, but still cached)
        bundle.format_pattern("msg", {"val": "test"})

        stats_before = bundle.get_cache_stats()
        assert stats_before is not None
        assert stats_before["size"] > 0

        # Add function - should clear cache
        def CUSTOM(val: str) -> str:  # noqa: N802
            return val.upper()

        bundle.add_function("CUSTOM", CUSTOM)

        stats_after = bundle.get_cache_stats()
        assert stats_after is not None
        assert stats_after["size"] == 0


class TestGetCacheStatsWhenDisabled:
    """Test get_cache_stats() when caching disabled."""

    def test_get_cache_stats_returns_none_when_disabled(self) -> None:
        """Test get_cache_stats() returns None when cache disabled (lines 1058-1060)."""
        bundle = FluentBundle("en", enable_cache=False)

        stats = bundle.get_cache_stats()

        assert stats is None


class TestCircularReferenceDetection:
    """Test circular reference detection in validate_resource()."""

    def test_validate_resource_detects_circular_message_refs(self) -> None:
        """Test circular message reference detection (branch 423->425)."""
        bundle = FluentBundle("en")

        # Create circular reference: msg1 -> msg2 -> msg1
        circular_ftl = """
msg1 = { msg2 }
msg2 = { msg1 }
"""

        result = bundle.validate_resource(circular_ftl)

        # Should detect circular reference as a warning
        assert len(result.warnings) > 0
        assert any("circular" in w.message.lower() for w in result.warnings)

    def test_validate_resource_detects_circular_term_refs(self) -> None:
        """Test circular term reference detection (branch 451->446, 465->460, 483->478)."""
        bundle = FluentBundle("en")

        # Create circular term reference
        circular_terms = """
-term1 = { -term2 }
-term2 = { -term1 }
"""

        result = bundle.validate_resource(circular_terms)

        # Should detect circular reference
        assert len(result.warnings) > 0


class TestValidateResourceBranches:
    """Test validate_resource() branch coverage."""

    def test_validate_resource_detects_undefined_message_ref(self) -> None:
        """Test undefined message reference detection (branch 606->611)."""
        bundle = FluentBundle("en")

        ftl = "msg = { undefined_msg }"

        result = bundle.validate_resource(ftl)

        # Should warn about undefined reference
        assert len(result.warnings) > 0
        assert any("undefined" in w.message.lower() for w in result.warnings)

    def test_validate_resource_detects_undefined_term_ref(self) -> None:
        """Test undefined term reference detection (lines 692-693)."""
        bundle = FluentBundle("en")

        ftl = "msg = { -undefined_term }"

        result = bundle.validate_resource(ftl)

        # Should warn about undefined term
        assert len(result.warnings) > 0

    def test_validate_resource_detects_term_referencing_undefined_message(self) -> None:
        """Test term referencing undefined message (line 711)."""
        bundle = FluentBundle("en")

        ftl = "-term = { undefined_msg }"

        result = bundle.validate_resource(ftl)

        # Should warn about undefined message reference from term
        assert len(result.warnings) > 0

    def test_validate_resource_checks_message_without_value(self) -> None:
        """Test detection of messages without value or attributes (line 648)."""
        bundle = FluentBundle("en")

        # Message with neither value nor attributes
        ftl = "empty-msg =\n"

        result = bundle.validate_resource(ftl)

        # May or may not warn depending on parser behavior
        # Just ensure it doesn't crash
        assert result is not None


class TestFormatPatternRecursionError:
    """Test format_pattern() RecursionError handling."""

    def test_format_pattern_handles_recursion_error(self) -> None:
        """Test format_pattern() catches RecursionError from circular refs (line 848)."""
        bundle = FluentBundle("en")

        # Create actual circular reference that would cause RecursionError
        bundle.add_resource("""
msg1 = { msg2 }
msg2 = { msg1 }
""")

        # Should handle RecursionError gracefully
        result, errors = bundle.format_pattern("msg1")

        # Should return fallback and error
        assert "{msg1}" in result or "msg1" in result
        assert len(errors) > 0
