"""Command-line interface for Nhandu."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nhandu import __version__, execute, parse, render
from nhandu.models import Document


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    # Handle the case where user provides a file without a subcommand
    # (backward compatibility)
    if argv is None:
        argv = sys.argv[1:]

    # If first arg looks like a file and not a subcommand, parse as default mode
    if (
        argv
        and not argv[0].startswith("-")
        and argv[0] not in ["import-notebook", "export-notebook"]
    ):
        # Default mode: process document
        parser = create_default_argument_parser()
        args = parser.parse_args(argv)

        if args.version:
            print(f"nhandu {__version__}")
            return 0

        try:
            process_document(args)
            return 0
        except Exception as e:
            if args.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"Error: {e}", file=sys.stderr)
            return 1

    # Subcommand mode
    parser = create_argument_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"nhandu {__version__}")
        return 0

    try:
        # Dispatch to appropriate handler
        if hasattr(args, "func"):
            args.func(args)
        else:
            # No subcommand and no file - show help
            parser.print_help()
            return 1
        return 0
    except Exception as e:
        verbose = getattr(args, "verbose", False)
        if verbose:
            import traceback

            traceback.print_exc()
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


def create_default_argument_parser() -> argparse.ArgumentParser:
    """Create the default argument parser (for processing documents)."""
    parser = argparse.ArgumentParser(
        prog="nhandu",
        description="A literate programming tool for Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "input",
        help="Input file to process (.py literate Python)",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: input with appropriate extension)",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "md", "html"],
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--config",
        help="Configuration file (YAML)",
    )

    parser.add_argument(
        "--working-dir",
        help="Working directory for code execution",
    )

    parser.add_argument(
        "--code-theme",
        help="Syntax highlighting theme for HTML output (e.g., github-dark, monokai)",
    )

    parser.add_argument(
        "--no-footer",
        action="store_true",
        help="Disable 'Made with Nhandu' footer in HTML output",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit",
    )

    return parser


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="nhandu",
        description="A literate programming tool for Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global arguments
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit",
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand: import-notebook
    import_parser = subparsers.add_parser(
        "import-notebook",
        help="Import Jupyter notebook to Nhandu format",
        description=(
            "Convert a Jupyter notebook (.ipynb) to Nhandu literate Python (.py)"
        ),
    )
    import_parser.add_argument(
        "input",
        help="Input Jupyter notebook file (.ipynb)",
    )
    import_parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output Python file (.py)",
    )
    import_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    import_parser.set_defaults(func=import_notebook_command)

    # Subcommand: export-notebook
    export_parser = subparsers.add_parser(
        "export-notebook",
        help="Export Nhandu document to Jupyter notebook",
        description=(
            "Convert a Nhandu literate Python file (.py) to Jupyter notebook (.ipynb)"
        ),
    )
    export_parser.add_argument(
        "input",
        help="Input Nhandu Python file (.py)",
    )
    export_parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output Jupyter notebook file (.ipynb)",
    )
    export_parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute notebook after creation",
    )
    export_parser.add_argument(
        "--kernel",
        default="python3",
        help="Kernel name to use if executing (default: python3)",
    )
    export_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    export_parser.set_defaults(func=export_notebook_command)

    return parser


def process_document(args: argparse.Namespace) -> None:
    """Process a Nhandu document."""
    if not args.input:
        raise ValueError("No input file specified")

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Read input file
    content = input_path.read_text(encoding="utf-8")

    # Parse document (Python literate format)
    if args.verbose:
        print(f"Parsing {input_path}...")

    doc = parse(content, str(input_path))

    # Load config if specified
    if args.config:
        load_config(doc, args.config)

    # Override with CLI arguments
    if args.format:
        doc.metadata.output = args.format.replace("md", "markdown")
    if args.code_theme:
        doc.metadata.code_theme = args.code_theme
    if args.no_footer:
        doc.metadata.show_footer = False

    # Execute code blocks
    if args.verbose:
        print("Executing code blocks...")
    executed_doc = execute(
        doc,
        working_dir=args.working_dir or doc.metadata.working_dir,
    )

    # Determine output format
    output_format = doc.metadata.output

    # Render output
    if args.verbose:
        print(f"Rendering to {output_format}...")
    output_content = render(executed_doc, output_format)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Generate output filename: source.out.ext or source.html
        if output_format == "html":
            output_path = input_path.with_suffix(".html")
        else:
            # Insert .out before extension: test.md -> test.out.md
            output_path = input_path.with_suffix(f".out{input_path.suffix}")

    # Write output
    output_path.write_text(output_content, encoding="utf-8")

    if args.verbose:
        print(f"Output written to {output_path}")

    # Print any execution errors
    if executed_doc.execution_errors:
        print("\nExecution errors encountered:", file=sys.stderr)
        for error in executed_doc.execution_errors:
            print(f"  - {error}", file=sys.stderr)


def load_config(doc: Document, config_path: str) -> None:
    """Load configuration from a YAML file."""
    import yaml

    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file) as f:
        config_data = yaml.safe_load(f)

    # Update document metadata with config
    if config_data:
        for key, value in config_data.items():
            if hasattr(doc.metadata, key):
                setattr(doc.metadata, key, value)
            doc.metadata.raw[key] = value


def import_notebook_command(args: argparse.Namespace) -> None:
    """
    Handle import-notebook command.

    @param args: Command-line arguments.
    """
    from nhandu.converters import import_notebook

    input_path = Path(args.input)
    output_path = Path(args.output)

    if args.verbose:
        print(f"Importing notebook {input_path} to {output_path}...")

    import_notebook(input_path, output_path)

    if args.verbose:
        print(f"Successfully imported to {output_path}")
        print(
            "\nNote: Notebook outputs were discarded. "
            "Run the file with nhandu to regenerate them."
        )


def export_notebook_command(args: argparse.Namespace) -> None:
    """
    Handle export-notebook command.

    @param args: Command-line arguments.
    """
    from nhandu.converters import export_notebook

    input_path = Path(args.input)
    output_path = Path(args.output)

    if args.verbose:
        print(f"Exporting {input_path} to notebook {output_path}...")

    export_notebook(
        input_path,
        output_path,
        execute=args.execute,
        kernel=args.kernel,
    )

    if args.verbose:
        if args.execute:
            print(f"Successfully exported and executed to {output_path}")
        else:
            print(f"Successfully exported to {output_path}")
            print(
                "\nNote: Notebook has no outputs. "
                "Open in Jupyter and run cells to generate outputs."
            )


if __name__ == "__main__":
    sys.exit(main())
