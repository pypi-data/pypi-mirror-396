"""Command-line interface for PowerPoint to HTML5 converter."""

import argparse
import sys
from pathlib import Path

from pptx_to_html5.converter import PowerPointToHTML5Converter


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        description="Convert PowerPoint presentations to HTML5 websites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pptx-to-html presentation.pptx
  pptx-to-html presentation.pptx -o output_folder
  pptx-to-html presentation.pptx --include-notes
        """,
    )

    parser.add_argument(
        "input",
        type=str,
        help="Path to the PowerPoint file (.pptx)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output directory (default: input filename without extension)",
    )

    parser.add_argument(
        "-n",
        "--include-notes",
        action="store_true",
        help="Include speaker notes in the output",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    args = parser.parse_args()

    # Determine output directory
    input_path = Path(args.input)
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = input_path.parent / input_path.stem

    try:
        # Create converter and convert
        converter = PowerPointToHTML5Converter(args.input)
        output_file = converter.convert(output_dir, include_notes=args.include_notes)

        print("✓ Successfully converted presentation to HTML5")
        print(f"✓ Output: {output_file}")
        print(f"\nOpen {output_file} in your web browser to view the presentation.")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
