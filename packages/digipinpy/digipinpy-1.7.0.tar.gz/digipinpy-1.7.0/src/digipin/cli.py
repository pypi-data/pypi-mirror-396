"""
Command-line interface for digipin-py.

Provides easy command-line access to encode, decode, and validate DIGIPIN codes.

SECURITY NOTE:
This CLI tool outputs location data (coordinates/DIGIPIN codes) to stdout,
which is the expected behavior for command-line tools. If you redirect this
output to log files in production systems, ensure appropriate access controls
and data retention policies are in place to protect potentially sensitive
location information.
"""

import sys
import argparse
from typing import Optional, Dict, Any

# Fix Windows console encoding for unicode characters
if sys.platform == "win32":
    try:
        import io

        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except:
        pass  # Fallback to ASCII-safe characters if encoding fix fails

from . import (
    encode,
    decode,
    is_valid,
    get_bounds,
    get_precision_info,
    __version__,
)


def cmd_encode(args):
    """Handle the encode command."""
    try:
        code = encode(args.latitude, args.longitude, precision=args.precision)

        if args.format == "json":
            import json

            output = {
                "code": code,
                "latitude": args.latitude,
                "longitude": args.longitude,
                "precision": args.precision,
            }
            print(json.dumps(output, indent=2))
        else:
            print(code)

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_decode(args):
    """Handle the decode command."""
    try:
        # Decode expects full 10-char code or partial code
        code = args.code
        if args.precision < 10:
            code = args.code[: args.precision]

        lat, lon = decode(code)

        if args.format == "json":
            import json

            output: Dict[str, Any] = {"latitude": lat, "longitude": lon}
            if args.bbox:
                min_lat, max_lat, min_lon, max_lon = get_bounds(code)
                output["bbox"] = {
                    "min_lat": min_lat,
                    "max_lat": max_lat,
                    "min_lon": min_lon,
                    "max_lon": max_lon,
                }
            print(json.dumps(output, indent=2))
        else:
            print(f"Latitude:  {lat}")
            print(f"Longitude: {lon}")

            if args.bbox:
                min_lat, max_lat, min_lon, max_lon = get_bounds(code)
                print(f"\nBounding Box:")
                print(f"  Latitude:  {min_lat} to {max_lat}")
                print(f"  Longitude: {min_lon} to {max_lon}")

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_validate(args):
    """Handle the validate command."""
    valid = is_valid(args.code)

    if args.format == "json":
        import json

        output = {"code": args.code, "valid": valid}
        if valid and args.detailed:
            try:
                lat, lon = decode(args.code)
                output["latitude"] = lat
                output["longitude"] = lon
            except:
                pass
        elif not valid and args.detailed:
            output["expected_format"] = {"length": 10, "symbols": "23456789CFJKLMPT"}
        print(json.dumps(output, indent=2))
    elif args.detailed:
        if valid:
            print("✓ Valid DIGIPIN code")
            try:
                lat, lon = decode(args.code)
                print(f"\nDecodes to:")
                print(f"  Latitude:  {lat}")
                print(f"  Longitude: {lon}")
            except:
                pass
        else:
            print("✗ Invalid DIGIPIN code")
            print("\nExpected format:")
            print(f"  - Exactly 10 characters")
            print(f"  - Using symbols: 23456789CFJKLMPT")
    else:
        print("Valid" if valid else "Invalid")

    return 0 if valid else 1


def cmd_info(args):
    """Handle the info command."""
    info = get_precision_info(args.precision)

    print(f"DIGIPIN Precision Information")
    print(f"{'=' * 40}")
    print(f"Level:               {info['level']}")
    print(f"Code length:         {info['code_length']}")
    print(f"Grid cells:          {info['total_cells']:,}")
    print(f"Approx. distance:    ~{info['approx_distance_m']:.2f} meters")
    print(f"Description:         {info['description']}")

    return 0


def main(argv: Optional[list] = None):
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="digipin",
        description="DIGIPIN: Open geocoding system for India",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  digipin encode 28.622788 77.213033
  digipin decode 39J49LL8T4
  digipin validate 39J49LL8T4
  digipin info

For more information, visit: https://github.com/DEADSERPENT/digipin
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Encode command
    encode_parser = subparsers.add_parser(
        "encode", help="Encode latitude/longitude to DIGIPIN code"
    )
    encode_parser.add_argument("latitude", type=float, help="Latitude (2.5 to 38.5)")
    encode_parser.add_argument("longitude", type=float, help="Longitude (63.5 to 99.5)")
    encode_parser.add_argument(
        "-p",
        "--precision",
        type=int,
        default=10,
        help="Code length (1-10, default: 10)",
    )
    encode_parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    encode_parser.set_defaults(func=cmd_encode)

    # Decode command
    decode_parser = subparsers.add_parser(
        "decode", help="Decode DIGIPIN code to latitude/longitude"
    )
    decode_parser.add_argument("code", type=str, help="DIGIPIN code to decode")
    decode_parser.add_argument(
        "-p",
        "--precision",
        type=int,
        default=10,
        help="Code length (1-10, default: 10)",
    )
    decode_parser.add_argument(
        "-b", "--bbox", action="store_true", help="Include bounding box in output"
    )
    decode_parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    decode_parser.set_defaults(func=cmd_decode)

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a DIGIPIN code")
    validate_parser.add_argument("code", type=str, help="DIGIPIN code to validate")
    validate_parser.add_argument(
        "-p",
        "--precision",
        type=int,
        default=10,
        help="Code length (1-10, default: 10)",
    )
    validate_parser.add_argument(
        "-d",
        "--detailed",
        action="store_true",
        help="Show detailed validation information",
    )
    validate_parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    validate_parser.set_defaults(func=cmd_validate)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show precision information")
    info_parser.add_argument(
        "-p",
        "--precision",
        type=int,
        default=10,
        help="Code length (1-10, default: 10)",
    )
    info_parser.set_defaults(func=cmd_info)

    # Parse arguments
    args = parser.parse_args(argv)

    # Handle no command
    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
