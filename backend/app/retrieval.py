
"""Search the locally stored medical evidence passages."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "evidence.jsonl"


def load_passages(path: Path = DATA_FILE) -> list[dict[str, Any]]:
    """Load and validate evidence passages from JSONL."""
    if not path.exists():
        raise FileNotFoundError(
            f"Evidence file not found: {path}. "
            "Run `python -m app.ingestion` first."
        )

    passages: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                passage = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {path}"
                ) from exc

            if not isinstance(passage, dict):
                continue

            if passage.get("text") and passage.get("url"):
                passages.append(passage)

    if not passages:
        raise ValueError(f"No usable evidence passages found in {path}")

    return passages


def tokenize(text: str) -> set[str]:
    """Normalize text into searchable word tokens."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class EvidenceRetriever:
    """Rank local evidence passages by query-term overlap."""

    def __init__(self, passages: list[dict[str, Any]]) -> None:
        if not passages:
            raise ValueError("Passages cannot be empty")

        self.passages = passages

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("Search query cannot be empty")

        if top_k < 0:
            raise ValueError("top_k must be non-negative")

        if top_k == 0:
            return []

        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        results: list[dict[str, Any]] = []

        for passage in self.passages:
            searchable_text = " ".join(
                str(passage.get(field, ""))
                for field in ("title", "text")
            )
            passage_tokens = tokenize(searchable_text)

            matched_tokens = query_tokens & passage_tokens
            score = len(matched_tokens) / len(query_tokens)

            result = dict(passage)
            result["relevance_score"] = round(score, 4)
            results.append(result)

        results.sort(
            key=lambda item: item["relevance_score"],
            reverse=True,
        )

        # Do not return unrelated passages with a zero score.
        return [
            result
            for result in results[:top_k]
            if result["relevance_score"] > 0
        ]


def search_library(
    query: str,
    top_k: int = 5,
    path: Path = DATA_FILE,
) -> list[dict[str, Any]]:
    """Search the saved evidence library without making network requests."""
    passages = load_passages(path)
    retriever = EvidenceRetriever(passages)
    return retriever.search(query, top_k=top_k)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise SystemExit(
            'Usage: python -m app.retrieval "your health question"'
        )

    question = " ".join(sys.argv[1:])

    try:
        results = search_library(question, top_k=5)
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    if not results:
        print("No matching evidence passages found.")
        raise SystemExit(0)

    for rank, result in enumerate(results, start=1):
        print(f"\n{rank}. {result.get('title', 'Untitled source')}")
        print(f"   Passage ID: {result.get('passage_id', 'N/A')}")
        print(f"   Relevance: {result['relevance_score']:.4f}")
        print(f"   Publisher: {result.get('publisher', 'Unknown')}")
        print(f"   Source: {result['url']}")
        print(f"   Evidence: {result['text'][:450]}...")