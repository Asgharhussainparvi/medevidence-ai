
"""Fetch selected medical sources and build a local evidence library.

This is a prototype ingestion pipeline. Review source licensing before
redistributing stored text or publishing a hosted evidence collection.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_FILE = DATA_DIR / "evidence.jsonl"

SOURCES = [
    {
        "document_id": "who-hypertension",
        "title": "Hypertension",
        "publisher": "World Health Organization",
        "url": "https://www.who.int/news-room/fact-sheets/detail/hypertension",
    },
    {
        "document_id": "who-healthy-diet",
        "title": "Healthy diet",
        "publisher": "World Health Organization",
        "url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
    },
    {
        "document_id": "who-diabetes",
        "title": "Diabetes",
        "publisher": "World Health Organization",
        "url": "https://www.who.int/news-room/fact-sheets/detail/diabetes",
    },
    {
        "document_id": "who-heat-health",
        "title": "Heat and health",
        "publisher": "World Health Organization",
        "url": (
            "https://www.who.int/en/news-room/fact-sheets/"
            "detail/climate-change-heat-and-health"
        ),
    },
]

CHUNK_WORDS = 180
CHUNK_OVERLAP_WORDS = 30

HEADERS = {
    "User-Agent": "MedEvidenceAI-EducationalPrototype/0.1"
}


def clean_text(text: str) -> str:
    """Normalize whitespace without changing the meaning of the text."""
    return re.sub(r"\s+", " ", text).strip()


def split_into_chunks(
    text: str,
    chunk_words: int = CHUNK_WORDS,
    overlap_words: int = CHUNK_OVERLAP_WORDS,
) -> list[str]:
    """Split text into overlapping word-based passages."""
    words = text.split()

    if not words:
        return []

    if chunk_words <= 0:
        raise ValueError("chunk_words must be positive")

    if overlap_words < 0 or overlap_words >= chunk_words:
        raise ValueError(
            "overlap_words must be non-negative and smaller than chunk_words"
        )

    chunks: list[str] = []
    step = chunk_words - overlap_words

    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + chunk_words])
        if chunk:
            chunks.append(chunk)

        if start + chunk_words >= len(words):
            break

    return chunks


def extract_document(html: str) -> dict[str, str]:
    """Extract the page title, publication date if available, and text."""
    soup = BeautifulSoup(html, "html.parser")

    title = ""
    if soup.title:
        title = clean_text(soup.title.get_text(" ", strip=True))

    date = ""
    for selector, attribute in [
        ('meta[property="article:modified_time"]', "content"),
        ('meta[property="article:published_time"]', "content"),
        ('meta[name="date"]', "content"),
        ("time[datetime]", "datetime"),
    ]:
        tag = soup.select_one(selector)
        if tag and tag.get(attribute):
            date = clean_text(tag[attribute])
            break

    # Prefer the main page content rather than navigation and footers.
    content = soup.find("main") or soup.find("article") or soup.body or soup

    for tag in content.select(
        "script, style, nav, footer, header, aside, form, noscript"
    ):
        tag.decompose()

    paragraphs = [
        clean_text(element.get_text(" ", strip=True))
        for element in content.find_all(["h1", "h2", "h3", "p", "li"])
    ]

    text = "\n".join(part for part in paragraphs if part)

    return {
        "title": title,
        "publication_date": date,
        "text": text,
    }


def fetch_source(
    client: httpx.Client,
    source: dict[str, str],
) -> dict[str, Any]:
    """Fetch one source and convert its content into evidence passages."""
    response = client.get(source["url"])
    response.raise_for_status()

    page = extract_document(response.text)
    if len(page["text"]) < 200:
        raise ValueError(
            f"Extracted too little text from {source['url']}; "
            "the page structure may have changed."
        )

    title = page["title"] or source["title"]
    chunks = split_into_chunks(page["text"])

    retrieved_at = datetime.now(timezone.utc).isoformat()
    records: list[dict[str, Any]] = []

    for index, chunk in enumerate(chunks, start=1):
        records.append(
            {
                "passage_id": f"{source['document_id']}-p{index:03d}",
                "document_id": source["document_id"],
                "title": title,
                "publisher": source["publisher"],
                "url": str(response.url),
                "publication_date": page["publication_date"] or None,
                "retrieved_at": retrieved_at,
                "text": chunk,
            }
        )

    return {
        "document_id": source["document_id"],
        "title": title,
        "passages": records,
    }


def ingest_sources() -> list[dict[str, Any]]:
    """Fetch configured sources and save successful passages as JSONL."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    successful: list[dict[str, Any]] = []
    failures: list[str] = []

    with httpx.Client(
        headers=HEADERS,
        follow_redirects=True,
        timeout=30.0,
    ) as client:
        for source in SOURCES:
            try:
                result = fetch_source(client, source)
                successful.append(result)
                print(
                    f"[OK] {result['title']}: "
                    f"{len(result['passages'])} passages"
                )
            except (httpx.HTTPError, ValueError) as exc:
                failures.append(source["document_id"])
                logger.warning(
                    "Could not ingest %s: %s",
                    source["document_id"],
                    exc,
                )
                print(f"[FAILED] {source['title']}: {exc}")

    all_passages = [
        passage
        for document in successful
        for passage in document["passages"]
    ]

    if all_passages:
        with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            for passage in all_passages:
                file.write(json.dumps(passage, ensure_ascii=False) + "\n")

        print(f"\nSaved {len(all_passages)} passages to {OUTPUT_FILE}")
    else:
        print("\nNo passages were saved. Check your connection and source URLs.")

    print(
        f"Documents succeeded: {len(successful)}; "
        f"documents failed: {len(failures)}"
    )

    return successful


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingest_sources()