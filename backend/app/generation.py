
"""Build focused, source-grounded health education responses."""

import re
from typing import Any


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by",
    "can", "do", "does", "for", "from", "how", "i", "in", "is",
    "it", "of", "on", "or", "the", "their", "this", "to", "what",
    "when", "which", "who", "why", "with", "you", "your",
    "about", "having", "have", "has", "that", "these", "those",
    "high", "blood", "pressure",
}

FOCUS_TERMS = {
    "risk factors": {
        "risk", "increase", "increases", "factors", "older", "age",
        "genetics", "family", "overweight", "obese", "active",
        "activity", "inactivity", "salt", "alcohol", "tobacco",
        "diabetes", "kidney", "pollution", "saturated", "fats",
        "fruits", "vegetables",
    },
    "symptoms": {
        "symptoms", "headaches", "headache", "vision", "pain",
        "blurred", "chest", "dizziness", "confusion",
    },
    "prevention": {
        "prevention", "prevent", "healthy", "diet", "salt",
        "exercise", "active", "activity", "tobacco", "weight",
    },
}


def _tokens(text: str) -> set[str]:
    """Return lowercase word tokens."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))



def _sentences(text: str) -> list[str]:
    """Extract complete sentences while preserving useful sentence openings."""
    text = re.sub(r"\s+", " ", text).strip()

    # Remove common headings when they run directly into a new section.
    text = re.sub(
        r"\b(?:Symptoms|Treatment|Prevention|Diagnosis)\s+(?=[A-Z])",
        " ",
        text,
    )

    parts = re.split(r"(?<=[.!?])\s+", text)
    cleaned = []

    for part in parts:
        sentence = part.strip()

        # Ignore very short fragments and incomplete trailing text.
        if len(sentence) < 25:
            continue
        if sentence[-1] not in ".!?":
            continue

        # Preserve "Risk factors include..." as meaningful text.
        sentence = re.sub(
            r"^Risk factors\s+(?=Modifiable risk factors)",
            "",
            sentence,
            flags=re.IGNORECASE,
        )

        cleaned.append(sentence)

    return cleaned

def _focus_for(question: str) -> tuple[str, set[str]]:
    """Identify common question intents."""
    normalized = question.lower()

    if any(term in normalized for term in (
        "risk factor", "increase the risk", "causes", "cause of"
    )):
        return "risk factors", FOCUS_TERMS["risk factors"]

    if any(term in normalized for term in (
        "symptom", "signs of", "how do i know"
    )):
        return "symptoms", FOCUS_TERMS["symptoms"]

    if any(term in normalized for term in (
        "prevent", "prevention", "reduce the risk"
    )):
        return "prevention", FOCUS_TERMS["prevention"]

    return "general", set()


def generate_answer(
    question: str,
    passages: list[dict[str, Any]],
) -> dict[str, Any]:
    """Select relevant source sentences without inventing new claims."""

    if not passages:
        return {
            "answer": (
                "I couldn't find sufficiently relevant evidence in the "
                "current source library to answer reliably."
            ),
            "status": "insufficient_evidence",
            "claims": [],
        }

    focus, focus_terms = _focus_for(question)
    question_tokens = _tokens(question) - STOP_WORDS
    candidates: list[dict[str, Any]] = []

    for passage in passages:
        text = passage.get("text", "")
        if not isinstance(text, str) or not text.strip():
            continue

        for sentence in _sentences(text):
            sentence_tokens = _tokens(sentence)
            question_overlap = len(
                question_tokens & sentence_tokens
            )
            focus_overlap = len(focus_terms & sentence_tokens)

            # Prefer sentences that match the question's intent.
            score = question_overlap + (2 * focus_overlap)

            if score > 0:
                candidates.append({
                    "text": sentence,
                    "score": score,
                    "passage": passage,
                })

    # Keep only a few useful source sentences.
    candidates.sort(key=lambda item: item["score"], reverse=True)

    selected: list[dict[str, Any]] = []
    seen_text: set[str] = set()
    seen_sources: set[str] = set()

    for candidate in candidates:
        sentence = candidate["text"]
        passage = candidate["passage"]
        passage_id = str(passage.get("passage_id", ""))

        sentence_tokens = _tokens(sentence)

        # A risk-factor question should not return treatment targets.
        if focus == "risk factors" and re.search(
            r"\b(goal is|target is|less than \d+/\d+|"
            r"blood pressure goal|blood pressure target)\b",
            sentence,
            flags=re.IGNORECASE,
        ):
            continue
        # Skip exact duplicates and sentences that repeat almost all
        # the information in a previously selected sentence.
        is_duplicate = False

        for previous in selected:
            previous_tokens = _tokens(previous["text"])
            smaller_size = min(len(sentence_tokens), len(previous_tokens))

            if smaller_size and (
                len(sentence_tokens & previous_tokens) / smaller_size >= 0.70
            ):
                is_duplicate = True
                break

        if is_duplicate:
            continue

        # Avoid flooding the answer with many passages from one source chunk.
        if passage_id in seen_sources:
            continue

        if not passage.get("url"):
            continue

        selected.append(candidate)
        seen_text.add(sentence.lower())
        seen_sources.add(passage_id)

        limit = 2 if focus == "risk factors" else 3
        if len(selected) >= limit:
            break

    if not selected:
        return {
            "answer": (
                "I couldn't find sufficiently relevant evidence in the "
                "current source library to answer reliably. Try "
                "rephrasing the question or consult a qualified "
                "healthcare professional."
            ),
            "status": "insufficient_evidence",
            "claims": [],
        }

    claims = []
    for item in selected:
        passage = item["passage"]
        claims.append({
            "text": item["text"],
            "passage_id": passage.get("passage_id", "unknown"),
            "source_url": passage["url"],
            "source_title": passage.get("title", "Untitled source"),
        })

    answer = "\n\n".join(
        f"{claim['text']} [Source: {claim['source_title']}]"
        for claim in claims
    )

    return {
        "answer": answer,
        "status": "evidence_found",
        "claims": claims,
    }
