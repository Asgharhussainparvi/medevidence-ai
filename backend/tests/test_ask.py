
"""Automated tests for the MedEvidence AI ask endpoint."""

from fastapi.testclient import TestClient

import app.main as main

client = TestClient(main.app)


def test_ask_returns_evidence_sources(monkeypatch):
    monkeypatch.setattr(
        main,
        "search_library",
        lambda query, top_k=5: [
            {
                "passage_id": "who-hypertension-p002",
                "title": "Hypertension",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/news-room/fact-sheets/detail/hypertension",
                "text": "Risk factors include older age, inactivity and a high-salt diet.",
                "relevance_score": 0.9,
            }
        ],
    )

    response = client.post(
        "/ask",
        json={"question": "What increases high blood pressure risk?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "evidence_found"
    assert len(body["sources"]) == 1
    assert body["sources"][0]["title"] == "Hypertension"
    assert body["sources"][0]["url"].startswith("https://www.who.int/")


def test_ask_emergency_skips_retrieval(monkeypatch):
    def unexpected_search(*args, **kwargs):
        raise AssertionError("Retrieval should not run for emergencies")

    monkeypatch.setattr(main, "search_library", unexpected_search)

    response = client.post(
        "/ask",
        json={"question": "I have chest pain and difficulty breathing"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "possible_emergency"
    assert body["sources"] == []
    assert "emergency" in body["answer"].lower()


def test_ask_blocks_personalized_medication_advice(monkeypatch):
    def unexpected_search(*args, **kwargs):
        raise AssertionError("Retrieval should not run for this request")

    monkeypatch.setattr(main, "search_library", unexpected_search)

    response = client.post(
        "/ask",
        json={"question": "Should I increase my medication dose?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "personalized_medication"
    assert body["sources"] == []


def test_ask_abstains_when_no_evidence_is_found(monkeypatch):
    monkeypatch.setattr(
        main,
        "search_library",
        lambda query, top_k=5: [],
    )

    response = client.post(
        "/ask",
        json={"question": "What is the health impact of moon dust?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "insufficient_evidence"
    assert body["sources"] == []
    assert "couldn't find" in body["answer"].lower()