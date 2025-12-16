import json
from pathlib import Path
from uuid import uuid4

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import MarkdownTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveJsonSplitter
from loguru import logger

from .config import ChunkerConfig
from .config import SplitterType


class DonkitChunker:
    def __init__(
        self,
        config: ChunkerConfig = ChunkerConfig(),
        embeddings: Embeddings | None = None,  # mandatory for semantic chunking
    ):
        self._config = config
        self._embeddings = embeddings
        if config.splitter == SplitterType.SEMANTIC and embeddings is None:
            raise ValueError("Embeddings are required for semantic chunking")
        self._default_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )

    @staticmethod
    def __get_file_content(file_path: str) -> str | dict:
        """
        Retrieve file content from S3.

        Args:
            file_path: Path to the file in S3

        Returns:
            Contents of the file as a string

        Raises:
            ValueError: If the file cannot be found or accessed
            Exception: For other S3 errors
        """
        with open(file_path, encoding="utf-8") as file:
            return file.read()

    def chunk_text(
        self,
        content: str | dict,
        filename: str | None = None,
    ) -> list[Document]:
        # If content is already a dict with 'content' key (parsed JSON), process page-by-page
        if isinstance(content, dict) and "content" in content:
            return self._process_json_pages(content, filename)

        # Try to parse as JSON if it's a string
        if isinstance(content, str):
            try:
                json_data = json.loads(content)
                if isinstance(json_data, dict) and "content" in json_data:
                    return self._process_json_pages(json_data, filename)
            except json.JSONDecodeError:
                pass  # Not JSON, treat as plain text

        # For plain text content, apply selected splitter
        text = content if isinstance(content, str) else json.dumps(content)
        return self._split_text_with_langchain(text, filename)

    def chunk_file(
        self,
        file_path: str,
    ) -> list[Document]:
        """
        Chunk the text from a file according to the specified parameters.

        Args:
            file_path:

        Returns:
            List of text chunks

        Raises:
            ValueError: If file content is empty or exceeds maximum allowed length
        """
        file_content: str | dict = self.__get_file_content(file_path)
        if not file_content:
            raise ValueError("File content is empty")
        filename = Path(file_path).name
        # Generate document_id for all chunks of this file
        document_id = str(uuid4())
        chunks = self.chunk_text(file_content, filename=filename)
        # Add document_id to all chunks
        for chunk in chunks:
            chunk.metadata["document_id"] = document_id
        return chunks

    def _split_text_with_langchain(
        self, text: str, filename: str | None = None
    ) -> list[Document]:
        """Split text using appropriate langchain splitter based on config."""

        # Choose splitter based on config
        match self._config.splitter:
            case SplitterType.CHARACTER:
                splitter = CharacterTextSplitter(
                    chunk_size=self._config.chunk_size,
                    chunk_overlap=self._config.chunk_overlap,
                )
            case SplitterType.SENTENCE:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self._config.chunk_size,
                    chunk_overlap=self._config.chunk_overlap,
                    separators=[". ", "! ", "? ", "\n", " ", ""],
                )
            case SplitterType.PARAGRAPH:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self._config.chunk_size,
                    chunk_overlap=self._config.chunk_overlap,
                    separators=["\n\n", "\n", ". ", " ", ""],
                )
            case SplitterType.SEMANTIC:
                splitter = SemanticChunker(
                    self._embeddings,
                    min_chunk_size=self._config.chunk_size,
                )
            case SplitterType.MARKDOWN:
                splitter = MarkdownTextSplitter(
                    chunk_size=self._config.chunk_size,
                    chunk_overlap=self._config.chunk_overlap,
                )
            case _:
                splitter = self._default_splitter

        # Split the text
        try:
            text_chunks = splitter.split_text(text)
        except Exception as e:
            logger.exception(e)
            if splitter == self._default_splitter:
                raise
            text_chunks = self._default_splitter.split_text(text)

        # Create Document objects with metadata
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            metadata = {"chunk_index": i}
            if filename:
                metadata["filename"] = filename

            doc = Document(
                page_content=chunk_text,
                metadata=metadata,
                id=str(uuid4()),
            )
            chunks.append(doc)

        return chunks

    def _process_json_pages(
        self, json_data: dict, filename: str | None = None
    ) -> list[Document]:
        """Process JSON data with page structure using langchain splitters."""
        content = json_data.get("content", [])
        if not content:
            raise ValueError("JSON data is empty or missing 'content' key")

        all_chunks = []
        json_splitter = RecursiveJsonSplitter(max_chunk_size=self._config.chunk_size)

        for page in content:
            # Handle plain string pages
            if isinstance(page, str):
                metadata = {"page_number": 0, "type": "text"}
                if filename:
                    metadata["filename"] = filename
                # For plain text, use text splitter
                chunks = self._split_text_with_langchain(page, filename)
                for chunk in chunks:
                    chunk.metadata.update(metadata)
                all_chunks.extend(chunks)
                continue

            # Extract metadata fields
            metadata = {
                "page_number": page.get("page", 0),
                "type": page.get("type", "text"),
            }
            if filename:
                metadata["filename"] = filename

            page_content = page.get("content", {})

            # If content is dict/list (structured JSON), use RecursiveJsonSplitter
            if isinstance(page_content, (dict, list)):
                json_chunks = json_splitter.split_json(
                    json_data=page_content, convert_lists=True
                )
                # Create Document objects from JSON chunks
                for json_chunk in json_chunks:
                    doc = Document(
                        page_content=json.dumps(json_chunk, ensure_ascii=False),
                        metadata=metadata.copy(),
                        id=str(uuid4()),
                    )
                    all_chunks.append(doc)
            else:
                # For plain text content, use text splitter
                text_content = str(page_content)
                chunks = self._split_text_with_langchain(text_content, filename)
                for chunk in chunks:
                    chunk.metadata.update(metadata)
                all_chunks.extend(chunks)

        # Add global chunk_index
        for i, chunk in enumerate(all_chunks):
            chunk.metadata["chunk_index"] = i

        return all_chunks
