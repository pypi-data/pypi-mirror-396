"""Tests for the executor module."""

import tempfile
from pathlib import Path

import pytest

from nhandu.executor import execute
from nhandu.parser import parse


def test_execute_basic_code():
    """Test executing basic Python code."""
    content = """x = 2 + 2
print(f"Result: {x}")
x"""

    doc = parse(content)
    executed_doc = execute(doc)

    code_block = executed_doc.blocks[0]
    assert code_block.output is not None
    assert "Result: 4" in code_block.output
    assert "4" in code_block.output  # Return value
    assert code_block.error is None


def test_execute_with_shared_namespace():
    """Test that code blocks share namespace."""
    content = """x = 42

#' Some markdown to separate code blocks

y = x * 2
print(f"y = {y}")"""

    doc = parse(content)
    executed_doc = execute(doc)

    # First block sets x
    assert executed_doc.blocks[0].output is None  # No output

    # Second block (after markdown) uses x
    code_block = executed_doc.blocks[2]
    assert "y = 84" in code_block.output


def test_execute_with_error():
    """Test error handling during execution."""
    content = """undefined_variable"""

    doc = parse(content)
    executed_doc = execute(doc)

    code_block = executed_doc.blocks[0]
    assert code_block.error is not None
    assert "NameError" in code_block.error
    assert "undefined_variable" in code_block.error


def test_execute_error_shows_line_number():
    """Test that errors show accurate source line numbers."""
    content = """#' # Header

x = 1
y = 2
undefined_var  # This should fail"""

    doc = parse(content, "test_file.py")
    executed_doc = execute(doc)

    code_block = executed_doc.blocks[1]  # The code block
    assert code_block.error is not None
    assert "NameError" in code_block.error
    # Should show the file name
    assert "test_file.py" in code_block.error
    # Should show the offending line
    assert "undefined_var" in code_block.error


def test_execute_error_multiline_block():
    """Test error in multiline code blocks contains useful info."""
    content = """x = 1
y = 2
z = 3
# This is a statement, not expression, so exec will be used
bad_call = undefined_var"""

    doc = parse(content)
    executed_doc = execute(doc)

    code_block = executed_doc.blocks[0]
    assert code_block.error is not None
    assert "NameError" in code_block.error
    # Error contains the undefined variable name
    assert "undefined_var" in code_block.error


def test_execute_error_with_accurate_line():
    """Test error shows accurate line for statement errors."""
    content = """#' Header

# First code block
x = 1

#' Middle text

# Second code block - error on first line
undefined_var"""

    doc = parse(content, "analysis.py")
    executed_doc = execute(doc)

    # Second code block (index 3: header=0, code1=1, middle=2, code2=3)
    code_blocks = [b for b in executed_doc.blocks if hasattr(b, "error") and b.error]
    assert len(code_blocks) == 1

    error_block = code_blocks[0]
    assert "NameError" in error_block.error
    # Should show the file name
    assert "analysis.py" in error_block.error
    # Should show the offending code
    assert "undefined_var" in error_block.error


def test_execute_continues_after_error():
    """Test that execution continues after an error."""
    content = """print("Before error")

#' Markdown separator

undefined_variable

#' Another separator

print("After error")"""

    doc = parse(content)
    executed_doc = execute(doc)

    # First block succeeds
    assert "Before error" in executed_doc.blocks[0].output
    assert executed_doc.blocks[0].error is None

    # Third block (index 2, after first markdown) has error
    assert executed_doc.blocks[2].error is not None

    # Fifth block (index 4, after second markdown) still executes
    assert "After error" in executed_doc.blocks[4].output
    assert executed_doc.blocks[4].error is None


def test_execute_inline_code():
    """Test executing inline code in markdown."""
    content = """#' <% x = 42 %>
#' The value is <%= x %> and double is <%= x * 2 %>."""

    doc = parse(content)
    executed_doc = execute(doc)

    markdown_block = executed_doc.blocks[0]
    assert "The value is 42" in markdown_block.content
    assert "double is 84" in markdown_block.content


