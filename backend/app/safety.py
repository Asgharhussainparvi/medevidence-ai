
"""Initial safety checks for the MedEvidence AI prototype."""

import re


DISCLAIMER = (
    "MedEvidence AI provides general health education, not medical "
    "diagnosis or treatment. It does not replace advice from a "
    "qualified healthcare professional."
)

EMERGENCY_MESSAGE = (
    "Your message may describe a medical emergency. Contact your local "
    "emergency service or go to the nearest emergency department now. "
    "Do not delay urgent care while using this tool."
)

MEDICATION_MESSAGE = (
    "I can't recommend starting, stopping, or changing a medication "
    "or provide individualized dosing instructions. Please consult a "
    "qualified healthcare professional or pharmacist for advice "
    "specific to your situation."
)

EMERGENCY_PATTERNS = [
    r"\b(chest pain|chest pressure)\b",
    r"\b(can't breathe|cannot breathe|difficulty breathing|severe shortness of breath)\b",
    r"\b(signs of stroke|face drooping|sudden weakness|sudden trouble speaking)\b",
    r"\b(unconscious|not breathing|severe bleeding)\b",
    r"\b(overdose|took too many pills)\b",
]

PERSONAL_MEDICATION_PATTERNS = [
    r"\bshould i (start|stop|skip|increase|decrease|change)\b.{0,60}\b(medicine|medication|dose|dosage|pill|drug)\b",
    r"\bhow much (medicine|medication|insulin|drug)\b",
    r"\bwhat dose\b",
    r"\bchange my dose\b",
    r"\bcan i stop taking\b",
]


def check_safety(question: str) -> dict[str, str | bool]:
    """Return a conservative safety decision for a health question."""
    normalized = re.sub(r"\s+", " ", question.lower()).strip()

    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, normalized):
            return {
                "blocked": True,
                "category": "possible_emergency",
                "message": EMERGENCY_MESSAGE,
            }

    for pattern in PERSONAL_MEDICATION_PATTERNS:
        if re.search(pattern, normalized):
            return {
                "blocked": True,
                "category": "personalized_medication",
                "message": MEDICATION_MESSAGE,
            }

    return {
        "blocked": False,
        "category": "general",
        "message": "",
    }