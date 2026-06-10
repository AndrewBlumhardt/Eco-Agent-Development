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

## Full Deployment — Recreating This App From Scratch

Follow these steps to go from zero to a running app on any Windows machine.

### Prerequisites

- Python 3.10 or higher — [python.org/downloads](https://www.python.org/downloads/)
- Git — [git-scm.com](https://git-scm.com/)
- PowerShell (built into Windows)

### Step 1 — Clone the repo

```powershell
git clone https://github.com/AndrewBlumhardt/Eco-Agent-Development.git
cd Eco-Agent-Development
```

### Step 2 — Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> If you get a script execution error, run this once as Administrator first:
> `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Step 3 — Install Python dependencies

```powershell
pip install -r requirements.txt
```

### Step 4 — Get your API keys

Sign up for free accounts at each service below:

| Service | Sign-up URL | Notes |
|---|---|---|
| Anthropic (Claude) | [console.anthropic.com](https://console.anthropic.com) | ~$5 in free credits goes a long way |
| TripAdvisor | [tripadvisor.com/developers](https://www.tripadvisor.com/developers) | Content API, 5,000 calls/month free |
| OpenWeatherMap | [openweathermap.org/api](https://openweathermap.org/api) | Free tier, key active within minutes |
| LangSmith | [smith.langchain.com](https://smith.langchain.com) | Free tier, needed for trace notebooks |
| Amadeus *(optional)* | [developers.amadeus.com](https://developers.amadeus.com) | Sandbox is free, need client ID + secret |
| PredictHQ *(optional)* | [predicthq.com](https://predicthq.com) | Free trial available |

### Step 5 — Create your `.env` file

```powershell
copy .env.example .env
```

Open `.env` in any text editor and fill in your keys:

```
ANTHROPIC_API_KEY=your-key-here
TRIPADVISOR_API_KEY=your-key-here
OPENWEATHERMAP_API_KEY=your-key-here
LANGCHAIN_API_KEY=your-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=eco-travel-agent

# Optional — leave blank if you don't have these
AMADEUS_CLIENT_ID=your-id-here
AMADEUS_CLIENT_SECRET=your-secret-here
PREDICTHQ_API_KEY=your-key-here
```

### Step 6 — Download the GeoNames dataset

Required for the "Nearby Destinations" feature. Run once:

```powershell
Invoke-WebRequest -Uri "https://download.geonames.org/export/dump/cities500.zip" -OutFile "data/cities500.zip"
Expand-Archive -Path "data/cities500.zip" -DestinationPath "data/" -Force
Remove-Item "data/cities500.zip"
```

Confirm `data/cities500.txt` now exists (~50 MB).

### Step 7 — Verify tests pass

```powershell
python -m pytest tests/ -v
```

All tests should pass without any API keys (they use mocks).

### Step 8 — Run the Streamlit app

```powershell
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

**What to expect on first load:**
1. A preference form appears — fill in budget, weather preference, drive distance, crowd tolerance
2. Click **Save Preferences**
3. Enter a destination (e.g. "Asheville, NC"), check-in and check-out dates
4. Click **Search Hotels** — results appear sorted by crowd score (lower = less crowded)
5. Use the quick-action buttons (hotel details, nearby destinations, itinerary)
6. Type follow-up questions in the chat box

### Step 9 — Run the course notebooks *(optional)*

Open VS Code or Jupyter in the project root:

```powershell
jupyter notebook
```

Run notebooks in order:
1. `notebooks/01_data_pipeline.ipynb`
2. `notebooks/02_agent_definition.ipynb`
3. `notebooks/03_traces_evaluation.ipynb`

After running notebook 03, open [smith.langchain.com](https://smith.langchain.com)
and navigate to the `eco-travel-agent` project to see your traces.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError` | Virtual environment not active — run `.\.venv\Scripts\Activate.ps1` |
| `KeyError: ANTHROPIC_API_KEY` | `.env` file missing or key name has a typo |
| `Activate.ps1 cannot be loaded` | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` as Admin |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |
| Amadeus returns empty results | Expected in sandbox — scorer uses fallback values automatically |
| `data/cities500.txt not found` | Re-run Step 6 above |

---

## Recommended Static Datasets (for EDA and vector search)

The current app uses live APIs for all data. To add a static knowledge base for
retrieval and grounding (recommended for a stronger course submission), consider:

### Hotel & Travel Reviews
| Dataset | Source | Size | Notes |
|---|---|---|---|
| [515K Hotel Reviews](https://www.kaggle.com/datasets/jiashenliu/515k-hotel-reviews-data-in-europe) | Kaggle | 515K rows | TripAdvisor-style reviews, Europe hotels, great for vector search |
| [TripAdvisor Hotel Reviews](https://www.kaggle.com/datasets/andrewmvd/trip-advisor-hotel-reviews) | Kaggle | 20K rows | Ratings + full text reviews, easy to load |
| [Hotel Recommendations](https://huggingface.co/datasets/Qdrant/dbpedia-entities-openai3-text-embedding-3-large-1536-1M) | Hugging Face | Various | Pre-embedded, plug directly into vector search |
| [Expedia Hotel Reviews](https://www.kaggle.com/datasets/dariuszzbyrad/expedia-hotel-review-english) | Kaggle | ~100K | Includes star ratings and categories |

### What to look for in a good dataset
- Text fields (reviews, descriptions, summaries) — needed for vector/semantic search
- Location data (city, country, coordinates) — enables geo filtering
- Numeric ratings — can be used as crowd proxy or quality filter
- Enough rows (>10K) to make retrieval meaningful

### How it would fit into the project
A static dataset would serve as the agent's **knowledge base**:
1. Load into a DataFrame during `01_data_pipeline.ipynb` (EDA section)
2. Embed the review text using a sentence-transformer or OpenAI embeddings
3. Store embeddings locally (FAISS) or in a cloud vector store
4. Add a `search_reviews` tool that retrieves semantically similar reviews for a destination
5. Claude uses retrieved reviews to ground its recommendations in real guest feedback

---

## API Key Safety

Your `.env` file is listed in `.gitignore` and will never be committed to GitHub.
Only `.env.example` (with placeholder values) is tracked. Never share your real keys.
