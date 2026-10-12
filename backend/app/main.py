
"""FastAPI application for MedEvidence AI."""

from fastapi import FastAPI
import os
from app.generation import generate_answer
from app.retrieval import search_library
from app.safety import DISCLAIMER, check_safety
from app.schemas import (
    AskRequest,
    AskResponse,
    ClaimVerification,
    EvidenceSource,
)
from app.verification import verify_claims
from fastapi.middleware.cors import CORSMiddleware
frontend_origin = os.getenv("FRONTEND_ORIGIN", "").rstrip("/")
app = FastAPI(
    title="MedEvidence AI",
    description=(
        "An evidence-grounded health education assistant. "
        "Responses include source passages and traceability checks."
    ),
    version="0.1.0",
)

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if frontend_origin:
    allowed_origins.append(frontend_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Report whether the API process is responding."""
    return {
        "status": "ok",
        "project": "MedEvidence AI",
        "version": "0.1.0",
    }


@app.post("/ask", response_model=AskResponse, tags=["Health Education"])
def ask_question(request: AskRequest) -> AskResponse:
    """Apply safety checks, retrieve evidence and build a sourced response."""

    question = request.question.strip()
    safety = check_safety(question)

    # Safety checks run before evidence retrieval.
    if safety["blocked"]:
        return AskResponse(
            question=question,
            answer=str(safety["message"]),
            status=str(safety["category"]),
            disclaimer=DISCLAIMER,
            sources=[],
            verification=[],
        )

    # Retrieve local evidence.
    try:
        passages = search_library(question, top_k=5)
    except (FileNotFoundError, ValueError):
        return AskResponse(
            question=question,
            answer=(
                "I couldn't access a usable evidence library for this "
                "question. Please try again later or consult a qualified "
                "healthcare professional."
            ),
            status="evidence_unavailable",
            disclaimer=DISCLAIMER,
            sources=[],
            verification=[],
        )

    # Only use passages with both text and a source URL.
    usable_passages = [
        passage
        for passage in passages
        if passage.get("text") and passage.get("url")
    ]

    # Generate a conservative response from source excerpts.
    generated = generate_answer(question, usable_passages)

    # Check whether generated excerpts link to retrieved passages.
    verification_results = verify_claims(
        generated["claims"],
        usable_passages,
    )

    sources = [
        EvidenceSource(
            passage_id=str(passage.get("passage_id", "unknown")),
            title=str(passage.get("title", "Untitled source")),
            publisher=str(passage.get("publisher", "Unknown publisher")),
            url=str(passage["url"]),
            excerpt=str(passage["text"])[:600],
            relevance_score=float(passage.get("relevance_score", 0.0)),
        )
        for passage in usable_passages
    ]

    # Be transparent if any source-link check fails.
    failed_checks = any(
        not result["traceable"]
        for result in verification_results
    )

    status = str(generated["status"])
    answer = str(generated["answer"])

    if status == "evidence_found" and failed_checks:
        status = "not_verified"
        answer += (
            "\n\nWarning: One or more source-link checks failed. "
            "Treat this response as unverified."
        )

    return AskResponse(
        question=question,
        answer=answer,
        status=status,
        disclaimer=DISCLAIMER,
        sources=sources,
        verification=[
            ClaimVerification(**result)
            for result in verification_results
        ],
    )