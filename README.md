# EcoTravel Agent — AAI 510 Final Project

**Team 3 | AAI 510 | University of San Diego**

An AI-powered travel assistant that helps users find **low-crowd hotel destinations**.
The agent analyzes hotel availability, local events, weather, and pricing to produce
a crowd likelihood score for each result — so you can avoid over-touristed areas.

> This repo is forked from [Brian-Covington/Eco-Agent-Development](https://github.com/Brian-Covington/Eco-Agent-Development).
> Team 3 is building on top of that foundation for our AAI 510 final project submission.

---

## What This Agent Does

- Collects user preferences (budget, weather type, drive distance, crowd tolerance)
- Searches hotels via the TripAdvisor Content API
- Pulls availability and pricing from the Amadeus sandbox API
- Scores each result 0–100 using a weighted crowd formula (lower = less crowded)
- Suggests nearby low-crowd alternatives using the GeoNames dataset
- Builds low-crowd itineraries with attraction timing tips
- Rejects off-topic queries gracefully and redirects to travel topics

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Claude (`claude-sonnet-4-6`, `claude-haiku-4-5-20251001`) via Anthropic SDK |
| Frontend | Streamlit |
| Data models | Pydantic v2 |
| Tracing | LangSmith |
| APIs | TripAdvisor, Amadeus, OpenWeatherMap, PredictHQ, GeoNames |
| Testing | pytest |
| Language | Python 3.10+ |

---

## Project Structure

```
├── src/
│   ├── agent.py                # Claude agentic loop + session memory + scope guard
│   ├── memory.py               # SessionMemory — stores preferences, filters results
│   ├── models.py               # Pydantic models (UserPreferences, HotelResult, etc.)
│   ├── tracing.py              # LangSmith traced_chat wrapper
│   ├── clients/
│   │   ├── tripadvisor.py      # Hotel search, ratings, and reviews
│   │   ├── amadeus.py          # Room availability and pricing (sandbox)
│   │   ├── weather.py          # OpenWeatherMap forecast + suitability score
│   │   ├── events.py           # PredictHQ events magnitude score
│   │   └── geonames.py         # Nearby cities from cities500.txt dataset
│   ├── scoring/
│   │   └── crowd_scorer.py     # Weighted 0–100 crowd score + reason generator
│   └── tools/
│       └── agent_tools.py      # 4 Claude tool schemas + dispatch handler
├── notebooks/
│   ├── 01_data_pipeline.ipynb      # Course deliverable 1: data pipeline
│   ├── 02_agent_definition.ipynb   # Course deliverable 2: agent definition
│   └── 03_traces_evaluation.ipynb  # Course deliverable 3: traces & LLM evaluation
├── tests/
│   ├── test_models.py
│   ├── test_memory.py
│   ├── test_crowd_scorer.py
│   ├── test_clients.py
│   └── test_agent.py
├── data/
│   └── .gitkeep                # cities500.txt downloaded here — excluded from git
├── app.py                      # Streamlit UI
├── requirements.txt
├── .env.example
└── Instructions.txt            # Detailed setup and run guide
```

---

## Quick Start

### 1. Clone and set up environment

```powershell
git clone https://github.com/AndrewBlumhardt/Eco-Agent-Development.git
cd Eco-Agent-Development
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Get API keys

| Key | Where to get it | Required? |
|---|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Yes |
| `TRIPADVISOR_API_KEY` | [tripadvisor.com/developers](https://tripadvisor.com/developers) | Yes |
| `OPENWEATHERMAP_API_KEY` | [openweathermap.org/api](https://openweathermap.org/api) | Yes |
| `AMADEUS_CLIENT_ID` + `AMADEUS_CLIENT_SECRET` | [developers.amadeus.com](https://developers.amadeus.com) | Optional |
| `PREDICTHQ_API_KEY` | [predicthq.com](https://predicthq.com) | Optional |
| `LANGCHAIN_API_KEY` | [smith.langchain.com](https://smith.langchain.com) | For tracing |

### 3. Create your `.env` file

```powershell
copy .env.example .env
# Then open .env and fill in your keys
```

### 4. Download GeoNames data

```powershell
Invoke-WebRequest -Uri "https://download.geonames.org/export/dump/cities500.zip" -OutFile "data/cities500.zip"
Expand-Archive -Path "data/cities500.zip" -DestinationPath "data/" -Force
Remove-Item "data/cities500.zip"
```

### 5. Run the Streamlit app

```powershell
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Course Deliverables

### Deliverable 1 — Data Pipeline (`notebooks/01_data_pipeline.ipynb`)

Demonstrates all 5 data sources feeding into a crowd-scored hotel results DataFrame.
Run all cells top-to-bottom; every cell must complete without error.

### Deliverable 2 — Agent Definition (`notebooks/02_agent_definition.ipynb`)

Shows the agent architecture: LLM (Claude), 4 tools, session memory, LangSmith tracing,
and 2 graceful rejection examples for off-topic queries.

### Deliverable 3 — Traces & Evaluation (`notebooks/03_traces_evaluation.ipynb`)

Generates 5 named traces in LangSmith, runs an LLM-as-judge evaluation (Haiku judge),
compares Sonnet vs. Haiku on an identical query, and produces an ROI analysis.

---

## Grading Checklist

**Data Pipeline — 21 pts**
- [ ] `01_data_pipeline.ipynb` executes without error
- [ ] Pulls from TripAdvisor, Amadeus, OpenWeatherMap, PredictHQ, and GeoNames
- [ ] Produces a crowd-scored results DataFrame

**Agent Code — 52.5 pts**
- [ ] `src/agent.py` uses Claude as LLM via Anthropic SDK
- [ ] 4 relevant tools defined in `src/tools/agent_tools.py`
- [ ] Session memory filters all results by user preferences
- [ ] `dispatch_tool` wraps all tool calls in `try/except` for error handling
- [ ] 2 graceful rejection examples in `02_agent_definition.ipynb`

**Evaluation Examples — 31.5 pts**
- [ ] 5 traces in LangSmith project `eco-travel-agent`
- [ ] Trace 5 compares Sonnet and Haiku on identical input
- [ ] LLM-as-judge scores documented
- [ ] Written commentary explains agent performance and model comparison

**Video Presentation — 105 pts** *(due June 20)*
- [ ] 10–15 minute video, all team members participate
- [ ] Technical walkthrough, evaluation examples, ROI, deployment recommendation
- [ ] Opinionated quality assessment included
- [ ] No AI usage in the video presentation

---

## Running Tests

```powershell
python -m pytest tests/ -v
```

---

## API Key Safety

Your `.env` file is listed in `.gitignore` and will never be committed to GitHub.
Only `.env.example` (with placeholder values) is tracked. Never share your real keys.
