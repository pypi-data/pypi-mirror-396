from dataclasses import dataclass
from textwrap import dedent
from typing import Any, get_args, override

import structlog
from llama_index.core.callbacks.schema import CBEventType, EventPayload
from llama_index.core.node_parser import CodeSplitter
from pydantic import BaseModel, Field
from tree_sitter import Node, Tree
from tree_sitter_language_pack import SupportedLanguage

logger = structlog.get_logger(__name__)

MAX_CHARS = 9000


class BaseChunk(BaseModel):
    text: str
    start_byte: int
    end_byte: int


class Loc(BaseModel):
    line: int = Field(description="The line number of the location, 1-indexed")
    column: int = Field(description="The column number of the location, 1-indexed")


class Chunk(BaseModel):
    text: str
    start_char: int
    end_char: int = Field(description="Exclusive")
    start_loc: Loc
    end_loc: Loc = Field(description="Inclusive")

    @property
    def length(self) -> int:
        return self.end_char - self.start_char

    def __repr__(self) -> str:
        trunc_len = 20
        text_sum = (
            self.text[: trunc_len - 3] + "..."
            if len(self.text) > trunc_len
            else self.text
        )
        return dedent(f"""Chunk(
            text={text_sum!r},
            start_char={self.start_char},
            end_char={self.end_char},
            start_loc={self.start_loc},
            end_loc={self.end_loc}
        )""")


def _add_char_positions(chunks: list[BaseChunk], original_text: str) -> list[Chunk]:
    """
    Post-process chunks to add character positions and location information based on
    byte positions.

    Args:
        chunks: List of chunks with byte positions
        original_text: The original text string

    Returns:
        List of chunks with both byte and character positions and location info filled
        in
    """
    # Convert original text to bytes for mapping
    text_bytes = original_text.encode("utf-8")

    # Pre-compute line starts for efficient line/column calculation
    line_starts = [0]  # Line 1 starts at position 0
    for i, char in enumerate(original_text):
        if char == "\n":
            line_starts.append(i + 1)

    def char_to_loc(char_pos: int) -> Loc:
        """Convert character position to line/column (1-indexed)"""
        # Find the line containing this character position
        line = 1
        for i in range(len(line_starts)):
            if i + 1 >= len(line_starts) or char_pos < line_starts[i + 1]:
                line = i + 1
                break

        # Column is the offset from the start of the line + 1 (1-indexed)
        column = char_pos - line_starts[line - 1] + 1

        return Loc(line=line, column=column)

    chunks_with_char_pos = []

    for chunk in chunks:
        # Convert byte positions to character positions
        start_char = len(text_bytes[: chunk.start_byte].decode("utf-8"))
        end_char = len(text_bytes[: chunk.end_byte].decode("utf-8"))

        # Convert character positions to line/column locations
        start_loc = char_to_loc(start_char)
        end_loc = char_to_loc(end_char - 1) if end_char > 0 else char_to_loc(0)

        chunk_with_char_pos = Chunk(
            text=original_text[start_char:end_char],
            start_char=start_char,
            end_char=end_char,
            start_loc=start_loc,
            end_loc=end_loc,
        )
        chunks_with_char_pos.append(chunk_with_char_pos)

    return chunks_with_char_pos


class TreeSitterChunkingError(Exception):
    pass


