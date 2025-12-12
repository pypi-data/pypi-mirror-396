"""
JSON to TRON encoder implementation.

Token Reduced Object Notation (TRON) Format Specification:

TRON is designed for ultra-minimal syntax, removing as much punctuation as possible
while maintaining parseability. It's optimized for bandwidth and token efficiency.

Design Principles:
1. Minimal quotes - only when necessary (strings with special chars)
2. Minimal separators - use single chars (; | :)
3. No braces/brackets where inferrable
4. Compact type inference

Format Examples:
    JSON:
        {"name": "Alice", "age": 30, "active": true}
    TRON:
        name=Alice;age=30;active=1

    JSON Array of Objects:
        [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    TRON:
        @id,name|1,Alice|2,Bob

    Nested:
        {"user": {"name": "Alice", "role": "admin"}}
    TRON:
        user.name=Alice;user.role=admin

    Or with grouping:
        user{name=Alice;role=admin}

Syntax Rules:
- Key=Value pairs separated by ;
- Arrays of objects: @headers|row1|row2|...
- Simple arrays: [val1,val2,val3]
- Nested objects: parent.child=value or parent{child=value}
- Booleans: 1/0 instead of true/false
- Null: _ (underscore)
- Strings with special chars: "quoted"

Token Savings vs JSON: 50-70% typical
Token Savings vs TOON: 15-30% additional
"""

from typing import Any, Dict, List, Union

from .exceptions import ToonEncodeError


class TronEncoder:
    """Encoder for converting Python objects to ultra-compact TRON format."""

    # Characters that require quoting in values
    SPECIAL_CHARS = set(";=|,{}[]\"'\\@\n\r\t ")

    def __init__(self, compact: bool = True, flatten_nested: bool = True):
        """
        Initialize the TRON encoder.

        Args:
            compact: If True, use most compact representation (default: True)
            flatten_nested: If True, flatten nested objects with dot notation
        """
        self.compact = compact
        self.flatten_nested = flatten_nested

    def encode(self, obj: Any) -> str:
        """
        Encode a Python object to TRON format.

        Args:
            obj: Python object to encode (dict, list, or primitive)

        Returns:
            TRON formatted string

        Raises:
            ToonEncodeError: If encoding fails
        """
        try:
            return self._encode_value(obj)
        except Exception as e:
            raise ToonEncodeError(f"Failed to encode to TRON: {e}")

    def _encode_value(self, obj: Any, prefix: str = "") -> str:
        """Encode any value to TRON format."""
        if obj is None:
            return "_"
        elif isinstance(obj, bool):
            return "1" if obj else "0"
        elif isinstance(obj, (int, float)):
            return self._encode_number(obj)
        elif isinstance(obj, str):
            return self._encode_string(obj)
        elif isinstance(obj, dict):
            return self._encode_dict(obj, prefix)
        elif isinstance(obj, (list, tuple)):
            return self._encode_list(obj, prefix)
        else:
            raise ToonEncodeError(f"Unsupported type: {type(obj).__name__}")

    def _encode_number(self, num: Union[int, float]) -> str:
        """Encode a number, handling special float cases."""
        if isinstance(num, float):
            if num != num:  # NaN check
                raise ToonEncodeError("NaN values not supported in TRON")
            if num == float("inf") or num == float("-inf"):
                raise ToonEncodeError("Infinity values not supported in TRON")
            # Remove trailing zeros for cleaner output
            if num == int(num):
                return str(int(num))
            return str(num)
        return str(num)

    def _encode_string(self, s: str) -> str:
        """Encode a string, quoting only when necessary."""
        if not s:
            return '""'  # Empty string

        # Check if quoting is needed
        needs_quote = any(c in self.SPECIAL_CHARS for c in s)

        # Also quote if it looks like a number or boolean
        if not needs_quote:
            if s in ("1", "0", "_", "true", "false", "null"):
                needs_quote = True
            else:
                try:
                    float(s)
                    needs_quote = True
                except ValueError:
                    pass

        if needs_quote:
            # Escape quotes and backslashes
            escaped = s.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'

        return s

    def _encode_dict(self, obj: Dict, prefix: str = "") -> str:
        """Encode a dictionary to TRON format."""
        if not obj:
            return "{}"

        pairs = []
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict) and self.flatten_nested:
                # Flatten nested dicts with dot notation
                nested = self._encode_dict(value, full_key)
                pairs.append(nested)
            elif isinstance(value, dict):
                # Use brace notation for nested
                inner = self._encode_dict(value)
                pairs.append(f"{key}{{{inner}}}")
            else:
                encoded_value = self._encode_value(value)
                pairs.append(f"{full_key}={encoded_value}")

        return ";".join(pairs)

    def _encode_list(self, obj: List, prefix: str = "") -> str:
        """Encode a list to TRON format."""
        if not obj:
            return "[]"

        # Check if all items are dicts with same keys (tabular data)
        if all(isinstance(item, dict) for item in obj) and len(obj) >= 1:
            return self._encode_tabular(obj)

        # Check if all items are primitives
        if all(isinstance(item, (int, float, str, bool, type(None))) for item in obj):
            return self._encode_simple_array(obj)

        # Mixed or nested array - use bracket notation
        encoded_items = [self._encode_value(item) for item in obj]
        return f"[{','.join(encoded_items)}]"

    def _encode_simple_array(self, obj: List) -> str:
        """Encode a simple array of primitives."""
        encoded = [self._encode_value(item) for item in obj]
        return f"[{','.join(encoded)}]"

    def _encode_tabular(self, obj: List[Dict]) -> str:
        """
        Encode an array of objects in ultra-compact tabular format.

        Format: @header1,header2|val1,val2|val3,val4
        """
        if not obj:
            return "[]"

        # Collect all unique keys maintaining order
        all_keys = []
        seen_keys = set()
        for item in obj:
            for key in item.keys():
                if key not in seen_keys:
                    all_keys.append(key)
                    seen_keys.add(key)

        if not all_keys:
            return "[]"

        # Build header
        header = ",".join(all_keys)

        # Build rows
        rows = []
        for item in obj:
            row_values = []
            for key in all_keys:
                value = item.get(key)
                encoded = self._encode_value(value) if value is not None else "_"
                row_values.append(encoded)
            rows.append(",".join(row_values))

        # Combine: @headers|row1|row2|...
        return f"@{header}|{'|'.join(rows)}"


def encode_tron(obj: Any, compact: bool = True, flatten_nested: bool = True) -> str:
    """
    Convenience function to encode a Python object to TRON format.

    Args:
        obj: Python object to encode
        compact: Use most compact representation (default: True)
        flatten_nested: Flatten nested objects with dot notation (default: True)

    Returns:
        TRON formatted string

    Examples:
        >>> encode_tron({"name": "Alice", "age": 30})
        'name=Alice;age=30'

        >>> encode_tron([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
        '@id,name|1,Alice|2,Bob'

        >>> encode_tron({"active": True, "count": None})
        'active=1;count=_'
    """
    encoder = TronEncoder(compact=compact, flatten_nested=flatten_nested)
    return encoder.encode(obj)
