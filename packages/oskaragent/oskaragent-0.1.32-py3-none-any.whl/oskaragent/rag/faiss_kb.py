"""Utilities to build and query a lightweight FAISS knowledge base."""

# ------------------ Install Required Libraries
# pip install F:\PyWinARM64\scikit_learn-1.7.0-cp313-cp313-win_arm64.whl
# pip install openai
# pip install faiss-cpu
# pip install pypdf
# ---- pip install --index-url https://download.pytorch.org/whl/cpu torch
# ---- pip install sentence_transformers

from __future__ import annotations

import json
import re
import os
from pathlib import Path
from typing import Any, Dict, List, Sequence

import faiss
import numpy as np
from openai import OpenAI
from pypdf import PdfReader

DEFAULT_MODEL_NAME = os.getenv("EMBED_MODEL", "text-embedding-3-small")
INDEX_SUFFIX = ".index"
METADATA_SUFFIX = "_metadata.json"
ALLOWED_EXTENSIONS = {".md", ".txt", ".pdf"}
_OPENAI_CLIENT: OpenAI | None = None
MAX_CHUNK_CHARS = 2000


def _get_openai_client() -> OpenAI:
    """
    Initializes and retrieves a singleton instance of the OpenAI client. Ensures that the
    client is created with the appropriate API key and optional base URL, which are
    fetched from the environment variables. Once initialized, the same client instance
    is returned for subsequent calls.

    Returns:
        OpenAI: A singleton instance of the OpenAI client.

    Raises:
        KeyError: Raised if the required environment variable "OPENAI_API_KEY" is not set.
    """
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is None:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        if base_url:
            _OPENAI_CLIENT = OpenAI(api_key=api_key, base_url=base_url)
        else:
            _OPENAI_CLIENT = OpenAI(api_key=api_key)
    return _OPENAI_CLIENT


def _embed_with_openai(texts: Sequence[str], model_name: str) -> np.ndarray:
    """
    Embeds a sequence of texts using the OpenAI embedding model.

    This function generates dense vector representations (embeddings) for a
    sequence of texts using a specified OpenAI model. It connects to the OpenAI
    API, computes embeddings for the input texts, and returns the result as a
    NumPy array of contiguous 32-bit floating-point numbers. The function expects
    non-empty input; otherwise, it raises a `ValueError`.

    Args:
        texts (Sequence[str]): A sequence of strings to be embedded.
        model_name (str): The name of the OpenAI model to use for embedding.

    Returns:
        np.ndarray: A NumPy array containing the embeddings of the input texts.
        Each row corresponds to the embedding of a single text in the sequence.

    Raises:
        ValueError: If the input sequence of texts is empty.
    """
    if not texts:
        raise ValueError("Cannot embed an empty sequence of texts.")
    client = _get_openai_client()
    response = client.embeddings.create(
        model=model_name,
        input=list(texts),
    )
    vectors = [item.embedding for item in response.data]
    return np.ascontiguousarray(np.array(vectors, dtype="float32"))


def _resolve_source_path(source_file: str) -> Path:
    """Return a usable ``Path`` for ``source_file``.

    Args:
        source_file: Absolute or relative location provided by the caller.

    Returns:
        A resolved ``Path`` object that exists on disk.

    Raises:
        FileNotFoundError: If the file cannot be located in the expected places.
    """
    candidate = Path(source_file)
    if candidate.exists():
        return candidate

    fallback = Path("fontes") / candidate.name
    if fallback.exists():
        return fallback

    raise FileNotFoundError(f"Source file not found: {source_file}")


def _split_paragraphs(text: str) -> List[str]:
    """Split ``text`` into paragraph-sized chunks.

    Args:
        text: Raw content to split.

    Returns:
        List of paragraphs separated by blank lines.
    """
    return [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]


def _split_markdown(text: str) -> List[str]:
    """Split markdown text into chunks grouped by headers.

    Args:
        text: Markdown string containing optional headings.

    Returns:
        List of markdown sections, falling back to paragraphs when no headings
        are present.
    """
    if not re.search(r"^#{1,6}\s", text, flags=re.MULTILINE):
        return _split_paragraphs(text)

    sections = re.split(r"(?m)(?=^#{1,6}\s)", text)
    return [section.strip() for section in sections if section.strip()]


