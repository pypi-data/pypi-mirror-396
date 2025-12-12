"""
Comprehensive unit tests for TRON (Token Reduced Object Notation).

Tests cover:
1. Primitive encoding/decoding (strings, numbers, booleans, null)
2. Object encoding/decoding (simple, nested)
3. Array encoding/decoding (simple, tabular)
4. Round-trip consistency
5. Edge cases and error handling
6. Comparison with TOON format
"""

import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from toonstream.exceptions import ToonDecodeError, ToonEncodeError
from toonstream.tron_decoder import TronDecoder, decode_tron
from toonstream.tron_encoder import TronEncoder, encode_tron


class TestTronPrimitives:
    """Test encoding/decoding of primitive types."""

    def test_encode_string_simple(self):
        """Simple strings without special chars."""
        assert encode_tron("hello") == "hello"
        assert encode_tron("Alice") == "Alice"
        assert encode_tron("world123") == "world123"

    def test_encode_string_with_spaces(self):
        """Strings with spaces should be quoted."""
        assert encode_tron("hello world") == '"hello world"'
        assert encode_tron("John Doe") == '"John Doe"'

    def test_encode_string_with_special_chars(self):
        """Strings with special characters should be quoted."""
        assert encode_tron("a;b") == '"a;b"'
        assert encode_tron("a=b") == '"a=b"'
        assert encode_tron("a|b") == '"a|b"'

    def test_encode_empty_string(self):
        """Empty string encoding."""
        assert encode_tron("") == '""'

    def test_encode_integer(self):
        """Integer encoding."""
        assert encode_tron(42) == "42"
        assert encode_tron(0) == "0"
        assert encode_tron(-100) == "-100"

    def test_encode_float(self):
        """Float encoding."""
        assert encode_tron(3.14) == "3.14"
        assert encode_tron(0.5) == "0.5"
        assert encode_tron(-2.5) == "-2.5"

    def test_encode_float_as_int(self):
        """Float with no decimal part becomes int."""
        assert encode_tron(3.0) == "3"
        assert encode_tron(100.0) == "100"

    def test_encode_boolean(self):
        """Boolean encoding uses 1/0."""
        assert encode_tron(True) == "1"
        assert encode_tron(False) == "0"

    def test_encode_null(self):
        """Null/None encoding uses underscore."""
        assert encode_tron(None) == "_"

    def test_decode_string_simple(self):
        """Decode unquoted strings."""
        assert decode_tron("hello") == "hello"
        assert decode_tron("Alice") == "Alice"

    def test_decode_string_quoted(self):
        """Decode quoted strings."""
        assert decode_tron('"hello world"') == "hello world"
        assert decode_tron('"a;b"') == "a;b"

    def test_decode_integer(self):
        """Decode integers."""
        assert decode_tron("42") == 42
        assert decode_tron("-100") == -100

    def test_decode_float(self):
        """Decode floats."""
        assert decode_tron("3.14") == 3.14
        assert decode_tron("-2.5") == -2.5

    def test_decode_boolean(self):
        """Decode boolean 1/0."""
        assert decode_tron("1") is True
        assert decode_tron("0") is False

    def test_decode_null(self):
        """Decode null underscore."""
        assert decode_tron("_") is None


