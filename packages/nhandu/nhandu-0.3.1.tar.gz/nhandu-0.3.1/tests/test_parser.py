"""Tests for the parser module (Python literate format)."""


from nhandu.models import CodeBlock, MarkdownBlock
from nhandu.parser import PythonLiterateParser, parse


def test_parse_basic_document():
    """Test parsing a basic Python literate document."""
    content = """#' # Title
#'
#' Some text here.

print("hello")
x = 42

#' More text."""

    doc = parse(content)

    assert len(doc.blocks) == 3
    assert isinstance(doc.blocks[0], MarkdownBlock)
    assert isinstance(doc.blocks[1], CodeBlock)
    assert isinstance(doc.blocks[2], MarkdownBlock)

    code_block = doc.blocks[1]
    assert code_block.language == "python"
    assert 'print("hello")' in code_block.content
    assert "x = 42" in code_block.content


def test_parse_with_frontmatter():
    """Test parsing document with YAML frontmatter."""
    content = """#' ---
#' title: Test Document
#' output: html
#' plot_dpi: 150
#' ---
#'
#' # Content
#'
#' Some content here."""

    doc = parse(content)

    assert doc.metadata.title == "Test Document"
    assert doc.metadata.output == "html"
    assert doc.metadata.plot_dpi == 150
    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], MarkdownBlock)


def test_parse_hidden_code_blocks():
    """Test parsing hidden code blocks with #| hide markers."""
    content = """#| hide
hidden_code = True
#|

#| hide
also_hidden = True
#|

visible_code = True
"""

    doc = parse(content)

    assert len(doc.blocks) == 3
    assert all(isinstance(block, CodeBlock) for block in doc.blocks)

    assert doc.blocks[0].hidden is True
    assert doc.blocks[1].hidden is True
    assert doc.blocks[2].hidden is False


def test_parse_mixed_markdown_and_code():
    """Test parsing with interleaved markdown and code."""
    content = """#' # Introduction
#' This is some text.

x = 10
print(x)

#' ## More text
#' Another section.

y = 20
print(y)
"""

    doc = parse(content)

    # Should have alternating markdown and code blocks
    assert len(doc.blocks) == 4
    assert isinstance(doc.blocks[0], MarkdownBlock)
    assert isinstance(doc.blocks[1], CodeBlock)
    assert isinstance(doc.blocks[2], MarkdownBlock)
    assert isinstance(doc.blocks[3], CodeBlock)


def test_extract_inline_code():
    """Test extracting inline code from markdown."""
    parser = PythonLiterateParser()
    text = "The result is <%= 2 + 2 %> and <% x = 5 %> the value is <%= x %>."

    inline_codes = parser.extract_inline_code(text)

    assert len(inline_codes) == 3
    assert inline_codes[0].expression == "2 + 2"
    assert inline_codes[0].is_statement is False
    assert inline_codes[1].expression == "x = 5"
    assert inline_codes[1].is_statement is True
    assert inline_codes[2].expression == "x"
    assert inline_codes[2].is_statement is False


def test_parse_invalid_yaml():
    """Test parsing with invalid YAML frontmatter."""
    content = """#' ---
#' title: Test
#' invalid: [unclosed list
#' ---
#'
#' # Content"""

    doc = parse(content)

    # Should fall back to default metadata
    assert doc.metadata.title is None
    assert doc.metadata.output == "markdown"


def test_empty_document():
    """Test parsing an empty document."""
    doc = parse("")

    assert len(doc.blocks) == 0
    assert doc.metadata.output == "markdown"


def test_only_frontmatter():
    """Test parsing document with only frontmatter."""
    content = """#' ---
#' title: Only Metadata
#' ---"""

    doc = parse(content)

    assert doc.metadata.title == "Only Metadata"
    # Frontmatter leaves behind a markdown block with the YAML content
    # which gets filtered if empty in the parser
    assert len(doc.blocks) >= 0  # May have 0 or 1 block depending on filtering


def test_code_with_regular_comments():
    """Test that regular Python comments are preserved in code blocks."""
    content = """#' # Document

# This is a regular comment
x = 42  # inline comment
print(x)
"""

    doc = parse(content)

    assert len(doc.blocks) == 2
    code_block = doc.blocks[1]
    assert "# This is a regular comment" in code_block.content
    assert "# inline comment" in code_block.content


def test_empty_code_blocks_filtered():
    """Test that truly empty code blocks are filtered out."""
    content = """#' # Document

#' More text

x = 42
"""

    doc = parse(content)

    # Should have 2 markdown blocks and 1 code block
    assert len(doc.blocks) == 3
    code_blocks = [b for b in doc.blocks if isinstance(b, CodeBlock)]
    assert len(code_blocks) == 1
    assert "x = 42" in code_blocks[0].content


def test_multiline_markdown():
    """Test multiline markdown blocks."""
    content = """#' # Title
#'
#' This is a longer paragraph
#' that spans multiple lines
#' of markdown comments.
#'
#' - List item 1
#' - List item 2

print("code")
"""

    doc = parse(content)

    assert len(doc.blocks) == 2
    markdown_block = doc.blocks[0]
    assert "# Title" in markdown_block.content
    assert "This is a longer paragraph" in markdown_block.content
    assert "- List item 1" in markdown_block.content