def _split_plain_text(text: str, max_chars: int) -> List[str]:
    """
    Splits a given plain text into multiple segments, each with a maximum specified
    number of characters. Ensures that no split occurs within words by finding the
    last space within the maximum character limit for each segment.

    Args:
        text: The plain text to be split.
        max_chars: The maximum number of characters allowed in each segment.

    Returns:
        List of segments, each containing a portion of the original text with a
        length less than or equal to the specified max_chars. Ensures that words are
        not cut off abruptly in the split.
    """
    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return [cleaned]

    segments: List[str] = []
    remaining = cleaned
    while len(remaining) > max_chars:
        split_idx = remaining.rfind(" ", 0, max_chars)
        if split_idx <= 0:
            split_idx = max_chars
        segment = remaining[:split_idx].strip()
        if segment:
            segments.append(segment)
        remaining = remaining[split_idx:].strip()
    if remaining:
        segments.append(remaining)
    return segments


def _ensure_chunk_size(chunks: List[str], max_chars: int) -> List[str]:
    """
    Ensures that the given chunks of text are appropriately sized, respecting the
    maximum character limit. Splits text chunks further into smaller segments if they
    exceed the specified maximum number of characters, while trying to maintain
    logical grouping of paragraphs.

    Args:
        chunks (List[str]): A list of text chunks to be processed.
        max_chars (int): The maximum number of characters allowed per chunk.

    Returns:
        List[str]: A list of text chunks, each of which respects the maximum character
            limit, with larger chunks split into smaller ones as necessary.
    """
    processed: List[str] = []
    for chunk in chunks:
        if len(chunk) <= max_chars:
            processed.append(chunk)
            continue

        paragraphs = _split_paragraphs(chunk)
        if not paragraphs:
            processed.extend(_split_plain_text(chunk, max_chars))
            continue

        current_group: List[str] = []
        current_length = 0
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            if len(paragraph) > max_chars:
                if current_group:
                    processed.append("\n\n".join(current_group))
                    current_group = []
                    current_length = 0
                processed.extend(_split_plain_text(paragraph, max_chars))
                continue

            separator = 0 if not current_group else 2
            proposed_length = current_length + separator + len(paragraph)
            if proposed_length <= max_chars:
                current_group.append(paragraph)
                current_length = proposed_length
            else:
                if current_group:
                    processed.append("\n\n".join(current_group))
                current_group = [paragraph]
                current_length = len(paragraph)

        if current_group:
            processed.append("\n\n".join(current_group))

    return processed


