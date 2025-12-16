"""Tests for Jupyter notebook import/export functionality."""

from __future__ import annotations

from pathlib import Path

import pytest

# Skip all tests if nbformat is not available
nbformat = pytest.importorskip("nbformat")

from nhandu.converters import export_notebook, import_notebook


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory for tests."""
    return tmp_path / "output"


@pytest.fixture
def fixtures_dir() -> Path:
    """Get the fixtures directory path."""
    return Path(__file__).parent / "fixtures" / "notebooks"


def test_import_simple_notebook(fixtures_dir: Path, temp_output_dir: Path) -> None:
    """Test importing a simple Jupyter notebook."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    input_file = fixtures_dir / "simple_notebook.ipynb"
    output_file = temp_output_dir / "simple.py"

    import_notebook(input_file, output_file)

    assert output_file.exists()
    content = output_file.read_text()

    # Check that markdown cells are converted to #' comments
    assert "#' # Simple Notebook" in content
    assert "#' This is a simple test notebook" in content
    assert "#' ## Results" in content

    # Check that code cells are present
    assert "import math" in content
    assert "x = 42" in content
    assert "result = math.sqrt(x)" in content


def test_import_discards_outputs(fixtures_dir: Path, temp_output_dir: Path) -> None:
    """Test that notebook outputs are discarded during import."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    input_file = fixtures_dir / "notebook_with_outputs.ipynb"
    output_file = temp_output_dir / "no_outputs.py"

    import_notebook(input_file, output_file)

    assert output_file.exists()
    content = output_file.read_text()

    # Code should be present
    assert 'print("Hello, world!")' in content
    assert "x = 42" in content
    assert "x * 2" in content

    # Outputs should NOT be present
    assert "Hello, world!" not in content.replace('print("Hello, world!")', "")
    assert "84" not in content.replace("x = 42", "")


def test_import_extracts_metadata(fixtures_dir: Path, temp_output_dir: Path) -> None:
    """Test that notebook metadata is extracted to YAML frontmatter."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    input_file = fixtures_dir / "notebook_with_metadata.ipynb"
    output_file = temp_output_dir / "with_metadata.py"

    import_notebook(input_file, output_file)

    assert output_file.exists()
    content = output_file.read_text()

    # Check frontmatter
    assert "#' ---" in content
    assert "#' title: My Research Notebook" in content
    assert "#' author: Alice Smith, Bob Jones" in content


def test_import_handles_hidden_cells(
    fixtures_dir: Path, temp_output_dir: Path
) -> None:
    """Test that cells with 'hide' tag are converted to #| hide blocks."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    input_file = fixtures_dir / "notebook_with_hidden_cells.ipynb"
    output_file = temp_output_dir / "with_hidden.py"

    import_notebook(input_file, output_file)

    assert output_file.exists()
    content = output_file.read_text()

    # Hidden cell should be in a hide block
    assert "#| hide" in content
    assert "SECRET_KEY" in content
    assert "#|" in content

    # Regular code should not be in hide block
    lines = content.split("\n")
    hidden_block_start = None
    hidden_block_end = None

    for i, line in enumerate(lines):
        if line.strip() == "#| hide":
            hidden_block_start = i
        elif hidden_block_start and line.strip() == "#|":
            hidden_block_end = i
            break

    # Verify visible code is outside the hidden block
    visible_code_line = None
    for i, line in enumerate(lines):
        if "x = 42" in line:
            visible_code_line = i
            break

    assert visible_code_line is not None
    assert hidden_block_end is not None
    assert visible_code_line > hidden_block_end


def test_import_nonexistent_file(temp_output_dir: Path) -> None:
    """Test that importing nonexistent file raises FileNotFoundError."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    input_file = Path("/nonexistent/notebook.ipynb")
    output_file = temp_output_dir / "output.py"

    with pytest.raises(FileNotFoundError):
        import_notebook(input_file, output_file)


def test_export_creates_notebook(temp_output_dir: Path) -> None:
    """Test exporting a Nhandu file to Jupyter notebook."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    # Create a simple Nhandu file
    input_file = temp_output_dir / "input.py"
    input_file.write_text(
        "#' # Test Document\n"
        "#'\n"
        "#' Some markdown content.\n"
        "\n"
        "x = 42\n"
        "print(x)\n"
    )

    output_file = temp_output_dir / "output.ipynb"

    export_notebook(input_file, output_file)

    assert output_file.exists()

    # Read and parse notebook
    with open(output_file) as f:
        nb = nbformat.read(f, as_version=4)

    assert len(nb.cells) >= 2

    # First cell should be markdown
    assert nb.cells[0].cell_type == "markdown"
    assert "# Test Document" in nb.cells[0].source

    # Second cell should be code
    assert nb.cells[1].cell_type == "code"
    assert "x = 42" in nb.cells[1].source


def test_export_with_hidden_blocks(temp_output_dir: Path) -> None:
    """Test that hidden blocks are exported with 'hide' tag."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    # Create file with hidden block
    input_file = temp_output_dir / "input.py"
    input_file.write_text(
        "#' # Document\n"
        "\n"
        "#| hide\n"
        "secret = 123\n"
        "#|\n"
        "\n"
        "public = 456\n"
    )

    output_file = temp_output_dir / "output.ipynb"

    export_notebook(input_file, output_file)

    assert output_file.exists()

    # Read notebook
    with open(output_file) as f:
        nb = nbformat.read(f, as_version=4)

    # Find the hidden cell
    hidden_cell = None
    for cell in nb.cells:
        if cell.cell_type == "code" and "secret" in cell.source:
            hidden_cell = cell
            break

    assert hidden_cell is not None
    assert "hide" in hidden_cell.metadata.get("tags", [])

    # Find the public cell
    public_cell = None
    for cell in nb.cells:
        if cell.cell_type == "code" and "public" in cell.source:
            public_cell = cell
            break

    assert public_cell is not None
    assert "hide" not in public_cell.metadata.get("tags", [])