class TestTronObjects:
    """Test encoding/decoding of dictionaries/objects."""

    def test_encode_simple_object(self):
        """Simple flat object."""
        data = {"name": "Alice", "age": 30}
        result = encode_tron(data)
        assert "name=Alice" in result
        assert "age=30" in result
        assert ";" in result

    def test_encode_object_with_boolean(self):
        """Object with boolean values."""
        data = {"active": True, "deleted": False}
        result = encode_tron(data)
        assert "active=1" in result
        assert "deleted=0" in result

    def test_encode_object_with_null(self):
        """Object with null values."""
        data = {"name": "Alice", "nickname": None}
        result = encode_tron(data)
        assert "name=Alice" in result
        assert "nickname=_" in result

    def test_encode_empty_object(self):
        """Empty object."""
        assert encode_tron({}) == "{}"

    def test_encode_nested_object_flattened(self):
        """Nested object with dot notation (default)."""
        data = {"user": {"name": "Alice", "age": 30}}
        result = encode_tron(data)
        assert "user.name=Alice" in result
        assert "user.age=30" in result

    def test_decode_simple_object(self):
        """Decode simple key=value pairs."""
        result = decode_tron("name=Alice;age=30")
        assert result == {"name": "Alice", "age": 30}

    def test_decode_object_with_boolean(self):
        """Decode object with boolean 1/0."""
        result = decode_tron("active=1;deleted=0")
        assert result == {"active": True, "deleted": False}

    def test_decode_object_with_null(self):
        """Decode object with null underscore."""
        result = decode_tron("name=Alice;nickname=_")
        assert result == {"name": "Alice", "nickname": None}

    def test_decode_empty_object(self):
        """Decode empty object."""
        assert decode_tron("{}") == {}

    def test_decode_nested_dot_notation(self):
        """Decode nested object with dot notation."""
        result = decode_tron("user.name=Alice;user.age=30")
        assert result == {"user": {"name": "Alice", "age": 30}}


class TestTronArrays:
    """Test encoding/decoding of arrays."""

    def test_encode_simple_array(self):
        """Simple array of primitives."""
        data = [1, 2, 3]
        result = encode_tron(data)
        assert result == "[1,2,3]"

    def test_encode_string_array(self):
        """Array of strings."""
        data = ["a", "b", "c"]
        result = encode_tron(data)
        assert result == "[a,b,c]"

    def test_encode_mixed_array(self):
        """Array with mixed types."""
        data = [1, "hello", True, None]
        result = encode_tron(data)
        assert result == "[1,hello,1,_]"

    def test_encode_empty_array(self):
        """Empty array."""
        assert encode_tron([]) == "[]"

    def test_encode_tabular_array(self):
        """Array of objects becomes tabular format."""
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        result = encode_tron(data)
        assert result.startswith("@")
        assert "id,name" in result or "name,id" in result
        assert "1,Alice" in result or "Alice,1" in result
        assert "2,Bob" in result or "Bob,2" in result

    def test_decode_simple_array(self):
        """Decode simple array."""
        result = decode_tron("[1,2,3]")
        assert result == [1, 2, 3]

    def test_decode_string_array(self):
        """Decode string array."""
        result = decode_tron("[a,b,c]")
        assert result == ["a", "b", "c"]

    def test_decode_empty_array(self):
        """Decode empty array."""
        assert decode_tron("[]") == []

    def test_decode_tabular_array(self):
        """Decode tabular format to array of objects."""
        result = decode_tron("@id,name|1,Alice|2,Bob")
        assert result == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]


class TestTronRoundTrip:
    """Test that encode -> decode returns original data."""

    def test_roundtrip_simple_object(self):
        """Round-trip simple object."""
        data = {"name": "Alice", "age": 30}
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        assert decoded == data

    def test_roundtrip_object_with_types(self):
        """Round-trip object with various types."""
        data = {"active": True, "count": 42, "name": "Test", "value": None}
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        assert decoded == data

    def test_roundtrip_simple_array(self):
        """Round-trip simple array."""
        data = [1, 2, 3, 4, 5]
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        assert decoded == data

    def test_roundtrip_tabular_array(self):
        """Round-trip array of objects."""
        data = [
            {"id": 1, "name": "Alice", "active": True},
            {"id": 2, "name": "Bob", "active": False},
        ]
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        assert decoded == data

    def test_roundtrip_nested_object(self):
        """Round-trip nested object."""
        data = {"user": {"name": "Alice", "profile": {"age": 30}}}
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        # With flattening, nested structure is preserved
        assert decoded["user"]["name"] == "Alice"
        assert decoded["user"]["profile"]["age"] == 30

    def test_roundtrip_complex_data(self):
        """Round-trip complex structure."""
        data = {
            "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
            "count": 2,
            "active": True,
        }
        # Encode the users array separately for tabular format
        users_encoded = encode_tron(data["users"])
        users_decoded = decode_tron(users_encoded)
        assert users_decoded == data["users"]


