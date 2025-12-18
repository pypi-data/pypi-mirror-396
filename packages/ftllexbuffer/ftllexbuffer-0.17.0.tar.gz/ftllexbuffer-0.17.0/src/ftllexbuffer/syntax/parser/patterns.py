"""Pattern parsing for Fluent FTL parser.

This module provides parsers for FTL patterns including variable references,
text elements, and placeables.

Architecture Note - Circular Imports:
    This module has a mutual dependency with expressions.py:
    - patterns.py imports parse_placeable from expressions.py
      (for parsing inline expressions within patterns)
    - expressions.py imports parse_simple_pattern from patterns.py
      (for parsing variant patterns in select expressions)

    This circular dependency is an INTENTIONAL architectural decision
    reflecting the inherent recursion in the FTL grammar:
    - Patterns contain Placeables, which contain Expressions
    - SelectExpression contains Variants, which contain Patterns

    The imports are placed inside function bodies to avoid import-time
    errors while still allowing the mutual recursion at runtime.
    This is documented in CHANGELOG.md v0.11.0 and suppressed via
    Pylint's cyclic-import global disable.
"""

from ftllexbuffer.syntax.ast import Identifier, Pattern, Placeable, TextElement, VariableReference
from ftllexbuffer.syntax.cursor import Cursor, ParseResult
from ftllexbuffer.syntax.parser.primitives import parse_identifier
from ftllexbuffer.syntax.parser.whitespace import is_indented_continuation


def parse_variable_reference(cursor: Cursor) -> ParseResult[VariableReference] | None:
    """Parse variable reference: $variable

    Variables start with $ followed by an identifier.

    Examples:
        $name → VariableReference(Identifier("name"))
        $count → VariableReference(Identifier("count"))

    Args:
        cursor: Current position in source

    Returns:
        Success(ParseResult(VariableReference, new_cursor)) on success
        Failure(ParseError(...)) if not a variable reference
    """
    # Expect $
    if cursor.is_eof or cursor.current != "$":
        return None  # "Expected variable reference (starts with $)", cursor, expected=["$"]

    cursor = cursor.advance()  # Skip $

    # Parse identifier
    result = parse_identifier(cursor)
    if result is None:
        return result

    parse_result = result
    var_ref = VariableReference(id=Identifier(parse_result.value))
    return ParseResult(var_ref, parse_result.cursor)


def parse_simple_pattern(cursor: Cursor) -> ParseResult[Pattern] | None:
    """Parse simple pattern (text with optional placeables).

    Handles:
    - Plain text
    - All placeable types: {$var}, {-term}, {NUMBER(...)}, {"string"}, {42}
    - Select expressions: {$x -> [a] A *[b] B}

    Stops at: newline, EOF, or dot (attribute marker)
    Also stops at variant delimiters: }, [, *

    Examples:
        "Hello"  → Pattern([TextElement("Hello")])
        "Hi {$name}"  → Pattern([TextElement("Hi "), Placeable(VariableReference("name"))])
        "{-term} text"  → Pattern([Placeable(TermReference("term")), TextElement(" text")])

    Args:
        cursor: Current position in source

    Returns:
        Success(ParseResult(Pattern, new_cursor)) on success
        Failure(ParseError(...)) on parse error
    """
    # Import here to avoid circular dependency
    from .expressions import parse_placeable  # noqa: PLC0415

    elements: list[TextElement | Placeable] = []

    while not cursor.is_eof:
        ch = cursor.current

        # Stop conditions
        # Also stop at } [ * for variant patterns inside select expressions
        if ch in ("\n", "\r", ".", "}", "[", "*"):
            break

        # Placeable: {expression}  # noqa: ERA001
        if ch == "{":
            cursor = cursor.advance()  # Skip {

            # Use full placeable parser which handles all expression types
            # (variables, terms, functions, strings, numbers, select expressions)
            placeable_result = parse_placeable(cursor)
            if placeable_result is None:
                return placeable_result

            placeable_parse = placeable_result
            cursor = placeable_parse.cursor
            elements.append(placeable_parse.value)

        else:
            # Parse text until { or stop condition
            text_start = cursor.pos
            while not cursor.is_eof:
                ch = cursor.current
                # Stop at: placeable start, line end, or special pattern markers
                # Note: '.' removed - only stops attributes at line start, not mid-pattern
                if ch in ("{", "\n", "\r", "}", "[", "*"):
                    break
                cursor = cursor.advance()

            if cursor.pos > text_start:
                text = Cursor(cursor.source, text_start).slice_to(cursor.pos)
                elements.append(TextElement(value=text))
            elif cursor.pos == text_start:
                # Prevent infinite loop: advance cursor when no text consumed
                # This happens when current char is a stop char but not '{'
                cursor = cursor.advance()

    pattern = Pattern(elements=tuple(elements))
    return ParseResult(pattern, cursor)


