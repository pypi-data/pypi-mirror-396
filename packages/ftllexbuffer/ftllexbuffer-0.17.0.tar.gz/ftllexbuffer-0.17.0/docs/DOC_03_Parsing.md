---
spec_version: AFAD-v1
project_version: 0.17.0
context: PARSING
last_updated: 2025-12-15T00:00:00Z
maintainer: claude-opus-4-5
---

# Parsing Reference

---

## `parse_ftl`

### Signature
```python
def parse_ftl(source: str) -> Resource:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `source` | `str` | Y | FTL source code. |

### Constraints
- Return: Resource AST containing parsed entries.
- Raises: `FluentSyntaxError` on critical parse error.
- State: None.
- Thread: Safe.

---

## `serialize_ftl`

### Signature
```python
def serialize_ftl(resource: Resource) -> str:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `resource` | `Resource` | Y | Resource AST node. |

### Constraints
- Return: FTL source string.
- Raises: None.
- State: None.
- Thread: Safe.

---

## `FluentParserV1`

### Signature
```python
class FluentParserV1:
    def __init__(self, *, max_source_size: int | None = None) -> None: ...
    def parse(self, source: str) -> Resource: ...
    @property
    def max_source_size(self) -> int: ...
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `max_source_size` | `int \| None` | N | Maximum source size in bytes (default: 10 MB). |

### Constraints
- Return: Parser instance.
- State: Stores max_source_size configuration.
- Thread: Safe for concurrent parse() calls.
- Security: Validates source size before parsing (DoS prevention).

---

## `FluentParserV1.parse`

### Signature
```python
def parse(self, source: str) -> Resource:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `source` | `str` | Y | FTL source code. |

### Constraints
- Return: Resource AST containing parsed entries.
- Raises: `ValueError` if source exceeds max_source_size.
- State: None.
- Thread: Safe.
- Security: Enforces input size limit.

---

## `set_max_nesting_depth`

### Signature
```python
def set_max_nesting_depth(max_depth: int) -> None:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `max_depth` | `int` | Y | Maximum nesting depth (default: 100). |

### Constraints
- Return: None.
- Raises: `ValueError` if max_depth < 1.
- State: Sets thread-local nesting limit.
- Thread: Thread-local (each thread has independent limit).
- Security: Prevents DoS via deeply nested placeables.
- Import: `from ftllexbuffer.syntax.parser.expressions import set_max_nesting_depth`

---

## `get_last_parse_error`

### Signature
```python
def get_last_parse_error() -> ParseErrorContext | None:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|

### Constraints
- Return: ParseErrorContext with error details, or None.
- Raises: None.
- State: Reads thread-local error storage.
- Thread: Thread-safe (thread-local storage).
- Import: `from ftllexbuffer.syntax.parser.primitives import get_last_parse_error`

---

## `clear_parse_error`

### Signature
```python
def clear_parse_error() -> None:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|

### Constraints
- Return: None.
- Raises: None.
- State: Clears thread-local error storage.
- Thread: Thread-safe.
- Import: `from ftllexbuffer.syntax.parser.primitives import clear_parse_error`

---

## `ParseErrorContext`

### Signature
```python
@dataclass(frozen=True, slots=True)
class ParseErrorContext:
    message: str
    position: int
    expected: tuple[str, ...] = ()
```

### Contract
| Field | Type | Description |
|:------|:-----|:------------|
| `message` | `str` | Human-readable error description. |
| `position` | `int` | Character position in source. |
| `expected` | `tuple[str, ...]` | Expected tokens (optional). |

### Constraints
- Immutable: Frozen dataclass.
- Thread: Safe (immutable).
- Import: `from ftllexbuffer.syntax.parser.primitives import ParseErrorContext`

---

## `parse_number`

### Signature
```python
def parse_number(
    value: str,
    locale_code: str,
) -> tuple[float | None, tuple[FluentParseError, ...]]:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `str` | Y | Locale-formatted number string. |
| `locale_code` | `str` | Y | BCP 47 locale identifier. |

### Constraints
- Return: Tuple of (float or None, errors).
- Raises: Never.
- State: None.
- Thread: Safe.

---

## `parse_decimal`

### Signature
```python
def parse_decimal(
    value: str,
    locale_code: str,
) -> tuple[Decimal | None, tuple[FluentParseError, ...]]:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `str` | Y | Locale-formatted number string. |
| `locale_code` | `str` | Y | BCP 47 locale identifier. |

### Constraints
- Return: Tuple of (Decimal or None, errors).
- Raises: Never.
- State: None.
- Thread: Safe.

---

## `parse_date`

### Signature
```python
def parse_date(
    value: str,
    locale_code: str,
) -> tuple[date | None, tuple[FluentParseError, ...]]:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `str` | Y | Locale-formatted date string. |
| `locale_code` | `str` | Y | BCP 47 locale identifier. |

### Constraints
- Return: Tuple of (date or None, errors).
- Raises: Never.
- State: None.
- Thread: Safe.

---

## `parse_datetime`

### Signature
```python
def parse_datetime(
    value: str,
    locale_code: str,
    *,
    tzinfo: timezone | None = None,
) -> tuple[datetime | None, tuple[FluentParseError, ...]]:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `str` | Y | Locale-formatted datetime string. |
| `locale_code` | `str` | Y | BCP 47 locale identifier. |
| `tzinfo` | `timezone \| None` | N | Timezone to assign. |

### Constraints
- Return: Tuple of (datetime or None, errors).
- Raises: Never.
- State: None.
- Thread: Safe.

---

## `parse_currency`

### Signature
```python
def parse_currency(
    value: str,
    locale_code: str,
    *,
    default_currency: str | None = None,
    infer_from_locale: bool = False,
) -> tuple[tuple[Decimal, str] | None, tuple[FluentParseError, ...]]:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `str` | Y | Currency string with amount and symbol. |
| `locale_code` | `str` | Y | BCP 47 locale identifier. |
| `default_currency` | `str \| None` | N | Fallback currency for ambiguous symbols ($, kr). |
| `infer_from_locale` | `bool` | N | Infer currency from locale if symbol ambiguous. |

### Constraints
- Return: Tuple of ((amount, currency_code) or None, errors).
- Raises: Never.
- State: None.
- Thread: Safe.

---

## `is_valid_number`

### Signature
```python
def is_valid_number(value: float) -> TypeIs[float]:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `float` | Y | Float to validate. |

### Constraints
- Return: True if finite float.
- Raises: None.
- State: None.

---

## `is_valid_decimal`

### Signature
```python
def is_valid_decimal(value: Decimal) -> TypeIs[Decimal]:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `Decimal` | Y | Decimal to validate. |

### Constraints
- Return: True if finite Decimal.
- Raises: None.
- State: None.

---

## `is_valid_date`

### Signature
```python
def is_valid_date(value: date | None) -> TypeIs[date]:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `date \| None` | Y | Date to validate. |

### Constraints
- Return: True if not None.
- Raises: None.
- State: None.

---

## `is_valid_datetime`

### Signature
```python
def is_valid_datetime(value: datetime | None) -> TypeIs[datetime]:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `datetime \| None` | Y | Datetime to validate. |

### Constraints
- Return: True if not None.
- Raises: None.
- State: None.

---

## `is_valid_currency`

### Signature
```python
def is_valid_currency(
    value: tuple[Decimal, str] | None,
) -> TypeIs[tuple[Decimal, str]]:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `tuple[Decimal, str] \| None` | Y | Currency tuple to validate. |

### Constraints
- Return: True if not None and amount is finite.
- Raises: None.
- State: None.

---
