
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MAX_CHUNK_CHARS = 1200
DEFAULT_TOP_K = 4
MAX_TOP_K = 8

KNOWLEDGE_FILE = (
    Path(__file__).resolve().parents[2]
    / "knowledge"
    / "analytics_catalog.md"
)


def _split_long_text(text: str, max_chars: int) -> list[str]:
    """Split unusually long text into word-boundary chunks."""
    words = text.split()
    chunks: list[str] = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()

        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = word

    if current:
        chunks.append(current)

    return chunks


def _chunk_markdown(text: str) -> list[str]:
    """Chunk Markdown by H2 sections and paragraphs."""
    sections = re.split(r"(?=^##\s+)", text, flags=re.MULTILINE)
    chunks: list[str] = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        lines = section.splitlines()
        title = lines[0].strip() if lines else "Overview"
        prefix = f"Section: {title}\n"

        if len(section) <= MAX_CHUNK_CHARS:
            chunks.append(section)
            continue

        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", section)
            if paragraph.strip()
        ]

        current_parts: list[str] = []

        def flush() -> None:
            if current_parts:
                chunks.append(
                    prefix + "\n\n".join(current_parts)
                )
                current_parts.clear()

        for paragraph in paragraphs:
            available_chars = MAX_CHUNK_CHARS - len(prefix)

            if len(paragraph) > available_chars:
                flush()

                for piece in _split_long_text(
                    paragraph, available_chars
                ):
                    chunks.append(prefix + piece)
                continue

            candidate = "\n\n".join(current_parts + [paragraph])

            if len(candidate) <= available_chars:
                current_parts.append(paragraph)
            else:
                flush()
                current_parts.append(paragraph)

        flush()

    return chunks


@lru_cache(maxsize=1)
def _load_knowledge_base() -> tuple[
    SentenceTransformer, list[str], np.ndarray
]:
    """Load the catalog and calculate embeddings once per process."""
    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(
            f"Knowledge document not found: {KNOWLEDGE_FILE}"
        )

    text = KNOWLEDGE_FILE.read_text(encoding="utf-8")
    chunks = _chunk_markdown(text)

    if not chunks:
        raise ValueError("The knowledge document contains no chunks.")

    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(
        chunks,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return model, chunks, embeddings


def retrieve_context(
    query: str,
    top_k: int = DEFAULT_TOP_K,
) -> list[dict[str, Any]]:
    """Retrieve the most semantically relevant knowledge chunks."""
    query = query.strip()

    if not query:
        raise ValueError("The retrieval query must not be empty.")

    if len(query) > 2000:
        raise ValueError("The retrieval query is too long.")

    if not 1 <= top_k <= MAX_TOP_K:
        raise ValueError(
            f"top_k must be between 1 and {MAX_TOP_K}."
        )

    model, chunks, embeddings = _load_knowledge_base()

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )[0]

    # Both vectors are normalized, so dot product equals cosine similarity.
    scores = embeddings @ query_embedding
    ranked_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {
            "content": chunks[int(index)],
            "score": round(float(scores[index]), 4),
        }
        for index in ranked_indices
    ]
