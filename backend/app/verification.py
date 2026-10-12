
"""Basic source-link checks for evidence-grounded responses."""

from typing import Any
from urllib.parse import urlparse


def verify_claims(
    claims: list[dict[str, Any]],
    passages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Check that each returned claim maps to a retrieved passage.

    This checks traceability, not medical truth or semantic entailment.
    """
    passage_by_id = {
        str(passage.get("passage_id")): passage
        for passage in passages
        if passage.get("passage_id")
    }

    results: list[dict[str, Any]] = []

    for claim in claims:
        passage_id = str(claim.get("passage_id", ""))
        passage = passage_by_id.get(passage_id)

        url = str(claim.get("source_url", ""))
        parsed_url = urlparse(url)

        valid_url = (
            parsed_url.scheme == "https"
            and bool(parsed_url.netloc)
        )

        matching_source = (
            passage is not None
            and str(passage.get("url", "")) == url
        )

        results.append(
            {
                "passage_id": passage_id,
                "traceable": bool(matching_source and valid_url),
                "status": (
                    "source_linked"
                    if matching_source and valid_url
                    else "not_verified"
                ),
                "reason": (
                    "Claim is linked to a retrieved passage and HTTPS URL. "
                    "Medical accuracy has not been independently verified."
                    if matching_source and valid_url
                    else "Could not confirm the claim's link to a retrieved source."
                ),
            }
        )

    return results
"""Basic source-link checks for evidence-grounded responses."""

from typing import Any
from urllib.parse import urlparse


def verify_claims(
    claims: list[dict[str, Any]],
    passages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Check that each returned claim maps to a retrieved passage.

    This checks traceability, not medical truth or semantic entailment.
    """
    passage_by_id = {
        str(passage.get("passage_id")): passage
        for passage in passages
        if passage.get("passage_id")
    }

    results: list[dict[str, Any]] = []

    for claim in claims:
        passage_id = str(claim.get("passage_id", ""))
        passage = passage_by_id.get(passage_id)

        url = str(claim.get("source_url", ""))
        parsed_url = urlparse(url)

        valid_url = (
            parsed_url.scheme == "https"
            and bool(parsed_url.netloc)
        )

        matching_source = (
            passage is not None
            and str(passage.get("url", "")) == url
        )

        results.append(
            {
                "passage_id": passage_id,
                "traceable": bool(matching_source and valid_url),
                "status": (
                    "source_linked"
                    if matching_source and valid_url
                    else "not_verified"
                ),
                "reason": (
                    "Claim is linked to a retrieved passage and HTTPS URL. "
                    "Medical accuracy has not been independently verified."
                    if matching_source and valid_url
                    else "Could not confirm the claim's link to a retrieved source."
                ),
            }
        )

    return results