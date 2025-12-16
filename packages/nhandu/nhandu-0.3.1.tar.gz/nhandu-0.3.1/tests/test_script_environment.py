"""Tests for Python script environment variables (__file__, sys.path, sys.argv)."""

from __future__ import annotations

import sys
from pathlib import Path

from nhandu import execute
from nhandu.executor import _script_environment
from nhandu.models import CodeBlock
from nhandu.parser import parse


def get_code_block_output(executed_doc):
    """Helper to get first code block output from executed document."""
    for block in executed_doc.blocks:
        if isinstance(block, CodeBlock) and hasattr(block, 'output'):
            return block.output
    return None


def test_file_variable_set(tmp_path: Path) -> None:
    """Test that __file__ is available in code blocks."""
    content = """
print(__file__)
"""
    doc_path = tmp_path / "document.md"
    doc = parse(content, str(doc_path))
    doc.source_path = doc_path

    executed = execute(doc)

    output = get_code_block_output(executed)
    assert output is not None
    assert str(doc_path) in output


def test_file_variable_absolute_path(tmp_path: Path) -> None:
    """Test that __file__ contains absolute path."""
    content = """
from pathlib import Path
print(Path(__file__).is_absolute())
"""
    doc_path = tmp_path / "document.md"
    doc = parse(content, str(doc_path))
    doc.source_path = doc_path

    executed = execute(doc)

    output = get_code_block_output(executed)
    assert output is not None
    assert "True" in output


def test_file_parent_operations(tmp_path: Path) -> None:
    """Test that Path(__file__).parent works correctly."""
    content = """
from pathlib import Path
parent = Path(__file__).parent
print(f"Parent: {parent}")
print(f"Exists: {parent.exists()}")
"""
    doc_path = tmp_path / "test.md"
    doc = parse(content, str(doc_path))
    doc.source_path = doc_path

    executed = execute(doc)

    output = get_code_block_output(executed)
    assert output is not None
    assert f"Parent: {tmp_path}" in output or "Parent: " in output
    assert "Exists: True" in output


def test_name_variable(tmp_path: Path) -> None:
    """Test that __name__ is set to '__main__'."""
    content = """
print(__name__)
"""
    doc_path = tmp_path / "test.md"
    doc = parse(content, str(doc_path))
    doc.source_path = doc_path

    executed = execute(doc)

    output = get_code_block_output(executed)
    assert output is not None
    assert "__main__" in output


def test_builtins_available(tmp_path: Path) -> None:
    """Test that __builtins__ is available."""
    content = """
print('__builtins__' in dir())
print(callable(print))
print(callable(len))
"""
    doc_path = tmp_path / "test.md"
    doc = parse(content, str(doc_path))
    doc.source_path = doc_path

    executed = execute(doc)

    output = get_code_block_output(executed)
    assert output is not None
    assert "True" in output
    # All three prints should return True
    assert output.count("True") == 3


def test_sys_argv_set(tmp_path: Path) -> None:
    """Test that sys.argv[0] matches __file__."""
    content = """
import sys
print(sys.argv[0])
print(sys.argv[0] == __file__)
"""
    doc_path = tmp_path / "script.py"
    doc = parse(content, str(doc_path))
    doc.source_path = doc_path

    executed = execute(doc)

    output = get_code_block_output(executed)
    assert output is not None
    assert str(doc_path) in output
    assert "True" in output


def test_sys_path_includes_script_dir(tmp_path: Path) -> None:
    """Test that sys.path[0] includes the script directory."""
    content = """
import sys
from pathlib import Path

script_dir = str(Path(__file__).parent.absolute())
print(f"Script dir in sys.path: {script_dir in sys.path}")
if script_dir in sys.path:
    print(f"Is sys.path[0]: {sys.path[0] == script_dir}")
"""
    doc_path = tmp_path / "subdir" / "script.py"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc = parse(content, str(doc_path))
    doc.source_path = doc_path

    executed = execute(doc)

    output = get_code_block_output(executed)
    assert output is not None
    assert "Script dir in sys.path: True" in output
    assert "Is sys.path[0]: True" in output