def parse_pattern(cursor: Cursor) -> ParseResult[Pattern] | None:  # noqa: PLR0912
    """Parse full pattern with multi-line continuation support.

    Use this for top-level message/attribute patterns. For variant patterns
    inside select expressions, use parse_simple_pattern() which has simpler
    stop conditions (no multi-line continuation).

    Handles:
    - Plain text with multi-line continuation (indented lines)
    - All placeable types: {$var}, {-term}, {NUMBER(...)}, {"string"}, {42}
    - Select expressions: {$var -> [key] value}

    Args:
        cursor: Current position in source

    Returns:
        ParseResult with Pattern on success, None on parse error
    """
    # Import here to avoid circular dependency
    from .expressions import parse_placeable  # noqa: PLC0415

    elements: list[TextElement | Placeable] = []

    while not cursor.is_eof:
        ch = cursor.current

        # Stop conditions - but check for indented continuations first
        if ch in ("\n", "\r"):
            if is_indented_continuation(cursor):
                # Skip newline and consume indentation
                cursor = cursor.advance()
                if not cursor.is_eof and cursor.current == "\n":
                    cursor = cursor.advance()  # Handle \r\n
                # Skip leading spaces (continuation indent)
                cursor = cursor.skip_spaces()
                # Add a space to represent the line break in the pattern value
                if elements and not isinstance(elements[-1], Placeable):
                    # Append space to previous text element
                    last_elem = elements[-1]
                    elements[-1] = TextElement(value=last_elem.value + " ")
                else:
                    # Add new text element with space
                    elements.append(TextElement(value=" "))
                continue  # Continue parsing on next line
            break  # Not a continuation, stop parsing pattern

        # Note: '.' is removed from stop conditions here.
        # Per Fluent spec, '.' only starts an attribute when it appears at the
        # beginning of a NEW LINE (after newline + optional indentation).
        # A '.' on the same line as '=' is valid text content.
        # Attributes are detected in message/term parsing after pattern completes.

        # Placeable: {$var} or {$var -> ...}
        if ch == "{":
            cursor = cursor.advance()  # Skip {

            # Use helper method to parse placeable (reduces nesting!)
            placeable_result = parse_placeable(cursor)
            if placeable_result is None:
                return placeable_result

            placeable_parse = placeable_result
            elements.append(placeable_parse.value)
            cursor = placeable_parse.cursor

        else:
            # Parse text until { or stop condition
            text_start = cursor.pos
            while not cursor.is_eof:
                ch = cursor.current
                # Stop at: placeable start, line end, or special pattern markers
                # Note: '.' removed - only stops attributes at line start, not mid-pattern
                if ch in ("{", "\n", "\r", "}", "[", "*"):
                    break
                cursor = cursor.advance()

            if cursor.pos > text_start:
                text = Cursor(cursor.source, text_start).slice_to(cursor.pos)
                elements.append(TextElement(value=text))
            elif cursor.pos == text_start:
                # Prevent infinite loop: advance cursor when no text consumed
                # This happens when current char is a stop char but not '{'
                cursor = cursor.advance()

    pattern = Pattern(elements=tuple(elements))
    return ParseResult(pattern, cursor)
