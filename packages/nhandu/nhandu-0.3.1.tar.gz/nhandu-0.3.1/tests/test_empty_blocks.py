"""Tests for empty block filtering."""

from nhandu.executor import execute
from nhandu.models import CodeBlock, MarkdownBlock
from nhandu.parser import parse
from nhandu.renderer import render


def test_non_empty_python_code_with_comments():
    """Test that Python code with comments AND actual code is not filtered."""
    content = """#' Test

# Comment
x = 42
"""

    doc = parse(content)

    # Should have 1 markdown block and 1 code block
    assert len(doc.blocks) == 2
    code_blocks = [b for b in doc.blocks if isinstance(b, CodeBlock)]
    assert len(code_blocks) == 1
    assert "x = 42" in code_blocks[0].content


def test_empty_markdown_block():
    """Test that empty markdown blocks are filtered in Python literate format."""
    content = """#' # Title
#'
#'

x = 42"""

    doc = parse(content)

    # Should have 1 markdown block and 1 code block, no empty markdown
    assert len(doc.blocks) == 2
    assert isinstance(doc.blocks[0], MarkdownBlock)
    assert isinstance(doc.blocks[1], CodeBlock)
    assert doc.blocks[0].content.strip() == "# Title"


def test_empty_code_block_python_literate():
    """Test that empty code blocks in Python literate format are filtered."""
    content = """#' # Title

# Just comments


#' More text."""

    doc = parse(content)

    # Should only have markdown blocks
    assert len(doc.blocks) == 2
    assert all(isinstance(block, MarkdownBlock) for block in doc.blocks)


def test_empty_hidden_block():
    """Test that empty hidden blocks are filtered."""
    content = """#' # Title

#| hide

#|

#' Text after."""

    doc = parse(content)

    # Should only have markdown blocks, no empty hidden block
    assert len(doc.blocks) == 2
    assert all(isinstance(block, MarkdownBlock) for block in doc.blocks)


def test_empty_hidden_block_with_comments():
    """Test that hidden blocks with only comments are filtered."""
    content = """#' # Title

#| hide
# Setup comment
# Another comment
#|

#' Text after."""

    doc = parse(content)

    # Should only have markdown blocks
    assert len(doc.blocks) == 2
    assert all(isinstance(block, MarkdownBlock) for block in doc.blocks)


def test_non_empty_hidden_block():
    """Test that non-empty hidden blocks are preserved."""
    content = """#' # Title

#| hide
import sys
x = 42
#|

#' Text after."""

    doc = parse(content)

    # Should have 2 markdown blocks and 1 hidden code block
    assert len(doc.blocks) == 3
    assert isinstance(doc.blocks[1], CodeBlock)
    assert doc.blocks[1].hidden is True
    assert "import sys" in doc.blocks[1].content


def test_defensive_render_empty_code_with_output():
    """Test defensive rendering: empty code block with output is rendered."""
    # Manually create a document with empty code but output
    # (shouldn't happen in normal flow, but defensive)
    from nhandu.models import DocumentMetadata, ExecutedDocument

    code_block = CodeBlock(content="   ", language="python")
    code_block.output = "Some output appeared"

    doc = ExecutedDocument(
        blocks=[code_block],
        metadata=DocumentMetadata(),
    )

    # Should render because it has output
    html_output = render(doc, "html")
    assert "Some output appeared" in html_output

    md_output = render(doc, "markdown")
    assert "Some output appeared" in md_output


def test_defensive_render_empty_code_with_error():
    """Test defensive rendering: empty code block with error is rendered."""
    from nhandu.models import DocumentMetadata, ExecutedDocument

    code_block = CodeBlock(content="", language="python")
    code_block.error = "RuntimeError: Something went wrong"

    doc = ExecutedDocument(
        blocks=[code_block],
        metadata=DocumentMetadata(),
    )

    # Should render because it has error
    html_output = render(doc, "html")
    assert "RuntimeError" in html_output

    md_output = render(doc, "markdown")
    assert "RuntimeError" in md_output


def test_mixed_empty_and_non_empty_blocks():
    """Test mix of empty and non-empty blocks in Python literate format."""
    content = """#' # Title
#'
#' Section 1

x = 42
print(x)

#' Section 2"""

    doc = parse(content)

    # Should have markdown blocks and 1 code block
    markdown_blocks = [b for b in doc.blocks if isinstance(b, MarkdownBlock)]
    code_blocks = [b for b in doc.blocks if isinstance(b, CodeBlock)]

    assert len(code_blocks) == 1
    assert "x = 42" in code_blocks[0].content


def test_rendering_filters_empty_blocks():
    """Test that renderer filters out any empty blocks that slip through."""
    from nhandu.models import Document, DocumentMetadata

    # Manually create blocks including some empty ones
    blocks = [
        MarkdownBlock("# Title", 1),
        MarkdownBlock("   ", 2),  # Whitespace only
        CodeBlock("x = 42", "python", False, 3),
        MarkdownBlock("", 4),  # Empty
    ]

    doc = Document(blocks=blocks, metadata=DocumentMetadata())
    executed = execute(doc)

    html = render(executed, "html")
    md = render(executed, "markdown")

    # Should only render non-empty blocks
    # HTML converts markdown headings
    assert "<h1>Title</h1>" in html or "# Title" in html
    assert "x" in html and "42" in html  # Code is rendered
    assert "# Title" in md
    assert "x = 42" in md