class BetterCodeSplitter(CodeSplitter):
    """Include location information

    Example:
        # gemini-embedding-001 has max_token 2048, which is
        # approximately 10000 characters
        max_chars=1500
        chunks = BetterCodeSplitter(
            language="python",
            max_chars=min(1500, 9000),
        ).split_text(src_code)
    """

    @override
    def _chunk_node(
        self, node: Any, text_bytes: bytes, last_end: int = 0
    ) -> list[BaseChunk]:
        new_chunks: list[BaseChunk] = []
        buffer = ""
        buffer_start = last_end

        for child in node.children:
            if child.end_byte - child.start_byte > self.max_chars:
                # Child is too big, recursively chunk the child
                if len(buffer) > 0:
                    new_chunks.append(
                        BaseChunk(
                            text=buffer,
                            start_byte=buffer_start,
                            end_byte=last_end,
                        )
                    )
                buffer = ""
                new_chunks.extend(self._chunk_node(child, text_bytes, last_end))
            elif len(buffer) + child.end_byte - child.start_byte > self.max_chars:
                # Child would overflow buffer, flush and start new buffer
                new_chunks.append(
                    BaseChunk(
                        text=buffer,
                        start_byte=buffer_start,
                        end_byte=last_end,
                    )
                )
                buffer = text_bytes[last_end : child.end_byte].decode("utf-8")
                buffer_start = last_end
            else:
                buffer += text_bytes[last_end : child.end_byte].decode("utf-8")
            last_end = child.end_byte
        if len(buffer) > 0:
            new_chunks.append(
                BaseChunk(
                    text=buffer,
                    start_byte=buffer_start,
                    end_byte=last_end,
                )
            )
        return new_chunks

    @override
    def split_text(self, text: str) -> list[Chunk]:
        with self.callback_manager.event(
            CBEventType.CHUNKING, payload={EventPayload.CHUNKS: [text]}
        ) as event:
            text_bytes = bytes(text, "utf-8")
            tree = self._parser.parse(text_bytes)

            if (
                not tree.root_node.children
                or tree.root_node.children[0].type != "ERROR"
            ):
                base_chunks = [
                    chunk
                    for chunk in self._chunk_node(tree.root_node, text_bytes)
                    if chunk.text.strip()  # Only include non-empty chunks
                ]

                # Fix the last chunk to ensure it covers the entire text
                if base_chunks and base_chunks[-1].end_byte < len(text_bytes):
                    last_chunk = base_chunks[-1]
                    # Extend the last chunk to cover remaining text
                    remaining_text = text_bytes[last_chunk.end_byte :].decode("utf-8")
                    base_chunks[-1] = BaseChunk(
                        text=last_chunk.text + remaining_text,
                        start_byte=last_chunk.start_byte,
                        end_byte=len(text_bytes),
                    )

                # Post-processing
                chunks = _add_char_positions(base_chunks, text)

                event.on_end(
                    payload={EventPayload.CHUNKS: chunks},
                )

                return chunks
            else:
                logger.error(
                    text_type=type(text),
                    text=text,
                    child_count=tree.root_node.child_count,
                    tree="\n".join(get_node_type_sexpr(tree)),
                )

                raise TreeSitterChunkingError(
                    f"Could not parse code with language {self.language}."
                )


def tree_sitter_chunk(
    src_code: str,
    src_lang: str,
    max_chars: int = MAX_CHARS,
) -> list[Chunk]:
    src_lang = src_lang.lower()
    if src_lang == "iml":
        src_lang = "ocaml"

    if src_lang not in get_args(SupportedLanguage):
        raise ValueError(f"Unsupported language: {src_lang}")

    cs = BetterCodeSplitter(language=src_lang, max_chars=max_chars)
    chunks = cs.split_text(src_code)
    return chunks


@dataclass
class Cursor:
    buffer: str
    start_char: int
    end_char: int

    @property
    def length(self):
        return self.end_char - self.start_char