def test_export_with_frontmatter(temp_output_dir: Path) -> None:
    """Test that YAML frontmatter is exported to notebook metadata."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    # Create file with frontmatter
    input_file = temp_output_dir / "input.py"
    input_file.write_text(
        "#' ---\n"
        "#' title: Test Notebook\n"
        "#' author: Test Author\n"
        "#' ---\n"
        "#'\n"
        "#' # Content\n"
        "\n"
        "x = 1\n"
    )

    output_file = temp_output_dir / "output.ipynb"

    export_notebook(input_file, output_file)

    assert output_file.exists()

    # Read notebook
    with open(output_file) as f:
        nb = nbformat.read(f, as_version=4)

    # Check metadata
    assert "title" in nb.metadata
    assert nb.metadata["title"] == "Test Notebook"
    assert "author" in nb.metadata
    assert nb.metadata["author"] == "Test Author"


def test_export_no_outputs_by_default(temp_output_dir: Path) -> None:
    """Test that exported notebooks have no outputs by default."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    input_file = temp_output_dir / "input.py"
    input_file.write_text(
        "#' # Test\n"
        "\n"
        "print('hello')\n"
    )

    output_file = temp_output_dir / "output.ipynb"

    export_notebook(input_file, output_file, execute=False)

    assert output_file.exists()

    # Read notebook
    with open(output_file) as f:
        nb = nbformat.read(f, as_version=4)

    # Check that code cells have no outputs
    for cell in nb.cells:
        if cell.cell_type == "code":
            assert len(cell.outputs) == 0


def test_export_nonexistent_file(temp_output_dir: Path) -> None:
    """Test that exporting nonexistent file raises FileNotFoundError."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    input_file = Path("/nonexistent/file.py")
    output_file = temp_output_dir / "output.ipynb"

    with pytest.raises(FileNotFoundError):
        export_notebook(input_file, output_file)


def test_round_trip_conversion(fixtures_dir: Path, temp_output_dir: Path) -> None:
    """Test round-trip conversion: notebook → py → notebook."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    # Start with original notebook
    original_nb = fixtures_dir / "simple_notebook.ipynb"
    py_file = temp_output_dir / "converted.py"
    final_nb = temp_output_dir / "round_trip.ipynb"

    # Import notebook to Python
    import_notebook(original_nb, py_file)

    # Export Python back to notebook
    export_notebook(py_file, final_nb)

    assert final_nb.exists()

    # Read both notebooks
    with open(original_nb) as f:
        original = nbformat.read(f, as_version=4)

    with open(final_nb) as f:
        final = nbformat.read(f, as_version=4)

    # Check that structure is preserved
    assert len(original.cells) == len(final.cells)

    # Check cell types match
    for orig_cell, final_cell in zip(original.cells, final.cells, strict=False):
        assert orig_cell.cell_type == final_cell.cell_type

        # Check content is similar (may have whitespace differences)
        orig_source = orig_cell.source.strip()
        final_source = final_cell.source.strip()

        # For markdown cells converted through #' comments
        if orig_cell.cell_type == "markdown":
            assert orig_source in final_source or final_source in orig_source
        # For code cells
        elif orig_cell.cell_type == "code":
            # Normalize whitespace for comparison
            assert orig_source.replace(" ", "") == final_source.replace(" ", "")


def test_round_trip_with_metadata(
    fixtures_dir: Path, temp_output_dir: Path
) -> None:
    """Test round-trip preserves metadata."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    original_nb = fixtures_dir / "notebook_with_metadata.ipynb"
    py_file = temp_output_dir / "converted.py"
    final_nb = temp_output_dir / "round_trip.ipynb"

    # Round-trip conversion
    import_notebook(original_nb, py_file)
    export_notebook(py_file, final_nb)

    # Read notebooks
    with open(original_nb) as f:
        original = nbformat.read(f, as_version=4)

    with open(final_nb) as f:
        final = nbformat.read(f, as_version=4)

    # Check that custom metadata is preserved
    assert original.metadata.get("title") == final.metadata.get("title")
    # Note: author format might change (list → string → metadata)
    assert "author" in final.metadata


def test_import_empty_notebook(temp_output_dir: Path) -> None:
    """Test importing an empty notebook."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    # Create empty notebook
    empty_nb = temp_output_dir / "empty.ipynb"
    notebook = nbformat.v4.new_notebook()

    with open(empty_nb, "w") as f:
        nbformat.write(notebook, f)

    output_file = temp_output_dir / "empty.py"
    import_notebook(empty_nb, output_file)

    assert output_file.exists()
    # Should have minimal content (possibly just empty)
    content = output_file.read_text()
    assert len(content.strip()) == 0 or content.strip() == ""


def test_export_empty_file(temp_output_dir: Path) -> None:
    """Test exporting an empty Python file."""
    temp_output_dir.mkdir(parents=True, exist_ok=True)

    input_file = temp_output_dir / "empty.py"
    input_file.write_text("")

    output_file = temp_output_dir / "output.ipynb"
    export_notebook(input_file, output_file)

    assert output_file.exists()

    with open(output_file) as f:
        nb = nbformat.read(f, as_version=4)

    # Should have no cells or empty cells
    assert len(nb.cells) == 0 or all(
        not cell.source.strip() for cell in nb.cells
    )