def _pdf_to_markdown(path: Path) -> str:
    """Convert a PDF file to a markdown-flavoured string.

    Args:
        path: Location of the PDF file on disk.

    Returns:
        Markdown text where each page is represented as a heading.

    Raises:
        ValueError: If no textual content could be extracted.
    """
    reader = PdfReader(str(path))
    content: List[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        extracted = page.extract_text() or ""
        extracted = extracted.strip()
        if not extracted:
            continue
        content.append(f"# Page {page_number}\n\n{extracted}")
    markdown_text = "\n\n".join(content).strip()
    if not markdown_text:
        raise ValueError(f"No textual content found in {path}")
    return markdown_text


def _load_chunks(path: Path) -> List[str]:
    """Split the input according to its file type.

    Args:
        path: Location of the source document.

    Returns:
        List of text chunks extracted from the source document.

    Raises:
        ValueError: If the document yields no textual content.
    """
    suffix = path.suffix.lower()
    if suffix == ".md":
        text = path.read_text(encoding="utf-8")
        chunks = _split_markdown(text)
    elif suffix == ".pdf":
        markdown_text = _pdf_to_markdown(path)
        chunks = _split_markdown(markdown_text)
    else:
        text = path.read_text(encoding="utf-8")
        chunks = _split_paragraphs(text)

    if not chunks:
        raise ValueError(f"No textual content found in {path}")

    return _ensure_chunk_size(chunks, MAX_CHUNK_CHARS)


def _embed_chunks(chunks: List[str]) -> np.ndarray:
    """Compute embeddings for the provided text chunks.

    Args:
        chunks: Ordered collection of text snippets.

    Returns:
        A contiguous ``float32`` array containing the embeddings.
    """
    return _embed_with_openai(chunks, DEFAULT_MODEL_NAME)


def _save_index(
    *,
    index: faiss.Index,
    chunks: List[str],
    output_dir: Path,
    index_name: str,
    source_path: Path,
) -> None:
    """Persist the FAISS index and the chunk metadata to disk.

    Args:
        index: FAISS index populated with embeddings.
        chunks: Source text chunks aligned with the index vectors.
        output_dir: Destination directory for the artifacts.
        index_name: Base filename (without suffix) for the artifacts.
        source_path: Original document path, stored for traceability.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    index_path = output_dir / f"{index_name}{INDEX_SUFFIX}"
    faiss.write_index(index, str(index_path))

    metadata = {
        "source": str(source_path),
        "model": DEFAULT_MODEL_NAME,
        "chunks": [{"id": idx, "text": chunk} for idx, chunk in enumerate(chunks)],
    }
    metadata_path = output_dir / f"{index_name}{METADATA_SUFFIX}"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def create_kowledgebase(source_file: str, output_folder: str, index_name: str=None) -> str:
    """Build and store a FAISS index for the provided text file.

    Args:
        source_file: File to ingest (.txt, .md, or .pdf).
        output_folder: Directory where the index and metadata will be saved.
        index_name: Index name

    Returns:
        The base index name that can be reused with ``find``.

    Raises:
        ValueError: If the file extension is not supported or no text is found.
    """
    source_path = _resolve_source_path(source_file)
    if source_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension '{source_path.suffix}'. "
            f"Allowed extensions are: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        )
    chunks = _load_chunks(source_path)

    vectors = _embed_chunks(chunks)
    dimension = vectors.shape[1]

    # https://bge-model.com/tutorial/3_Indexing/3.1.3.html
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

    if index_name is None:
        index_name = source_path.stem

    output_dir = Path(output_folder)

    _save_index(
        index=index,
        chunks=chunks,
        output_dir=output_dir,
        index_name=index_name,
        source_path=source_path,
    )

    return index_name


def find(
    query: str,
    num_of_itens: int,
    folder: str,
    index_name: str,
) -> List[Dict[str, Any]]:
    """Return the closest chunks for ``query`` using the stored FAISS index.

    Args:
        query: Natural-language string used to search the index.
        num_of_itens: Maximum number of chunks to return.
        folder: Directory that contains the stored index and metadata.
        index_name: Base filename for the stored artifacts.

    Returns:
        List of dictionaries with chunk metadata and the associated distance.

    Raises:
        ValueError: If ``num_of_itens`` is not positive or metadata is invalid.
        FileNotFoundError: If the index or metadata file is missing.
    """
    if num_of_itens <= 0:
        raise ValueError("num_of_itens must be a positive integer.")

    folder_path = Path(folder)
    index_path = folder_path / f"{index_name}{INDEX_SUFFIX}"
    metadata_path = folder_path / f"{index_name}{METADATA_SUFFIX}"

    if not index_path.exists():
        raise FileNotFoundError(f"Index file not found: {index_path}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    index = faiss.read_index(str(index_path))

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    chunks = metadata.get("chunks")
    if not isinstance(chunks, list):
        raise ValueError("Metadata file does not contain a valid 'chunks' list.")

    texts = [entry["text"] for entry in chunks if "text" in entry]
    if not texts:
        return []

    model_name = metadata.get("model", DEFAULT_MODEL_NAME)
    if not model_name.startswith("text-embedding"):
        raise ValueError(
            f"Unsupported embedding model '{model_name}'. "
            "Regenerate the index using OpenAI embeddings."
        )
    query_vector = _embed_with_openai([query], model_name)

    top_k = min(num_of_itens, len(texts), index.ntotal)
    if top_k <= 0:
        return []

    distances, indices = index.search(query_vector, top_k)

    results: List[Dict[str, Any]] = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(texts):
            continue
        results.append(
            {
                "text": texts[idx],
                "distance": float(distance),
                "chunk_id": int(idx),
            }
        )

    return results