def naive_chunk(text: str, max_chars: int = MAX_CHARS) -> list[Chunk]:
    """Split text into chunks by line boundaries, respecting character limits.

    This is a fallback chunking method for when tree-sitter parsing is not available
    for a given language. It preserves line boundaries as much as possible while
    ensuring no chunk exceeds the maximum character limit.

    Algorithm:
    1. Process lines sequentially, accumulating them in a buffer
    2. When adding a line would exceed max_chars:
       - Flush current buffer as a chunk (if non-empty)
       - If line fits alone: start new buffer with this line
       - If line too long: split line into multiple chunks of max_chars each
    3. When line fits exactly: flush buffer and reset
    4. When line fits: add to current buffer

    Args:
        text: The text to split into chunks
        max_chars: Maximum characters per chunk (default: MAX_CHARS = 9000)

    Returns:
        List of Chunk objects with text content, character positions, and
        line/column location information

    Example:
        >>> chunks = naive_chunk("line 1\\nline 2\\nvery long line...", max_chars=20)
        >>> len(chunks)  # Number of chunks created
        >>> chunks[0].start_loc  # First chunk's starting position
        Loc(line=1, column=1)
    """
    lines: list[str] = text.splitlines(keepends=True)
    chunks: list[Chunk] = []

    # Pre-compute line starts for efficient line/column calculation
    line_starts = [0]  # Line 1 starts at position 0
    for i, char in enumerate(text):
        if char == "\n":
            line_starts.append(i + 1)

    def char_to_loc(char_pos: int) -> Loc:
        """Convert character position to line/column (1-indexed)"""
        # Find the line containing this character position
        line = 1
        for i in range(len(line_starts)):
            if i + 1 >= len(line_starts) or char_pos < line_starts[i + 1]:
                line = i + 1
                break

        # Column is the offset from the start of the line + 1 (1-indexed)
        column = char_pos - line_starts[line - 1] + 1

        return Loc(line=line, column=column)

    def flush_buffer(cursor: Cursor) -> None:
        """Create a chunk from the current buffer and add to chunks list"""
        if cursor.buffer:
            start_loc = char_to_loc(cursor.start_char)
            end_loc = (
                char_to_loc(cursor.end_char - 1)
                if cursor.end_char > 0
                else char_to_loc(0)
            )

            chunk = Chunk(
                text=cursor.buffer,
                start_char=cursor.start_char,
                end_char=cursor.end_char,
                start_loc=start_loc,
                end_loc=end_loc,
            )
            chunks.append(chunk)

    cursor = Cursor("", 0, 0)
    current_pos = 0

    for line in lines:
        line_len = len(line)

        if cursor.length + line_len > max_chars:
            # Line would overflow current buffer
            if cursor.buffer:
                # Flush current buffer if it has content
                flush_buffer(cursor)

            if line_len <= max_chars:
                # Start new buffer with this line
                cursor = Cursor(line, current_pos, current_pos + line_len)
            else:
                # Line is too long, split it into multiple chunks
                remaining_line = line
                line_start_pos = current_pos

                while remaining_line:
                    chunk_text = remaining_line[:max_chars]
                    chunk_len = len(chunk_text)

                    start_loc = char_to_loc(line_start_pos)
                    end_loc = (
                        char_to_loc(line_start_pos + chunk_len - 1)
                        if chunk_len > 0
                        else char_to_loc(line_start_pos)
                    )

                    chunk = Chunk(
                        text=chunk_text,
                        start_char=line_start_pos,
                        end_char=line_start_pos + chunk_len,
                        start_loc=start_loc,
                        end_loc=end_loc,
                    )
                    chunks.append(chunk)

                    remaining_line = remaining_line[max_chars:]
                    line_start_pos += chunk_len

                # Reset cursor for next iteration
                cursor = Cursor("", current_pos + line_len, current_pos + line_len)

        elif cursor.length + line_len == max_chars:
            # Line fills buffer exactly
            cursor.buffer += line
            cursor.end_char = current_pos + line_len
            flush_buffer(cursor)
            cursor = Cursor("", current_pos + line_len, current_pos + line_len)

        else:
            # Line fits in current buffer
            if not cursor.buffer:
                # Starting new buffer
                cursor.start_char = current_pos
            cursor.buffer += line
            cursor.end_char = current_pos + line_len

        current_pos += line_len

    # Flush any remaining buffer
    flush_buffer(cursor)

    return chunks


def chunk_code(src_code: str, src_lang: str) -> list[Chunk]:
    """Split source code into chunks using the best available method.

    Automatically selects between tree-sitter parsing (for supported languages)
    and naive line-based chunking (for unsupported languages). This provides
    intelligent code-aware chunking when possible, with a reliable fallback.

    Supported languages for tree-sitter parsing include Python, JavaScript,
    TypeScript, Rust, Go, Java, C, C++, and others defined in SupportedLanguage.
    IML code is treated as OCaml for parsing purposes.

    Args:
        src_code: The source code text to split into chunks
        src_lang: Programming language identifier (case-insensitive)

    Returns:
        List of Chunk objects with text content, character positions, and
        precise line/column location information

    Raises:
        ValueError: If tree-sitter fails to parse supported language code

    Example:
        >>> chunks = chunk("def foo():\\n    pass\\n", "python")
        >>> chunks[0].start_loc  # Precise location info
        Loc(line=1, column=1)
    """
    src_lang = src_lang.lower()
    if src_lang == "iml":
        src_lang = "ocaml"

    if src_lang in get_args(SupportedLanguage):
        try:
            chunks = tree_sitter_chunk(src_code, src_lang)
        except TreeSitterChunkingError as e:
            logger.error(
                "tree-sitter chunking failed, falling back to naive chunking",
                error=e,
            )
            chunks = naive_chunk(src_code)
    else:
        chunks = naive_chunk(src_code)

    return chunks


def get_node_type_sexpr(
    node: Node | Tree,
    depth: int = 0,
    max_depth: int | None = None,
) -> list[str]:
    """Print node type in sexpr format.

    Include 'text' only for leaf nodes.

    Return:
        list[str]: a list of lines

    """
    if isinstance(node, Tree):
        node = node.root_node

    if max_depth is not None and depth > max_depth:
        return []

    result: list[str] = []
    indent = "  " * depth
    if node.children:
        result.append(f"{indent}{node.type}")
        for child in node.children:
            child_result = get_node_type_sexpr(child, depth + 1, max_depth)
            if child_result:  # Only extend if child_result is not empty
                result.extend(child_result)
    else:
        text = node.text.decode("utf-8") if node.text else ""
        if text.strip():  # Only print non-empty text
            result.append(f"{indent}{node.type}: '{text}'")
        else:
            result.append(f"{indent}{node.type}")
    return result
