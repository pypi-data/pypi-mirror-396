from __future__ import annotations

from enum import StrEnum
from enum import auto

from pydantic import BaseModel
from pydantic import Field


class SplitterType(StrEnum):
    """Supported strategies for splitting raw content into chunks."""

    CHARACTER = auto()
    SENTENCE = auto()
    PARAGRAPH = auto()
    SEMANTIC = auto()
    MARKDOWN = auto()


SPLITTER_DESCRIPTION = """
Chunking strategy to apply to incoming content.
- If raw file was read into JSON format by `read_engine`, will use RecursiveJsonSplitter (overlap ignored).
- For MARKDOWN type, uses MarkdownTextSplitter with awareness of headers, lists, and code blocks.
- For SEMANTIC type, uses SemanticChunker with min_chunk_size set to chunk_size.
- For other types (CHARACTER, SENTENCE, PARAGRAPH), uses RecursiveCharacterTextSplitter with different separators.
"""


class ChunkerConfig(BaseModel):
    """Configuration options that control chunk generation."""

    splitter: SplitterType = Field(
        default=SplitterType.PARAGRAPH,
        description=SPLITTER_DESCRIPTION,
    )
    chunk_size: int = Field(
        default=500,
        description="Maximum number of characters per chunk.",
    )
    chunk_overlap: int = Field(
        default=100,
        description="Number of overlapping characters between consecutive chunks.",
    )