def test_execute_hidden_blocks():
    """Test that hidden blocks still execute."""
    content = """#| hide
hidden_var = "secret"
#|

print(f"Hidden var: {hidden_var}")"""

    doc = parse(content)
    executed_doc = execute(doc)

    # Hidden block executes but output won't be shown in rendering
    hidden_block = executed_doc.blocks[0]
    assert hidden_block.hidden is True

    # Visible block can access variables from hidden block
    visible_block = executed_doc.blocks[1]
    assert "Hidden var: secret" in visible_block.output


@pytest.mark.skipif(
    not pytest.importorskip("matplotlib", reason="matplotlib not available"),
    reason="matplotlib not available",
)
def test_execute_with_plots():
    """Test executing code that creates matplotlib plots."""
    content = """import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2*np.pi, 10)
y = np.sin(x)

plt.figure()
plt.plot(x, y)
plt.title("Test Plot")"""

    doc = parse(content)

    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()
        try:
            # Change to temp directory for plot output
            import os

            os.chdir(tmpdir)

            executed_doc = execute(doc)

            code_block = executed_doc.blocks[0]
            assert len(code_block.figures) > 0

            # Check that figure file was created
            figure_path = code_block.figures[0]
            assert figure_path.exists()
            assert figure_path.suffix == ".png"

        finally:
            os.chdir(original_cwd)


@pytest.mark.skipif(
    not pytest.importorskip("seaborn", reason="seaborn not available"),
    reason="seaborn not available",
)
def test_execute_with_seaborn_plots():
    """Test executing code that creates seaborn plots.

    Seaborn uses matplotlib as its backend, so figures should be captured
    using the same plt.get_fignums() mechanism.
    """
    content = """import seaborn as sns
import matplotlib.pyplot as plt

# Create a simple seaborn plot
tips = sns.load_dataset("tips")
sns.scatterplot(data=tips, x="total_bill", y="tip")
plt.title("Seaborn Test Plot")"""

    doc = parse(content)

    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(tmpdir)

            executed_doc = execute(doc)

            code_block = executed_doc.blocks[0]
            # Seaborn plots should be captured just like matplotlib plots
            assert len(code_block.figures) > 0, "Seaborn plots should be captured"

            # Check that figure file was created
            figure_path = code_block.figures[0]
            assert figure_path.exists()
            assert figure_path.suffix == ".png"

        finally:
            os.chdir(original_cwd)


def test_execute_with_working_dir():
    """Test executing with a specific working directory."""
    content = """import os
print(f"Current directory: {os.getcwd()}")"""

    doc = parse(content)

    with tempfile.TemporaryDirectory() as tmpdir:
        executed_doc = execute(doc, working_dir=tmpdir)

        code_block = executed_doc.blocks[0]
        assert tmpdir in code_block.output


def test_execute_expression_vs_statement():
    """Test difference between expressions and statements."""
    content = """# Expression - should show return value
2 + 2

#' Markdown separator 1

# Statement - should not show return value
x = 2 + 2

#' Markdown separator 2

# Expression again
x"""

    doc = parse(content)
    executed_doc = execute(doc)

    # Expression shows result (block 0)
    assert "4" in executed_doc.blocks[0].output

    # Assignment doesn't show result (block 2)
    assert executed_doc.blocks[2].output is None or executed_doc.blocks[2].output == ""

    # Variable reference shows value (block 4)
    assert "4" in executed_doc.blocks[4].output


def test_execute_fixture_files():
    """Test executing all fixture files."""
    fixtures_dir = Path(__file__).parent / "fixtures"

    for fixture_file in fixtures_dir.glob("*.py"):
        if fixture_file.name == "with_plots.py":
            # Skip plots test if matplotlib not available
            pytest.importorskip("matplotlib")

        content = fixture_file.read_text()
        doc = parse(content, str(fixture_file))

        executed_doc = execute(doc)

        # Should return ExecutedDocument
        assert hasattr(executed_doc, "namespace")
        assert isinstance(executed_doc.namespace, dict)

        # Should have same number of blocks
        assert len(executed_doc.blocks) == len(doc.blocks)
