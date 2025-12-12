"""
Token Oriented Object Notation (TOON) Library

TOON is a data serialization format designed to minimize token usage for LLM applications.
It converts arrays of objects into a tabular CSV-like format, significantly reducing tokens
compared to standard JSON while maintaining structure and readability.

Format Example:
    JSON:
    {
      "users": [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"}
      ]
    }

    TOON:
    users[2]{id,name,role}:
    1,Alice,admin
    2,Bob,user

Performance:
- Arrays of objects (3+ items): 38-55% token savings vs JSON
- Flat tabular data: Matches CSV efficiency (±1%)
- Deep nested configs: Ties with JSON Compact (with smart_optimize=True)
- Processing speed: 1.62x faster average

Usage:
    Basic encoding (with smart optimization, recommended):
    >>> from toonstream import encode
    >>> toon_str = encode(data)

    Legacy mode (always use tabular, no optimization):
    >>> from toonstream import encode
    >>> toon_str = encode(data, smart_optimize=False)

    Decoding:
    >>> from toonstream import decode
    >>> data = decode(toon_str)

Modules:
- encoder: TOON encoder with optional smart array detection
- decoder: TOON to Python object decoder
- exceptions: Custom exception classes

For more information, see README.md and OPTIMIZATION_GUIDE.md
"""

from .decoder import ToonDecoder
from .decoder import decode as _normal_decode
from .encoder import ToonEncoder
from .encoder import encode as _normal_encode
from .exceptions import ToonDecodeError, ToonEncodeError, ToonError, ToonValidationError
from .pickle_utils import (
    ToonPickleError,
    load_pickle,
    load_toon_pickle,
    save_pickle,
    save_toon_pickle,
)

# Optional tensor support (requires PyTorch)
try:
    from .tensor_utils import (
        TensorDecoder,
        TensorEncoder,
        decode_with_tensors,
        encode_with_tensors,
        is_torch_available,
    )

    _TENSOR_SUPPORT = True
except ImportError:
    _TENSOR_SUPPORT = False
    encode_with_tensors = None
    decode_with_tensors = None
    TensorEncoder = None
    TensorDecoder = None
    is_torch_available = lambda: False

# TRON (Token Reduced Object Notation) support
from .tron_decoder import TronDecoder, decode_tron
from .tron_encoder import TronEncoder, encode_tron

# Unified API for mode selection and format choice
try:
    from .unified_api import decode, encode
except ImportError:
    encode = None
    decode = None

__version__ = "2.0.0"
__all__ = [
    # Convenience functions (recommended API)
    "encode",  # Now supports format='toon'/'tron' and auto_mode parameters
    "decode",  # Now supports format='toon'/'tron' and auto_mode parameters
    # TRON format (ultra compact) - NEW in v2.0.0
    "encode_tron",
    "decode_tron",
    "TronEncoder",
    "TronDecoder",
    # Pickle utilities
    "save_toon_pickle",
    "load_toon_pickle",
    "save_pickle",
    "load_pickle",
    # Tensor utilities (optional)
    "encode_with_tensors",
    "decode_with_tensors",
    "TensorEncoder",
    "TensorDecoder",
    "is_torch_available",
    # Classes for advanced usage
    "ToonEncoder",
    "ToonDecoder",
    # Exceptions
    "ToonError",
    "ToonEncodeError",
    "ToonDecodeError",
    "ToonValidationError",
    "ToonPickleError",
]
