
from fastapi import FastAPI

app = FastAPI(
    title="MedEvidence AI",
    description=(
        "An evidence-grounded health education "
        "assistant. This API is under development."
    ),
    version="0.1.0",
)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Report whether the API process is responding."""
    return {
        "status": "ok",
        "project": "MedEvidence AI",
        "version": "0.1.0",
    }