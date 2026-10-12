# MedEvidence AI

### Evidence-Grounded Health Education Assistant

MedEvidence AI is a health education web application designed to help users explore general health questions using retrieved passages from published health guidance. It presents source links alongside responses and includes safety checks for potential medical emergencies and personalized medication requests.

**Built for:** UnivaBio Hackathon 2026
**Project status:** Minimum Viable Product (MVP)

## The Problem

People searching for health information online may encounter unreliable advice, unsupported claims, or information without clear references. Health education tools should make their evidence sources visible and be transparent about their limitations.

## Our Solution

MedEvidence AI combines a web interface with a FastAPI backend to:

* Accept general health education questions.
* Retrieve relevant passages from a locally stored evidence library.
* Generate concise, rule-based summaries from retrieved passages.
* Display source titles, publishers, excerpts, and original links.
* Check whether generated claims are traceable to retrieved source passages.
* Apply safety rules to potential emergencies and personalized medication requests.
* Communicate when evidence is unavailable.

## Key Features

* **Evidence-grounded responses:** Answers are constructed from retrieved health guidance.
* **Source transparency:** Users can inspect and open the original source pages.
* **Safety-first handling:** Emergency and individualized medication requests trigger dedicated safety messages.
* **Traceability checks:** The application checks links between generated claims and retrieved passages.
* **Responsive interface:** A React-based interface provides question suggestions, loading feedback, answers, and source cards.

## Technology Stack

| Component          | Technology                                      |
| ------------------ | ----------------------------------------------- |
| Frontend           | React, Vite, CSS                                |
| Backend            | Python, FastAPI                                 |
| API validation     | Pydantic                                        |
| Evidence retrieval | Local passage library and token-overlap scoring |
| Answer generation  | Rule-based sentence selection                   |
| Testing            | pytest                                          |
| Evidence sources   | World Health Organization (WHO) health guidance |

## Evidence Library

The initial evidence library contains passages ingested from these WHO resources:

* [Hypertension](https://www.who.int/news-room/fact-sheets/detail/hypertension)
* [Healthy diet](https://www.who.int/news-room/fact-sheets/detail/healthy-diet)
* [Diabetes](https://www.who.int/news-room/fact-sheets/detail/diabetes)
* [Climate change, heat and health](https://www.who.int/en/news-room/fact-sheets/detail/climate-change-heat-and-health)

The passages are stored locally in `backend/data/evidence.jsonl`.

## Getting Started

### Prerequisites

* Python installed
* Node.js and npm installed
* Git (optional)

### 1. Set up the Python environment

Open PowerShell in the project root:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

If the virtual environment does not exist, create it first:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

### 2. Start the backend

In the first terminal:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive API documentation: `http://127.0.0.1:8000/docs`

Health check: `http://127.0.0.1:8000/health`

### 3. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite, usually `http://localhost:5173/`.

Keep both terminals running while using the application.

## Testing

From the project root, activate the virtual environment if necessary and run:

```powershell
python -m pytest -q backend/tests
```

The backend test suite has passed during development. Tests cover the health endpoint, evidence retrieval, question responses, emergency handling, medication safety, and behavior when evidence is unavailable.

## Safety and Limitations

MedEvidence AI is an educational prototype, not a medical device or a substitute for professional healthcare.

* It does not diagnose conditions or prescribe treatments.
* It blocks selected emergency and personalized medication requests using predefined safety patterns. These rules are not comprehensive and may miss some urgent situations.
* Retrieval currently uses token overlap rather than semantic search.
* Answer generation uses rule-based sentence selection rather than a large language model.
* Traceability checks establish source linkage; they do **not** independently establish medical accuracy, completeness, or clinical validity.
* The evidence library is limited to the sources ingested for this prototype and may not cover every health question.
* Users should consult qualified healthcare professionals for personal medical advice and contact local emergency services for emergencies.

## Future Improvements

* Expand the evidence library with additional reputable health sources.
* Introduce semantic retrieval and improved relevance evaluation.
* Add more comprehensive safety tests and clinical review workflows.
* Evaluate answer faithfulness, citation accuracy, and evidence coverage.
* Improve accessibility, multilingual support, and deployment reliability.

## Project Goal

MedEvidence AI aims to make general health education more transparent by connecting answers to inspectable sources and clearly communicating safety boundaries and system limitations.

**Evidence matters. Your wellbeing matters more.**
