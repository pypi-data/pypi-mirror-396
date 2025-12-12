"""
TRON to Python decoder implementation.

Token Reduced Object Notation (TRON) Decoder

Parses ultra-compact TRON format back to Python objects.

Syntax Rules Parsed:
- Key=Value pairs separated by ;
- Arrays of objects: @headers|row1|row2|...
- Simple arrays: [val1,val2,val3]
- Nested objects: parent.child=value or parent{child=value}
- Booleans: 1/0 (in context) or true/false
- Null: _ (underscore)
- Quoted strings: "value with spaces"
- Unquoted strings: simpleValue
"""

from typing import Any, Dict, List

from .exceptions import ToonDecodeError


class TronDecoder:
    """Decoder for converting TRON format back to Python objects."""

    def __init__(self, strict: bool = True):
        """
        Initialize the TRON decoder.

        Args:
            strict: If True, raise errors on invalid syntax (default: True)
        """
        self.strict = strict

    def decode(self, tron_str: str) -> Any:
        """
        Decode a TRON string to Python object.

        Args:
            tron_str: TRON formatted string

        Returns:
            Python object (dict, list, or primitive)

        Raises:
            ToonDecodeError: If decoding fails
        """
        try:
            tron_str = tron_str.strip()

            if not tron_str:
                return None

            # Detect format type
            if tron_str.startswith("@"):
                return self._decode_tabular(tron_str)
            elif tron_str.startswith("["):
                return self._decode_array(tron_str)
            elif tron_str.startswith("{"):
                return self._decode_brace_object(tron_str)
            elif tron_str.startswith('"') and tron_str.endswith('"'):
                # Quoted string - decode as primitive
                return self._decode_primitive(tron_str)
            elif "=" in tron_str or (";" in tron_str and not tron_str.startswith('"')):
                return self._decode_object(tron_str)
            else:
                return self._decode_primitive(tron_str)

        except ToonDecodeError:
            raise
        except Exception as e:
            raise ToonDecodeError(f"Failed to decode TRON: {e}")

    def _decode_primitive(self, s: str) -> Any:
        """Decode a primitive value."""
        s = s.strip()

        if not s:
            return None

        # Null
        if s == "_":
            return None

        # Boolean (0/1 shorthand)
        if s == "0":
            return False
        if s == "1":
            return True

        # Quoted string
        if s.startswith('"') and s.endswith('"'):
            return self._decode_quoted_string(s)

        # Try number
        try:
            if "." in s:
                return float(s)
            return int(s)
        except ValueError:
            pass

        # Unquoted string
        return s

    def _decode_quoted_string(self, s: str) -> str:
        """Decode a quoted string, handling escapes."""
        # Remove outer quotes
        inner = s[1:-1]

        # Unescape
        result = []
        i = 0
        while i < len(inner):
            if inner[i] == "\\" and i + 1 < len(inner):
                next_char = inner[i + 1]
                if next_char == '"':
                    result.append('"')
                elif next_char == "\\":
                    result.append("\\")
                elif next_char == "n":
                    result.append("\n")
                elif next_char == "t":
                    result.append("\t")
                elif next_char == "r":
                    result.append("\r")
                else:
                    result.append(next_char)
                i += 2
            else:
                result.append(inner[i])
                i += 1

        return "".join(result)

    def _decode_object(self, s: str) -> Dict:
        """Decode key=value pairs into a dictionary."""
        result = {}

        # Split by semicolon, respecting quotes
        pairs = self._split_pairs(s, ";")

        for pair in pairs:
            if not pair.strip():
                continue

            if "=" not in pair:
                if self.strict:
                    raise ToonDecodeError(f"Invalid pair (no '='): {pair}")
                continue

            key, value = pair.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Handle dot notation (nested keys)
            if "." in key:
                self._set_nested(result, key, self._decode_value(value))
            else:
                result[key] = self._decode_value(value)

        return result

    def _decode_value(self, s: str) -> Any:
        """Decode a value (could be primitive, array, or nested object)."""
        s = s.strip()

        if s.startswith("["):
            return self._decode_array(s)
        elif s.startswith("{"):
            return self._decode_brace_object(s)
        elif s.startswith("@"):
            return self._decode_tabular(s)
        else:
            return self._decode_primitive(s)

    def _decode_array(self, s: str) -> List:
        """Decode a bracketed array [val1,val2,...]."""
        s = s.strip()

        if s == "[]":
            return []

        if not s.startswith("[") or not s.endswith("]"):
            raise ToonDecodeError(f"Invalid array format: {s}")

        inner = s[1:-1]

        if not inner.strip():
            return []

        # Split by comma, respecting quotes and brackets
        items = self._split_values(inner, ",")

        return [self._decode_value(item) for item in items if item.strip()]

    def _decode_brace_object(self, s: str) -> Dict:
        """Decode a brace-enclosed object {key=value;...}."""
        s = s.strip()

        if s == "{}":
            return {}

        if not s.startswith("{") or not s.endswith("}"):
            raise ToonDecodeError(f"Invalid object format: {s}")

        inner = s[1:-1]
        return self._decode_object(inner)

    def _decode_tabular(self, s: str) -> List[Dict]:
        """
        Decode tabular format @headers|row1|row2|...

        Returns list of dictionaries.
        """
        s = s.strip()

        if not s.startswith("@"):
            raise ToonDecodeError(f"Invalid tabular format (missing @): {s}")

        # Remove @ prefix
        content = s[1:]

        # Split by | respecting quotes
        parts = self._split_values(content, "|")

        if not parts:
            return []

        # First part is headers
        headers = self._split_values(parts[0], ",")
        headers = [h.strip() for h in headers]

        # Remaining parts are data rows
        result = []
        for row_str in parts[1:]:
            values = self._split_values(row_str, ",")

            obj = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    value = self._decode_value(values[i])
                    obj[header] = value
                else:
                    obj[header] = None

            result.append(obj)

        return result

    def _split_pairs(self, s: str, delimiter: str) -> List[str]:
        """Split string by delimiter, respecting quotes and braces."""
        return self._split_values(s, delimiter)

    def _split_values(self, s: str, delimiter: str) -> List[str]:
        """Split string by delimiter, respecting quotes and nested structures."""
        result = []
        current = []
        depth = 0
        in_quotes = False
        escape_next = False

        for char in s:
            if escape_next:
                current.append(char)
                escape_next = False
                continue

            if char == "\\":
                current.append(char)
                escape_next = True
                continue

            if char == '"':
                in_quotes = not in_quotes
                current.append(char)
                continue

            if in_quotes:
                current.append(char)
                continue

            if char in "[{":
                depth += 1
                current.append(char)
            elif char in "]}":
                depth -= 1
                current.append(char)
            elif char == delimiter and depth == 0:
                result.append("".join(current))
                current = []
            else:
                current.append(char)

        if current:
            result.append("".join(current))

        return result

    def _set_nested(self, obj: Dict, dotted_key: str, value: Any) -> None:
        """Set a value using dot-notation key (e.g., 'user.name')."""
        keys = dotted_key.split(".")
        current = obj

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value


def decode_tron(tron_str: str, strict: bool = True) -> Any:
    """
    Convenience function to decode a TRON string to Python object.

    Args:
        tron_str: TRON formatted string
        strict: Raise errors on invalid syntax (default: True)

    Returns:
        Python object (dict, list, or primitive)

    Examples:
        >>> decode_tron('name=Alice;age=30')
        {'name': 'Alice', 'age': 30}

        >>> decode_tron('@id,name|1,Alice|2,Bob')
        [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]

        >>> decode_tron('active=1;count=_')
        {'active': True, 'count': None}
    """
    decoder = TronDecoder(strict=strict)
    return decoder.decode(tron_str)