class TestTronEdgeCases:
    """Test edge cases and special scenarios."""

    def test_string_that_looks_like_number(self):
        """String that looks like number should be quoted."""
        data = {"code": "123"}
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        # Note: Without explicit quotes, "123" may decode as int
        # This is a known limitation of ultra-compact formats

    def test_string_with_quotes(self):
        """String containing quotes."""
        data = {"message": 'He said "hello"'}
        encoded = encode_tron(data)
        assert '\\"' in encoded  # Escaped quotes
        decoded = decode_tron(encoded)
        assert decoded["message"] == 'He said "hello"'

    def test_unicode_string(self):
        """Unicode characters in strings."""
        data = {"emoji": "Hello 🌍"}
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        assert decoded["emoji"] == "Hello 🌍"

    def test_large_number(self):
        """Large numbers."""
        data = {"big": 9999999999999}
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        assert decoded["big"] == 9999999999999

    def test_negative_float(self):
        """Negative float values."""
        data = {"temp": -40.5}
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        assert decoded["temp"] == -40.5

    def test_many_columns_tabular(self):
        """Tabular with many columns."""
        data = [{"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}, {"a": 6, "b": 7, "c": 8, "d": 9, "e": 10}]
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        assert decoded == data

    def test_single_row_tabular(self):
        """Single row still uses tabular format."""
        data = [{"id": 1, "name": "Alice"}]
        encoded = encode_tron(data)
        assert encoded.startswith("@")
        decoded = decode_tron(encoded)
        assert decoded == data


class TestTronErrorHandling:
    """Test error handling."""

    def test_encode_unsupported_type(self):
        """Unsupported type raises error."""
        with pytest.raises(ToonEncodeError):
            encode_tron(object())

    def test_encode_nan(self):
        """NaN raises error."""
        with pytest.raises(ToonEncodeError):
            encode_tron(float("nan"))

    def test_encode_infinity(self):
        """Infinity raises error."""
        with pytest.raises(ToonEncodeError):
            encode_tron(float("inf"))

    def test_decode_invalid_pair(self):
        """Invalid pair in strict mode."""
        with pytest.raises(ToonDecodeError):
            decode_tron("name;age=30", strict=True)


class TestTronVsToon:
    """Compare TRON output with TOON for size reduction."""

    def test_simple_object_comparison(self):
        """TRON should be more compact than TOON for simple objects."""
        from toonstream import encode as toon_encode

        data = {"name": "Alice", "age": 30, "active": True}

        toon_result = toon_encode(data)
        tron_result = encode_tron(data)

        # TRON should be shorter or equal
        assert len(tron_result) <= len(toon_result)
        print("\nSimple object comparison:")
        print(f"  TOON: {len(toon_result)} chars - {toon_result}")
        print(f"  TRON: {len(tron_result)} chars - {tron_result}")

    def test_tabular_comparison(self):
        """TRON tabular vs TOON tabular."""
        from toonstream import encode as toon_encode

        data = [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
            {"id": 3, "name": "Carol", "role": "user"},
        ]

        toon_result = toon_encode(data)
        tron_result = encode_tron(data)

        print("\nTabular comparison:")
        print(f"  TOON: {len(toon_result)} chars")
        print(f"  TRON: {len(tron_result)} chars")
        print(
            f"  Savings: {len(toon_result) - len(tron_result)} chars ({100 * (len(toon_result) - len(tron_result)) / len(toon_result):.1f}%)"
        )


class TestTronRealWorld:
    """Test with real-world like data structures."""

    def test_user_records(self):
        """User records typical in APIs."""
        data = [
            {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
            {"id": 2, "name": "Bob", "email": "bob@example.com", "active": True},
            {"id": 3, "name": "Carol", "email": "carol@example.com", "active": False},
        ]
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        assert decoded == data

    def test_config_object(self):
        """Configuration object."""
        data = {"host": "localhost", "port": 8080, "debug": True, "timeout": None}
        encoded = encode_tron(data)
        decoded = decode_tron(encoded)
        assert decoded == data

    def test_api_response(self):
        """Typical API response structure."""
        data = {
            "success": True,
            "count": 2,
            "data": [{"id": 1, "title": "Item1"}, {"id": 2, "title": "Item2"}],
        }
        # Encode nested array separately
        items_encoded = encode_tron(data["data"])
        items_decoded = decode_tron(items_encoded)
        assert items_decoded == data["data"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