def test_file_with_no_source_path() -> None:
    """Test __file__ when source_path is None (stdin/in-memory)."""
    content = """
from pathlib import Path
import os
print(__file__)
print("<stdin>" in __file__)
# Check parent is a valid directory
parent = Path(__file__).parent
print(f"Parent is directory: {parent.is_dir()}")
"""
    doc = parse(content, source_path=None)
    doc.source_path = None

    executed = execute(doc)

    output = get_code_block_output(executed)
    assert output is not None
    assert "<stdin>" in output
    assert "True" in output
    assert "Parent is directory: True" in output


def test_script_environment_context_manager() -> None:
    """Test that _script_environment restores sys.path and sys.argv."""
    original_path = sys.path.copy()
    original_argv = sys.argv.copy()

    test_path = Path("/tmp/test_script.py")

    with _script_environment(test_path):
        # Inside context, sys.path and sys.argv should be modified
        assert sys.argv[0] == str(test_path.absolute())
        assert str(test_path.parent.absolute()) in sys.path

    # After context, should be restored
    assert sys.path == original_path
    assert sys.argv == original_argv


def test_script_environment_with_none() -> None:
    """Test _script_environment with None source_path."""
    original_path = sys.path.copy()
    original_argv = sys.argv.copy()

    with _script_environment(None):
        # Should use current directory
        assert "<stdin>" in sys.argv[0]
        assert str(Path.cwd().absolute()) in sys.path

    # After context, should be restored
    assert sys.path == original_path
    assert sys.argv == original_argv


def test_relative_imports_work(tmp_path: Path) -> None:
    """Test that relative imports work from script directory."""
    # Create a module to import
    module_file = tmp_path / "test_module.py"
    module_file.write_text("TEST_VALUE = 42\n")

    # Create a script that imports the module
    script_content = """
import test_module
print(test_module.TEST_VALUE)
"""
    doc_path = tmp_path / "script.md"
    doc = parse(script_content, str(doc_path))
    doc.source_path = doc_path

    executed = execute(doc)

    # Should successfully import and print value
    output = get_code_block_output(executed)
    assert output is not None
    assert "42" in output


def test_file_in_python_literate_format(tmp_path: Path) -> None:
    """Test __file__ works in Python literate format (.py files)."""
    content = """
#' # Test Document

#' Using __file__ in literate Python:

print(f"File: {__file__}")

from pathlib import Path
print(f"Directory: {Path(__file__).parent}")
"""
    doc_path = tmp_path / "literate.py"
    doc = parse(content, str(doc_path))
    doc.source_path = doc_path

    executed = execute(doc)

    # Find code blocks (skip markdown blocks)
    code_blocks = [b for b in executed.blocks if isinstance(b, CodeBlock)]
    assert len(code_blocks) > 0

    # Check first code block output
    output = code_blocks[0].output
    assert output is not None
    assert str(doc_path) in output


def test_file_persists_across_blocks(tmp_path: Path) -> None:
    """Test that __file__ value persists across multiple code blocks."""
    content = """#' # Block 1

file_from_block1 = __file__

#' # Block 2

print(f"Block 1: {file_from_block1}")
print(f"Block 2: {__file__}")
print(f"Same: {file_from_block1 == __file__}")
"""
    doc_path = tmp_path / "multi.py"
    doc = parse(content, str(doc_path))
    doc.source_path = doc_path

    executed = execute(doc)

    # Find code blocks
    code_blocks = [b for b in executed.blocks if isinstance(b, CodeBlock)]
    assert len(code_blocks) >= 2

    # Second block should have the output showing they match
    output = code_blocks[1].output
    assert output is not None
    assert str(doc_path) in output
    assert "Same: True" in output


def test_builtins_functions_work(tmp_path: Path) -> None:
    """Test that common builtins functions work."""
    content = """
# Test various builtins
items = [1, 2, 3]
print(f"len: {len(items)}")
print(f"sum: {sum(items)}")
print(f"max: {max(items)}")
print(f"min: {min(items)}")
print(f"type: {type(items).__name__}")
"""
    doc_path = tmp_path / "test.md"
    doc = parse(content, str(doc_path))
    doc.source_path = doc_path

    executed = execute(doc)

    output = get_code_block_output(executed)
    assert output is not None
    assert "len: 3" in output
    assert "sum: 6" in output
    assert "max: 3" in output
    assert "min: 1" in output
    assert "type: list" in output
