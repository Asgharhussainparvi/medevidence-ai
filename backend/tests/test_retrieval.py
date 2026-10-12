
from app.ingestion import split_into_chunks
from app.retrieval import EvidenceRetriever


def test_chunking_preserves_all_words() -> None:
    text = " ".join(f"word{i}" for i in range(25))

    chunks = split_into_chunks(
        text,
        chunk_words=10,
        overlap_words=2,
    )

    assert len(chunks) == 3
    assert chunks[0].split()[-2:] == chunks[1].split()[:2]
    assert chunks[-1].split()[-1] == "word24"


def test_retriever_ranks_relevant_passage_first() -> None:
    passages = [
        {
            "passage_id": "diet-001",
            "document_id": "diet",
            "title": "Healthy diet",
            "publisher": "WHO",
            "url": "https://example.org/diet",
            "text": (
                "A healthy diet includes fruits, vegetables, "
                "whole grains and a variety of nutritious foods."
            ),
        },
        {
            "passage_id": "heat-001",
            "document_id": "heat",
            "title": "Heat and health",
            "publisher": "WHO",
            "url": "https://example.org/heat",
            "text": (
                "Extreme heat can cause heat exhaustion and "
                "heatstroke, which is a medical emergency."
            ),
        },
    ]

    retriever = EvidenceRetriever(passages)
    results = retriever.search("healthy diet fruits vegetables", top_k=2)

    assert results[0]["passage_id"] == "diet-001"
    assert len(results) == 1
    assert results[0]["relevance_score"] > 0

def test_retriever_rejects_empty_query() -> None:
    retriever = EvidenceRetriever(
        [
            {
                "passage_id": "test-001",
                "document_id": "test",
                "title": "Test",
                "publisher": "Test",
                "url": "https://example.org",
                "text": "General health education information.",
            }
        ]
    )

    try:
        retriever.search("   ")
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected an empty-query error")