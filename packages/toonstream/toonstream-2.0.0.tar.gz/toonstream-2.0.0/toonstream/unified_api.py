"""
Unified API for ToonStream with automatic mode detection and format selection.

Users can optionally enable auto mode, which automatically chooses between
normal TOON conversion and tensor-aware conversion based on the data.

Supported Formats:
    - 'toon': Token Oriented Object Notation (default) - LLM optimized
    - 'tron': Token Reduced Object Notation - Ultra compact, bandwidth optimized

Usage Examples:
    # Normal TOON conversion (default)
    >>> from toonstream import encode, decode
    >>> toon_str = encode(data)
    >>> decoded = decode(toon_str)

    # TRON format - ultra compact
    >>> tron_str = encode(data, format='tron')
    >>> decoded = decode(tron_str, format='tron')

    # Auto mode - automatically detects and uses tensor mode if needed
    >>> toon_str = encode(data, auto_mode=True)
    >>> decoded = decode(toon_str, auto_mode=True)
"""

from typing import Any, Literal

from .decoder import decode as toon_decode
from .encoder import encode as toon_encode
from .tron_decoder import decode_tron
from .tron_encoder import encode_tron

# Try to import tensor utilities
try:
    from .tensor_utils import decode_with_tensors, encode_with_tensors, is_torch_available

    _TENSOR_SUPPORT = True
except ImportError:
    _TENSOR_SUPPORT = False
    encode_with_tensors = None
    decode_with_tensors = None
    def is_torch_available():
        return False


def encode(
    obj: Any, format: Literal["toon", "tron"] = "toon", auto_mode: bool = False, **kwargs
) -> str:
    """
    Encode a Python object to TOON or TRON format.

    Args:
        obj: Python object to encode
        format: Output format - 'toon' (default, LLM optimized) or 'tron' (ultra compact)
        auto_mode: If True, auto-detect and use tensor mode if data contains tensors
        **kwargs: Additional arguments for encoding (compact, smart_optimize, indent, sort_keys)

    Returns:
        Encoded string in specified format

    Examples:
        >>> data = {'items': [{'id': 1}, {'id': 2}]}
        >>> toon_str = encode(data)  # TOON format (default)
        >>> tron_str = encode(data, format='tron')  # TRON format
        >>> toon_str = encode(data, auto_mode=True)  # Auto-detect tensors
    """
    # Handle TRON format
    if format == "tron":
        return encode_tron(
            obj, **{k: v for k, v in kwargs.items() if k in ("compact", "flatten_nested")}
        )

    # Handle TOON format (default)
    # If auto_mode is enabled and data contains tensors, use tensor encoding
    if auto_mode and _TENSOR_SUPPORT and _contains_tensors(obj):
        return encode_with_tensors(obj, **kwargs)

    # Default to normal TOON mode
    return toon_encode(obj, **kwargs)


def decode(
    encoded_str: str, format: Literal["toon", "tron"] = "toon", auto_mode: bool = False, **kwargs
) -> Any:
    """
    Decode a TOON or TRON string back to Python object.

    Args:
        encoded_str: Encoded string to decode
        format: Input format - 'toon' (default) or 'tron'
        auto_mode: If True, auto-detect tensor encoding (TOON only)
        **kwargs: Additional arguments for decoding (strict)

    Returns:
        Decoded Python object

    Examples:
        >>> data = decode(toon_str)  # Decode TOON (default)
        >>> data = decode(tron_str, format='tron')  # Decode TRON
        >>> data = decode(toon_str, auto_mode=True)  # Auto-detect tensors
    """
    # Handle TRON format
    if format == "tron":
        return decode_tron(encoded_str, **{k: v for k, v in kwargs.items() if k in ("strict",)})

    # Handle TOON format (default)
    # If auto_mode is enabled and string looks like tensor encoding, use tensor decoding
    if auto_mode and _TENSOR_SUPPORT and _looks_like_tensor_encoded(encoded_str):
        return decode_with_tensors(encoded_str, **kwargs)

    # Default to normal TOON mode
    return toon_decode(encoded_str, **kwargs)


def _contains_tensors(obj: Any) -> bool:
    """Check if object contains PyTorch tensors."""
    if not _TENSOR_SUPPORT:
        return False

    import torch

    if isinstance(obj, torch.Tensor):
        return True

    if isinstance(obj, dict):
        return any(_contains_tensors(v) for v in obj.values())

    if isinstance(obj, (list, tuple)):
        return any(_contains_tensors(item) for item in obj)

    return False


def _looks_like_tensor_encoded(data: str) -> bool:
    """Check if string looks like it contains tensor-encoded data."""
    if not isinstance(data, str):
        return False

    # Look for tensor encoding markers
    return "_type" in data and "torch.Tensor" in data


__all__ = ["encode", "decode"]
