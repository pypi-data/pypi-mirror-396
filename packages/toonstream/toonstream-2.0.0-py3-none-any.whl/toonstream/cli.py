import argparse
import json
import sys
from typing import Any, Dict, List, Optional
from .unified_api import encode, decode

def load_input(file_path: str, raw_string: bool = False) -> Any:
    """Load input data from file or stdin."""
    if file_path == "-":
        content = sys.stdin.read()
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    
    if raw_string:
        return content

    # Try to parse as JSON first (for encode)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return content

def save_output(data: Any, file_path: str, indent: Optional[int] = None) -> None:
    """Save output data to file or stdout."""
    if isinstance(data, (dict, list)) and indent is not None:
        content = json.dumps(data, indent=indent)
    elif isinstance(data, (dict, list)):
        content = json.dumps(data)
    else:
        content = str(data)
        
    if file_path == "-":
        sys.stdout.write(content)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ToonStream: Token-Oriented Object Notation CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Encode command
    encode_parser = subparsers.add_parser("encode", help="Convert JSON to TOON/TRON")
    encode_parser.add_argument("input", help="Input file path (or - for stdin)")
    encode_parser.add_argument("-o", "--output", help="Output file path (default: stdout)", default="-")
    encode_parser.add_argument(
        "--format", choices=["toon", "tron"], default="toon", help="Output format"
    )
    encode_parser.add_argument(
        "--auto", action="store_true", help="Enable auto-mode (tensor detection)"
    )

    # Decode command
    decode_parser = subparsers.add_parser("decode", help="Convert TOON/TRON to JSON")
    decode_parser.add_argument("input", help="Input file path (or - for stdin)")
    decode_parser.add_argument("-o", "--output", help="Output file path (default: stdout)", default="-")
    decode_parser.add_argument(
        "--format", choices=["toon", "tron"], default="toon", help="Input format hint"
    )
    decode_parser.add_argument(
        "--indent", type=int, help="Indentation for JSON output", default=2
    )
    decode_parser.add_argument(
        "--auto", action="store_true", help="Enable auto-mode"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        
        if args.command == "encode":
            input_data = load_input(args.input, raw_string=False)
            if not isinstance(input_data, (dict, list)):
                print("Error: Input for encoding must be valid JSON object or array", file=sys.stderr)
                sys.exit(1)
            
            result = encode(input_data, format=args.format, auto_mode=args.auto)
            save_output(result, args.output)
            
        elif args.command == "decode":
            input_str = load_input(args.input, raw_string=True)
            result = decode(str(input_str), format=args.format, auto_mode=args.auto)
            save_output(result, args.output, indent=args.indent)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
