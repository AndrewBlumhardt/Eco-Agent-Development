# notebooks/

Three Jupyter notebooks that are the course deliverables for AAI 510 Assignment 7.1.
Run them in order. Each builds on the previous one.

## Files

| Notebook | Deliverable | Points | What it does |
|---|---|---|---|
| `01_data_pipeline.ipynb` | Deliverable 1 | 21 pts | Pulls from all 5 data sources, combines them into a crowd-scored hotel results DataFrame |
| `02_agent_definition.ipynb` | Deliverable 2 | 52.5 pts | Defines the agent architecture, shows tool schemas, session memory, and 2 graceful rejections |
| `03_traces_evaluation.ipynb` | Deliverable 3 | 31.5 pts | Runs 5 named LangSmith traces, LLM-as-judge evaluation, Sonnet vs. Haiku comparison, ROI analysis |

## Before running

1. Make sure your `.env` file is set up with all API keys (see root [README.md](../README.md)).
2. Download `data/cities500.txt` — see [data/README.md](../data/README.md).
3. Activate your virtual environment: `.\.venv\Scripts\Activate.ps1`

## Running order

```
01_data_pipeline.ipynb   →   02_agent_definition.ipynb   →   03_traces_evaluation.ipynb
```

Each notebook adds `sys.path` to the project root so `from src.xxx import ...` works correctly.

## Notebook 01 — Data Pipeline

**Purpose:** Prove the data sources work and produce a usable crowd-scored DataFrame.

Sections:
- Source 1: TripAdvisor hotel search
- Source 2: Amadeus pricing and availability
- Source 3: OpenWeatherMap weather suitability
- Source 4: PredictHQ events magnitude
- Source 5: GeoNames nearby destinations
- Combined: Crowd-scored results DataFrame

> Note: Amadeus sandbox may return empty results for some destinations — add a comment in that cell if so, the scorer falls back gracefully.

## Notebook 02 — Agent Definition

**Purpose:** Show the agent's architecture, tools, and memory — including 2 rejections.

Sections:
- Agent initialization
- Tool definitions (4 tools, JSON schemas)
- Preference shelter — setting user preferences
- Live agent demo queries
- Graceful rejection 1 (off-topic factual question)
- Graceful rejection 2 (off-topic creative request)
- Session memory state inspection

## Notebook 03 — Traces & Evaluation

**Purpose:** Generate 5 traces in LangSmith, evaluate with an LLM judge, compare models, calculate ROI.

Sections:
- Trace 1–4: Standard agent interactions (search, details, nearby, itinerary)
- Trace 5: Identical query run against both Sonnet and Haiku
- LLM-as-judge evaluation (Haiku judge, 5 criteria scored 1–5)
- ROI analysis: monthly cost comparison Sonnet vs. Haiku
- Performance commentary (fill in manually after running)
