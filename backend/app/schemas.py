
"""Request and response models for MedEvidence AI."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
        description="A general health education question.",
    )


class EvidenceSource(BaseModel):
    passage_id: str
    title: str
    publisher: str
    url: str
    excerpt: str
    relevance_score: float


class ClaimVerification(BaseModel):
    passage_id: str
    traceable: bool
    status: str
    reason: str


class AskResponse(BaseModel):
    question: str
    answer: str
    status: str
    disclaimer: str
    sources: list[EvidenceSource]
    verification: list[ClaimVerification] = Field(
        default_factory=list
    )