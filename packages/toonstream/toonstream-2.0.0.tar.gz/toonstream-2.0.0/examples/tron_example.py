"""
Example demonstrating TRON (Token Reduced Object Notation) format.

TRON is an ultra-compact serialization format that minimizes tokens
for LLM context optimization. It uses minimal punctuation and special
syntax for maximum compression.

Key TRON Features:
- Key=Value pairs separated by semicolons
- Booleans: 1/0 instead of true/false
- Null: ~ instead of null
- Arrays: [item1;item2;item3]
- Nested objects: dot notation (user.name=Alice)
- Tabular data: @col1,col2|row1,row2|row3,row4
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from toonstream import decode, encode

print("=" * 70)
print("TOONSTREAM - TRON Format Examples")
print("Token Reduced Object Notation")
print("=" * 70)
print()

# =============================================================================
# Example 1: Simple Object
# =============================================================================
print("1. SIMPLE OBJECT")
print("-" * 70)

data = {
    "name": "Alice Johnson",
    "age": 30,
    "email": "alice@example.com",
    "active": True,
    "score": 95.5,
}

print("Input:")
print(data)
print()

# Encode to TRON
tron_str = encode(data, format="tron")
print("TRON output:")
print(tron_str)
print()

# Decode back
decoded = decode(tron_str, format="tron")
print(f"Round-trip match: {decoded == data}")
print()

# =============================================================================
# Example 2: Nested Objects (Dot Notation)
# =============================================================================
print("2. NESTED OBJECTS (Dot Notation)")
print("-" * 70)

data = {
    "user": {"name": "Bob", "profile": {"age": 28, "city": "NYC"}},
    "settings": {"theme": "dark", "notifications": True},
}

print("Input:")
print(data)
print()

tron_str = encode(data, format="tron")
print("TRON output:")
print(tron_str)
print()
print("Notice: Nested keys become dot notation (user.profile.age=28)")
print()

# =============================================================================
# Example 3: Arrays
# =============================================================================
print("3. ARRAYS")
print("-" * 70)

data = {
    "tags": ["python", "machine-learning", "nlp"],
    "scores": [95, 87, 92, 78],
    "flags": [True, False, True],
}

print("Input:")
print(data)
print()

tron_str = encode(data, format="tron")
print("TRON output:")
print(tron_str)
print()
print("Notice: Arrays use [item1;item2;item3] syntax, booleans become 1/0")
print()

# =============================================================================
# Example 4: Tabular Data (Arrays of Objects)
# =============================================================================
print("4. TABULAR DATA (Arrays of Objects)")
print("-" * 70)

data = [
    {"id": 1, "name": "Alice", "dept": "Engineering", "salary": 95000},
    {"id": 2, "name": "Bob", "dept": "Sales", "salary": 75000},
    {"id": 3, "name": "Carol", "dept": "Marketing", "salary": 85000},
]

print("Input:")
for row in data:
    print(f"  {row}")
print()

tron_str = encode(data, format="tron")
print("TRON output:")
print(tron_str)
print()
print("Notice: Tabular format uses @header|row1|row2|row3")
print()

# =============================================================================
# Example 5: Special Values
# =============================================================================
print("5. SPECIAL VALUES")
print("-" * 70)

data = {"enabled": True, "disabled": False, "empty": None, "count": 0, "pi": 3.14159}

print("Input:")
print(data)
print()

tron_str = encode(data, format="tron")
print("TRON output:")
print(tron_str)
print()
print("Notice: True→1, False→0, None→~")
print()

# =============================================================================
# Example 6: Format Comparison
# =============================================================================
print("6. FORMAT COMPARISON")
print("-" * 70)

import json

data = {
    "users": [
        {"id": 1, "name": "User1", "active": True},
        {"id": 2, "name": "User2", "active": False},
        {"id": 3, "name": "User3", "active": True},
    ]
}

json_str = json.dumps(data, separators=(",", ":"))
toon_str = encode(data, format="toon")
tron_str = encode(data, format="tron")

print("Input: 3 user records")
print()
print(f"JSON Compact ({len(json_str)} chars):")
print(f"  {json_str}")
print()
print(f"TOON ({len(toon_str)} chars):")
print(f"  {toon_str.replace(chr(10), ' ')[:80]}...")
print()
print(f"TRON ({len(tron_str)} chars):")
print(f"  {tron_str}")
print()
print(f"TRON saves {(1 - len(tron_str)/len(json_str))*100:.1f}% characters vs JSON Compact")
print()

# =============================================================================
# Example 7: Decoding TRON
# =============================================================================
print("7. DECODING TRON")
print("-" * 70)

# Manual TRON strings
tron_samples = [
    "name=Alice;age=30;active=1",
    "user.name=Bob;user.age=25",
    "@id,name|1,Alice|2,Bob|3,Carol",
    "tags=[python;ml;ai];count=3",
]

print("Decoding manual TRON strings:")
print()
for tron in tron_samples:
    decoded = decode(tron, format="tron")
    print(f"  TRON: {tron}")
    print(f"  Data: {decoded}")
    print()

# =============================================================================
# Example 8: Real-World API Response
# =============================================================================
print("8. REAL-WORLD API RESPONSE")
print("-" * 70)

api_response = {
    "status": "success",
    "data": {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
            {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
        ],
        "total": 2,
        "page": 1,
    },
    "meta": {"version": "2.0.0", "timestamp": "2025-12-01T12:00:00Z"},
}

print("API Response:")
json_str = json.dumps(api_response, separators=(",", ":"))
tron_str = encode(api_response, format="tron")

print(f"  JSON Compact: {len(json_str)} chars")
print(f"  TRON:         {len(tron_str)} chars")
print(f"  Savings:      {(1 - len(tron_str)/len(json_str))*100:.1f}%")
print()
print("TRON output:")
print(tron_str)
print()

# =============================================================================
# Example 9: Explicit Format Selection
# =============================================================================
print("9. EXPLICIT FORMAT SELECTION")
print("-" * 70)

# Always specify format explicitly for best results
data = {"name": "Alice", "age": 30}

print("Same data in different formats:")
print()
print(f"  TOON: {encode(data, format='toon')}")
print(f"  TRON: {encode(data, format='tron')}")
print(f"  JSON: {json.dumps(data)}")
print()
print("Tip: Always use format='tron' when encoding/decoding TRON data")
print()

# =============================================================================
# Summary
# =============================================================================
print("=" * 70)
print("TRON FORMAT SUMMARY")
print("=" * 70)
print()
print("TRON Syntax Rules:")
print("  • Key=Value pairs separated by ;")
print("  • Nested objects: user.profile.name=Alice")
print("  • Arrays: [item1;item2;item3]")
print("  • Tabular: @col1,col2|row1val1,row1val2|row2val1,row2val2")
print("  • Booleans: 1 (true), 0 (false)")
print("  • Null: ~")
print('  • Quoted strings for special chars: "value;with;semicolons"')
print()
print("When to Use TRON:")
print("  ✓ LLM context optimization (61% fewer tokens vs JSON)")
print("  ✓ Simple key-value configurations")
print("  ✓ Nested settings/configs")
print("  ✓ Streaming data to LLMs")
print("  ✓ Logging and telemetry")
print()
print("API Usage:")
print("  encode(data, format='tron')  # Encode to TRON")
print("  decode(tron_str, format='tron')  # Decode from TRON")
print("  decode(data, format='auto')  # Auto-detect format")
print()
