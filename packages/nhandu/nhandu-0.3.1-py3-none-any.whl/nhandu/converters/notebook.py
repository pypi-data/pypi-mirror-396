"""
Jupyter Notebook import/export functionality.

This module provides conversion between Jupyter notebooks (.ipynb) and
Nhandu's literate Python format (.py).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Handle optional nbformat dependency
NBFORMAT_AVAILABLE = False
nbformat: Any = None

try:
    import nbformat as _nbformat

    nbformat = _nbformat
    NBFORMAT_AVAILABLE = True
except ImportError:
    pass

# NotebookNode is used in type annotations only - with __future__.annotations
# these are evaluated as strings, so we don't need the actual import
NotebookNode = Any  # Runtime placeholder for type annotations


def _check_nbformat() -> None:
    """
    Check if nbformat is available and raise helpful error if not.

    @raise ImportError: If nbformat is not installed with install instructions.
    """
    if not NBFORMAT_AVAILABLE:
        raise ImportError(
            "nbformat is required for Jupyter notebook conversion.\n"
            "Install it with: pip install nhandu[jupyter]\n"
            "Or directly: pip install nbformat"
        )


def _extract_frontmatter(notebook: NotebookNode) -> dict[str, Any]:
    """
    Extract metadata from notebook to YAML frontmatter format.

    @param notebook: Jupyter notebook object.
    @return: Dictionary of metadata for frontmatter.
    """
    metadata = {}

    # Extract common metadata fields
    nb_metadata = notebook.get("metadata", {})

    # Title (various sources)
    if "title" in nb_metadata:
        metadata["title"] = nb_metadata["title"]

    # Authors
    if "authors" in nb_metadata:
        authors = nb_metadata["authors"]
        if isinstance(authors, list) and authors:
            # Join author names
            metadata["author"] = ", ".join(
                a.get("name", str(a)) if isinstance(a, dict) else str(a)
                for a in authors
            )
        elif authors:
            metadata["author"] = str(authors)

    # Language info
    language_info = nb_metadata.get("language_info", {})
    if language_info:
        lang_name = language_info.get("name")
        if lang_name and lang_name != "python":
            metadata["language"] = lang_name

    # Kernel info (informational)
    kernelspec = nb_metadata.get("kernelspec", {})
    if kernelspec and kernelspec.get("name") != "python3":
        metadata["kernel"] = kernelspec.get("name")

    return metadata


def _convert_inline_code_to_fstring(text: str) -> str:
    """
    Convert inline code expressions to f-strings where possible.

    Converts <%= expr %> to {expr} and wraps in f-string markers.
    Leaves <% stmt %> statements as-is (cannot convert to f-string).

    @param text: Text containing inline code expressions.
    @return: Text with inline code converted to f-string format where possible.
    """
    # Pattern to find <%= expression %>
    pattern = r"<%=\s*(.+?)\s*%>"

    # Check if we have any expressions to convert
    if not re.search(pattern, text):
        return text

    # Convert <%= expr %> to {expr}
    converted = re.sub(pattern, r"{\1}", text)

    return converted


def _format_markdown_cell(source: str) -> list[str]:
    """
    Format markdown cell content as Nhandu #' comments.

    @param source: Markdown cell source (may be string or list).
    @return: List of formatted lines with #' prefix.
    """
    # Handle both string and list sources
    if isinstance(source, list):
        source = "".join(source)

    lines = []
    for line in source.splitlines():
        # Convert inline code if present
        line = _convert_inline_code_to_fstring(line)
        lines.append(f"#' {line}\n" if line.strip() else "#'\n")

    return lines


def _format_code_cell(source: str, is_hidden: bool = False) -> list[str]:
    """
    Format code cell content as Python code.

    @param source: Code cell source (may be string or list).
    @param is_hidden: Whether to wrap in #| hide ... #| block.
    @return: List of formatted Python code lines.
    """
    # Handle both string and list sources
    if isinstance(source, list):
        source = "".join(source)

    lines = []

    if is_hidden:
        lines.append("#| hide\n")

    # Add code directly (no modification)
    for line in source.splitlines():
        lines.append(f"{line}\n")

    if is_hidden:
        lines.append("#|\n")

    return lines


def _format_raw_cell(source: str) -> list[str]:
    """
    Format raw cell content as markdown code block.

    @param source: Raw cell source (may be string or list).
    @return: List of formatted lines in markdown code block.
    """
    # Handle both string and list sources
    if isinstance(source, list):
        source = "".join(source)

    lines = [
        "#' ```\n",
    ]

    for line in source.splitlines():
        lines.append(f"#' {line}\n")

    lines.append("#' ```\n")

    return lines


def import_notebook(ipynb_path: Path, output_path: Path) -> None:
    """
    Import Jupyter notebook to Nhandu literate Python format.

    Converts a .ipynb file to .py format with:
    - Markdown cells → #' comments
    - Code cells → Regular Python code
    - Raw cells → Markdown code blocks
    - Metadata → YAML frontmatter
    - Outputs are discarded (regeneratable)

    @param ipynb_path: Path to input .ipynb file.
    @param output_path: Path to output .py file.
    @raise ImportError: If nbformat is not installed.
    @raise FileNotFoundError: If input file doesn't exist.
    @raise ValueError: If notebook format is invalid.
    """
    _check_nbformat()

    if not ipynb_path.exists():
        raise FileNotFoundError(f"Notebook not found: {ipynb_path}")

    # Read notebook
    with open(ipynb_path, encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    # Extract metadata
    metadata = _extract_frontmatter(notebook)

    # Build output content
    lines: list[str] = []

    # Add frontmatter if we have metadata
    if metadata:
        lines.append("#' ---\n")
        for key, value in metadata.items():
            # Handle multiline values
            if isinstance(value, str) and "\n" in value:
                lines.append(f"#' {key}: |\n")
                for line in value.splitlines():
                    lines.append(f"#'   {line}\n")
            else:
                lines.append(f"#' {key}: {value}\n")
        lines.append("#' ---\n")
        lines.append("#'\n")

    # Process cells
    for cell in notebook.cells:
        cell_type = cell.get("cell_type")
        source = cell.get("source", "")

        # Skip empty cells
        if not source or (isinstance(source, list) and not any(source)):
            continue

        if cell_type == "markdown":
            lines.extend(_format_markdown_cell(source))
            lines.append("#'\n")  # Blank line after markdown

        elif cell_type == "code":
            # Check if cell should be hidden (from tags or metadata)
            tags = cell.get("metadata", {}).get("tags", [])
            is_hidden = "hide" in tags or "hidden" in tags

            lines.extend(_format_code_cell(source, is_hidden=is_hidden))
            lines.append("\n")  # Blank line after code

        elif cell_type == "raw":
            lines.extend(_format_raw_cell(source))
            lines.append("#'\n")  # Blank line after raw

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def export_notebook(
    py_path: Path,
    output_path: Path,
    execute: bool = False,
    kernel: str = "python3",
) -> None:
    """
    Export Nhandu literate Python file to Jupyter notebook format.

    Converts a .py file to .ipynb format with:
    - #' comments → Markdown cells
    - Regular code → Code cells
    - Hidden blocks (#| hide) → Code cells with "hide" tag
    - YAML frontmatter → Notebook metadata
    - No outputs by default (symmetric to import)

    @param py_path: Path to input .py file.
    @param output_path: Path to output .ipynb file.
    @param execute: Whether to execute notebook after creation (default: False).
    @param kernel: Kernel name to use if executing (default: "python3").
    @raise ImportError: If nbformat is not installed.
    @raise FileNotFoundError: If input file doesn't exist.
    """
    _check_nbformat()

    if not py_path.exists():
        raise FileNotFoundError(f"Python file not found: {py_path}")

    # Read and parse the Python file
    with open(py_path, encoding="utf-8") as f:
        content = f.read()

    # Parse the content (we'll use a simple regex-based parser)
    cells = _parse_py_to_cells(content)

    # Extract metadata from frontmatter
    metadata = _extract_metadata_from_py(content)

    # Create notebook structure
    notebook = nbformat.v4.new_notebook()

    # Set metadata
    notebook.metadata.update(
        {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": kernel,
            },
            "language_info": {
                "name": "python",
                "version": "3.10",
                "mimetype": "text/x-python",
                "codemirror_mode": {"name": "ipython", "version": 3},
                "pygments_lexer": "ipython3",
            },
        }
    )

    # Add custom metadata from frontmatter
    if metadata:
        notebook.metadata.update(metadata)

    # Add cells
    notebook.cells = cells

    # Write notebook
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        nbformat.write(notebook, f)

    # Execute if requested
    if execute:
        from nbconvert.preprocessors import ExecutePreprocessor

        ep = ExecutePreprocessor(timeout=600, kernel_name=kernel)
        ep.preprocess(notebook)

        # Write again with outputs
        with open(output_path, "w", encoding="utf-8") as f:
            nbformat.write(notebook, f)


def _parse_py_to_cells(content: str) -> list[NotebookNode]:
    """
    Parse Python literate file content into notebook cells.

    @param content: Content of .py file.
    @return: List of notebook cells.
    """
    cells = []
    lines = content.splitlines(keepends=True)

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for markdown comment
        if line.strip().startswith("#'"):
            # Collect consecutive markdown lines
            md_lines = []
            while i < len(lines) and lines[i].strip().startswith("#'"):
                # Remove #' prefix and leading space
                text = lines[i].lstrip("#'").lstrip(" ")
                # Skip frontmatter (handled separately)
                if text.strip() == "---":
                    # Skip frontmatter block
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith(
                        "#' ---"
                    ):
                        i += 1
                    i += 1  # Skip closing ---
                    continue
                md_lines.append(text)
                i += 1

            # Create markdown cell if we have content
            if md_lines:
                md_text = "".join(md_lines).rstrip()
                if md_text.strip():  # Only add non-empty cells
                    cells.append(nbformat.v4.new_markdown_cell(md_text))

        # Check for hidden code block
        elif line.strip() == "#| hide":
            # Collect code until #|
            code_lines = []
            i += 1  # Skip #| hide line
            while i < len(lines) and lines[i].strip() != "#|":
                code_lines.append(lines[i])
                i += 1
            i += 1  # Skip closing #| line

            # Create code cell with hide tag
            if code_lines:
                code_text = "".join(code_lines).rstrip()
                if code_text.strip():
                    cell = nbformat.v4.new_code_cell(code_text)
                    cell.metadata.tags = ["hide"]
                    cells.append(cell)

        # Regular code (including Python comments, but not #' or #|)
        elif (
            line.strip()
            and not line.strip().startswith("#'")
            and not line.strip().startswith("#|")
        ):
            # Collect consecutive code lines (including Python # comments)
            code_lines = []
            while i < len(lines):
                curr_line = lines[i]
                # Stop at markdown comments or hidden blocks
                if curr_line.strip().startswith(
                    "#'"
                ) or curr_line.strip().startswith("#| hide"):
                    break
                # Stop at blank lines followed by markdown
                if (
                    not curr_line.strip()
                    and i + 1 < len(lines)
                    and lines[i + 1].strip().startswith("#'")
                ):
                    break
                code_lines.append(curr_line)
                i += 1

            # Create code cell
            if code_lines:
                code_text = "".join(code_lines).rstrip()
                if code_text.strip():
                    cells.append(nbformat.v4.new_code_cell(code_text))

        else:
            # Skip blank lines
            i += 1

    return cells


def _extract_metadata_from_py(content: str) -> dict[str, Any]:
    """
    Extract YAML frontmatter metadata from Python literate file.

    @param content: Content of .py file.
    @return: Dictionary of metadata.
    """
    metadata = {}
    lines = content.splitlines()

    # Look for frontmatter
    in_frontmatter = False
    frontmatter_lines = []

    for line in lines:
        stripped = line.strip()

        # Check for start of frontmatter
        if stripped == "#' ---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                # End of frontmatter
                break

        if in_frontmatter:
            # Remove #' prefix
            text = line.lstrip("#'").lstrip(" ")
            frontmatter_lines.append(text)

    # Parse frontmatter YAML
    if frontmatter_lines:
        try:
            import yaml

            yaml_text = "\n".join(frontmatter_lines)
            parsed = yaml.safe_load(yaml_text)
            if isinstance(parsed, dict):
                metadata = parsed
        except ImportError:
            # If yaml not available, do basic parsing
            for line in frontmatter_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
        except Exception:
            # Silently ignore parsing errors
            pass

    return metadata
