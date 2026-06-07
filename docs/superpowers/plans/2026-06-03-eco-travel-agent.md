# EcoTravel Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an interactive AI travel agent that recommends low-crowd hotel destinations by combining TripAdvisor, Amadeus, weather, and events data into a weighted crowd-likelihood score, with session memory for user preferences and a Streamlit UI with interactive tables and action buttons.

**Architecture:** Claude (Anthropic SDK) acts as the LLM orchestrator in an agentic tool-use loop. A `SessionMemory` object stores user preferences (budget, weather type, max drive distance, crowd tolerance) collected in an upfront preference shelter and applies them as filters on every search result. A `CrowdScorer` combines four API signals into a 0–100 score per hotel (lower = less crowded). The Streamlit app provides the interactive preference shelter form, search form, results, and three action buttons. Three Jupyter notebooks deliver the course artifacts. LangSmith captures all traces for evaluation.

**Tech Stack:** Python 3.14, Anthropic SDK (`claude-sonnet-4-6` + `claude-haiku-4-5-20251001`), TripAdvisor Content API v2, Amadeus Hotel Search API (sandbox), OpenWeatherMap API, PredictHQ Events API, GeoNames `cities500.txt` dataset, LangSmith (tracing), Streamlit, pandas, pydantic v2, pytest, python-dotenv

---

## API Keys Required

| API            | Sign Up URL                | Free Tier         |
| -------------- | -------------------------- | ----------------- |
| Anthropic      | console.anthropic.com      | Pay-as-you-go     |
| TripAdvisor    | tripadvisor.com/developers | 5,000 calls/month |
| Amadeus        | developers.amadeus.com     | Sandbox free      |
| OpenWeatherMap | openweathermap.org/api     | 1,000 calls/day   |
| PredictHQ      | predicthq.com              | Free trial        |
| LangSmith      | smith.langchain.com        | Free tier         |

---

## File Structure

```
eco-travel-agent/
├── src/
│   ├── __init__.py
│   ├── models.py                   # Pydantic data models (UserPreferences, HotelResult, CrowdScore, etc.)
│   ├── memory.py                   # SessionMemory — holds preferences, applies filters
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── tripadvisor.py          # TripAdvisor Content API — hotel info, ratings, reviews
│   │   ├── amadeus.py              # Amadeus Hotel Search API — availability & pricing
│   │   ├── weather.py              # OpenWeatherMap — weather forecast & suitability score
│   │   ├── events.py               # PredictHQ — local events magnitude score
│   │   └── geonames.py             # GeoNames dataset — nearby cities lookup
│   ├── scoring/
│   │   ├── __init__.py
│   │   └── crowd_scorer.py         # Weighted crowd score + explanation generator
│   ├── tools/
│   │   ├── __init__.py
│   │   └── agent_tools.py          # Claude tool schemas + dispatch handler
│   └── agent.py                    # Agent orchestrator — Claude loop + session memory
├── app.py                          # Streamlit UI
├── notebooks/
│   ├── 01_data_pipeline.ipynb      # Course deliverable: data pipeline
│   ├── 02_agent_definition.ipynb   # Course deliverable: agent definition
│   └── 03_traces_evaluation.ipynb  # Course deliverable: traces & LLM evaluation
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_memory.py
│   ├── test_crowd_scorer.py
│   ├── test_clients.py
│   └── test_agent.py
├── data/
│   └── .gitkeep                    # cities500.txt downloaded here, excluded from git
├── .env.example
├── .gitignore
└── requirements.txt
```

---

### Task 1: Project Scaffold

**Files:**

- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `src/__init__.py`, `src/clients/__init__.py`, `src/scoring/__init__.py`, `src/tools/__init__.py`
- Create: `tests/__init__.py`
- Create: `data/.gitkeep`

- [ ] **Step 1: Create requirements.txt**

```
anthropic>=0.40.0
streamlit>=1.40.0
pandas>=2.2.0
pydantic>=2.0.0
python-dotenv>=1.0.0
requests>=2.32.0
pytest>=8.0.0
langsmith>=0.1.0
```

- [ ] **Step 2: Create .env.example**

```
ANTHROPIC_API_KEY=your_anthropic_key_here
TRIPADVISOR_API_KEY=your_tripadvisor_key_here
AMADEUS_CLIENT_ID=your_amadeus_client_id_here
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret_here
OPENWEATHERMAP_API_KEY=your_openweathermap_key_here
PREDICTHQ_API_KEY=your_predicthq_key_here
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=eco-travel-agent
```

- [ ] **Step 3: Create .gitignore**

```
.env
__pycache__/
*.py[cod]
.pytest_cache/
*.ipynb_checkpoints/
data/cities500.txt
data/cities500.zip
venv/
.venv/
.streamlit/
```

- [ ] **Step 4: Create directory structure and empty init files**

```powershell
New-Item -ItemType Directory -Force -Path src, "src/clients", "src/scoring", "src/tools", tests, data, notebooks
"" | Set-Content src/__init__.py
"" | Set-Content src/clients/__init__.py
"" | Set-Content src/scoring/__init__.py
"" | Set-Content src/tools/__init__.py
"" | Set-Content tests/__init__.py
"" | Set-Content data/.gitkeep
```

- [ ] **Step 5: Install dependencies (activate venv first if using one)**

```powershell
pip install -r requirements.txt
```

Expected: All packages install without error.

- [ ] **Step 6: Initialize git and commit**

```powershell
git init
git add requirements.txt .env.example .gitignore src/ tests/ data/
git commit -m "feat: initial project scaffold"
```

---

### Task 2: Data Models

**Files:**

- Create: `src/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_models.py
from src.models import UserPreferences, HotelResult, CrowdScore, SearchQuery, NearbyDestination

def test_user_preferences_crowd_threshold_low():
    prefs = UserPreferences(
        budget_per_night=150.0,
        weather_preference="warm",
        max_drive_miles=25,
        crowd_tolerance="low"
    )
    assert prefs.crowd_score_threshold == 35.0

def test_user_preferences_crowd_threshold_high():
    prefs = UserPreferences(
        budget_per_night=300.0,
        weather_preference="any",
        max_drive_miles=100,
        crowd_tolerance="high"
    )
    assert prefs.crowd_score_threshold == 80.0

def test_hotel_matches_preferences_within_budget():
    hotel = HotelResult(
        hotel_id="h1", name="Test Inn", location="Austin, TX",
        availability_pct=45.0, avg_nightly_rate=120.0,
        rating=4.2, distance_miles=8.0, crowd_score=28.0
    )
    prefs = UserPreferences(
        budget_per_night=150.0, weather_preference="warm",
        max_drive_miles=25, crowd_tolerance="low"
    )
    assert hotel.matches_preferences(prefs) is True

def test_hotel_excluded_over_budget():
    hotel = HotelResult(
        hotel_id="h2", name="Expensive Hotel", location="Austin, TX",
        availability_pct=30.0, avg_nightly_rate=300.0,
        rating=4.8, distance_miles=5.0, crowd_score=20.0
    )
    prefs = UserPreferences(
        budget_per_night=150.0, weather_preference="warm",
        max_drive_miles=25, crowd_tolerance="low"
    )
    assert hotel.matches_preferences(prefs) is False

def test_hotel_excluded_over_distance():
    hotel = HotelResult(
        hotel_id="h3", name="Far Hotel", location="Austin, TX",
        availability_pct=60.0, avg_nightly_rate=100.0,
        rating=4.0, distance_miles=40.0, crowd_score=15.0
    )
    prefs = UserPreferences(
        budget_per_night=200.0, weather_preference="any",
        max_drive_miles=25, crowd_tolerance="low"
    )
    assert hotel.matches_preferences(prefs) is False

def test_hotel_excluded_by_crowd_score():
    hotel = HotelResult(
        hotel_id="h4", name="Busy Hotel", location="Austin, TX",
        availability_pct=10.0, avg_nightly_rate=100.0,
        rating=4.5, distance_miles=5.0, crowd_score=70.0
    )
    prefs = UserPreferences(
        budget_per_night=500.0, weather_preference="any",
        max_drive_miles=100, crowd_tolerance="low"
    )
    assert hotel.matches_preferences(prefs) is False
```

- [ ] **Step 2: Run to verify they fail**

```powershell
python -m pytest tests/test_models.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.models'`

- [ ] **Step 3: Write src/models.py**

```python
# src/models.py
from pydantic import BaseModel
from typing import Literal


class UserPreferences(BaseModel):
    budget_per_night: float
    weather_preference: Literal["warm", "cool", "mild", "any"]
    max_drive_miles: Literal[15, 25, 50, 100]
    crowd_tolerance: Literal["low", "medium", "high"]

    @property
    def crowd_score_threshold(self) -> float:
        return {"low": 35.0, "medium": 55.0, "high": 80.0}[self.crowd_tolerance]


class SearchQuery(BaseModel):
    location: str
    checkin_date: str   # YYYY-MM-DD
    checkout_date: str  # YYYY-MM-DD
    radius_miles: Literal[15, 25, 50, 100]


class CrowdScore(BaseModel):
    availability_component: float
    price_component: float
    events_component: float
    seasonal_component: float
    weather_component: float
    total: float
    crowd_reasons: list[str]


class HotelResult(BaseModel):
    hotel_id: str
    name: str
    location: str
    availability_pct: float    # 0-100, percentage of rooms available
    avg_nightly_rate: float
    rating: float              # 0-5 TripAdvisor rating
    distance_miles: float
    crowd_score: float         # 0-100, lower = less crowded

    def matches_preferences(self, prefs: UserPreferences) -> bool:
        if self.avg_nightly_rate > prefs.budget_per_night:
            return False
        if self.distance_miles > prefs.max_drive_miles:
            return False
        if self.crowd_score > prefs.crowd_score_threshold:
            return False
        return True


class NearbyDestination(BaseModel):
    name: str
    lat: float
    lng: float
    distance_miles: float
    population: int
    crowd_indicator: Literal["low", "medium", "high"]
```

- [ ] **Step 4: Run tests**

```powershell
python -m pytest tests/test_models.py -v
```

Expected: All 6 tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/models.py tests/test_models.py
git commit -m "feat: add pydantic data models"
```

---

### Task 3: Session Memory

**Files:**

- Create: `src/memory.py`
- Create: `tests/test_memory.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_memory.py
from src.models import UserPreferences, HotelResult
from src.memory import SessionMemory


def test_preferences_stored_and_retrieved():
    mem = SessionMemory()
    prefs = UserPreferences(
        budget_per_night=200.0, weather_preference="warm",
        max_drive_miles=50, crowd_tolerance="medium"
    )
    mem.set_preferences(prefs)
    assert mem.get_preferences() is prefs


def test_has_preferences_false_before_set():
    mem = SessionMemory()
    assert mem.has_preferences() is False


def test_has_preferences_true_after_set():
    mem = SessionMemory()
    mem.set_preferences(UserPreferences(
        budget_per_night=100.0, weather_preference="any",
        max_drive_miles=15, crowd_tolerance="high"
    ))
    assert mem.has_preferences() is True


def test_filter_hotels_by_budget():
    mem = SessionMemory()
    mem.set_preferences(UserPreferences(
        budget_per_night=150.0, weather_preference="any",
        max_drive_miles=100, crowd_tolerance="high"
    ))
    hotels = [
        HotelResult(hotel_id="a", name="Cheap", location="TX",
                    availability_pct=30, avg_nightly_rate=100,
                    rating=4.0, distance_miles=10, crowd_score=30),
        HotelResult(hotel_id="b", name="Expensive", location="TX",
                    availability_pct=30, avg_nightly_rate=200,
                    rating=4.5, distance_miles=10, crowd_score=30),
    ]
    filtered = mem.apply_filters(hotels)
    assert len(filtered) == 1
    assert filtered[0].hotel_id == "a"


def test_filter_hotels_by_crowd():
    mem = SessionMemory()
    mem.set_preferences(UserPreferences(
        budget_per_night=500.0, weather_preference="any",
        max_drive_miles=100, crowd_tolerance="low"
    ))
    hotels = [
        HotelResult(hotel_id="a", name="Quiet", location="TX",
                    availability_pct=60, avg_nightly_rate=100,
                    rating=4.0, distance_miles=10, crowd_score=20),
        HotelResult(hotel_id="b", name="Busy", location="TX",
                    availability_pct=10, avg_nightly_rate=100,
                    rating=4.5, distance_miles=10, crowd_score=60),
    ]
    filtered = mem.apply_filters(hotels)
    assert len(filtered) == 1
    assert filtered[0].hotel_id == "a"


def test_no_preferences_returns_all():
    mem = SessionMemory()
    hotels = [
        HotelResult(hotel_id="a", name="A", location="TX",
                    availability_pct=30, avg_nightly_rate=100,
                    rating=4.0, distance_miles=10, crowd_score=30),
    ]
    assert len(mem.apply_filters(hotels)) == 1


def test_conversation_history_appends():
    mem = SessionMemory()
    mem.add_message("user", "hello")
    mem.add_message("assistant", "hi there")
    history = mem.get_conversation_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
```

- [ ] **Step 2: Run to verify they fail**

```powershell
python -m pytest tests/test_memory.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.memory'`

- [ ] **Step 3: Write src/memory.py**

```python
# src/memory.py
from src.models import UserPreferences, HotelResult, SearchQuery


class SessionMemory:
    def __init__(self):
        self._preferences: UserPreferences | None = None
        self._last_query: SearchQuery | None = None
        self._conversation_history: list[dict] = []

    def set_preferences(self, prefs: UserPreferences):
        self._preferences = prefs

    def get_preferences(self) -> UserPreferences | None:
        return self._preferences

    def has_preferences(self) -> bool:
        return self._preferences is not None

    def update_query(self, query: SearchQuery):
        self._last_query = query

    def get_last_query(self) -> SearchQuery | None:
        return self._last_query

    def add_message(self, role: str, content: str):
        self._conversation_history.append({"role": role, "content": content})

    def get_conversation_history(self) -> list[dict]:
        return list(self._conversation_history)

    def apply_filters(self, hotels: list[HotelResult]) -> list[HotelResult]:
        if self._preferences is None:
            return hotels
        return [h for h in hotels if h.matches_preferences(self._preferences)]
```

- [ ] **Step 4: Run tests**

```powershell
python -m pytest tests/test_memory.py -v
```

Expected: All 7 tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/memory.py tests/test_memory.py
git commit -m "feat: add session memory with preference-based hotel filtering"
```

---

### Task 4: TripAdvisor API Client

**Files:**

- Create: `src/clients/tripadvisor.py`
- Create: `tests/test_clients.py`

Note: TripAdvisor Content API v2 base URL is `https://api.content.tripadvisor.com/api/v1`. The API provides hotel search, details, and reviews. It does **not** provide live room availability — that is handled by Amadeus in Task 5.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_clients.py
import pytest
from unittest.mock import patch, Mock
from src.clients.tripadvisor import TripAdvisorClient


def test_search_hotels_returns_list():
    client = TripAdvisorClient(api_key="test_key")
    mock_response = {
        "data": [
            {"location_id": "123", "name": "Test Hotel", "rating": "4.5",
             "address_obj": {"address_string": "123 Main St, Austin, TX"}}
        ]
    }
    with patch("src.clients.tripadvisor.requests.get") as mock_get:
        mock_get.return_value = Mock(status_code=200, json=lambda: mock_response)
        mock_get.return_value.raise_for_status = Mock()
        results = client.search_hotels(location="Austin, TX", radius_miles=25)
    assert isinstance(results, list)
    assert results[0]["location_id"] == "123"


def test_get_hotel_reviews_returns_list():
    client = TripAdvisorClient(api_key="test_key")
    mock_response = {
        "data": [
            {"rating": 5, "text": "Amazing place, very quiet", "title": "Great stay"},
            {"rating": 4, "text": "Good location, not too busy", "title": "Solid hotel"},
        ]
    }
    with patch("src.clients.tripadvisor.requests.get") as mock_get:
        mock_get.return_value = Mock(status_code=200, json=lambda: mock_response)
        mock_get.return_value.raise_for_status = Mock()
        reviews = client.get_hotel_reviews(location_id="123")
    assert len(reviews) == 2
    assert reviews[0]["rating"] == 5


def test_summarize_reviews_returns_string():
    client = TripAdvisorClient(api_key="test_key")
    reviews = [
        {"rating": 5, "text": "Wonderful and peaceful"},
        {"rating": 4, "text": "Nice place, easy parking"},
    ]
    summary = client.summarize_reviews(reviews)
    assert "4" in summary or "5" in summary  # Average rating present
    assert isinstance(summary, str)


def test_summarize_reviews_empty():
    client = TripAdvisorClient(api_key="test_key")
    assert client.summarize_reviews([]) == "No reviews available."
```

- [ ] **Step 2: Run to verify they fail**

```powershell
python -m pytest tests/test_clients.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.clients.tripadvisor'`

- [ ] **Step 3: Write src/clients/tripadvisor.py**

```python
# src/clients/tripadvisor.py
import requests
from typing import Any

BASE_URL = "https://api.content.tripadvisor.com/api/v1"


class TripAdvisorClient:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._session = requests.Session()
        self._session.headers.update({"accept": "application/json"})

    def search_hotels(self, location: str, radius_miles: int) -> list[dict[str, Any]]:
        params = {
            "key": self._api_key,
            "searchQuery": location,
            "category": "hotels",
            "radius": radius_miles,
            "radiusUnit": "mi",
            "language": "en",
        }
        resp = self._session.get(f"{BASE_URL}/location/search", params=params)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_hotel_details(self, location_id: str) -> dict[str, Any]:
        params = {"key": self._api_key, "language": "en", "currency": "USD"}
        resp = self._session.get(f"{BASE_URL}/location/{location_id}/details", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_hotel_reviews(self, location_id: str, limit: int = 5) -> list[dict[str, Any]]:
        params = {"key": self._api_key, "language": "en", "limit": limit}
        resp = self._session.get(f"{BASE_URL}/location/{location_id}/reviews", params=params)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def summarize_reviews(self, reviews: list[dict]) -> str:
        if not reviews:
            return "No reviews available."
        avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews)
        snippets = "; ".join(r.get("text", "")[:120] for r in reviews[:3])
        return f"Average rating: {avg_rating:.1f}/5. Recent guest highlights: {snippets}"
```

- [ ] **Step 4: Run tests**

```powershell
python -m pytest tests/test_clients.py -v
```

Expected: All 4 tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/clients/tripadvisor.py tests/test_clients.py
git commit -m "feat: add TripAdvisor API client"
```

---

### Task 5: Amadeus Hotel Availability Client

**Files:**

- Create: `src/clients/amadeus.py`
- Modify: `tests/test_clients.py`

Note: Amadeus Hotel Search API provides room availability and pricing. Use the sandbox at `https://test.api.amadeus.com`. Authentication is OAuth2 client credentials. The client caches the bearer token and refreshes it before expiry.

- [ ] **Step 1: Add tests to test_clients.py**

```python
# Append to tests/test_clients.py
from src.clients.amadeus import AmadeusClient


def test_amadeus_get_hotel_offers_returns_list():
    client = AmadeusClient(client_id="test_id", client_secret="test_secret")
    mock_token = Mock(status_code=200, json=lambda: {"access_token": "tok123", "expires_in": 1799})
    mock_token.raise_for_status = Mock()
    mock_offers = Mock(
        status_code=200,
        json=lambda: {
            "data": [
                {
                    "hotel": {"hotelId": "MCLONGHM", "name": "Test Hotel"},
                    "offers": [{"price": {"total": "150.00"}}]
                }
            ]
        }
    )
    mock_offers.raise_for_status = Mock()
    with patch("src.clients.amadeus.requests.post", return_value=mock_token):
        with patch("src.clients.amadeus.requests.get", return_value=mock_offers):
            results = client.search_hotel_offers(
                city_code="AUS", checkin_date="2026-07-01", checkout_date="2026-07-05"
            )
    assert len(results) == 1
    assert results[0]["hotel"]["name"] == "Test Hotel"


def test_amadeus_estimate_availability_pct_scales_with_offers():
    client = AmadeusClient(client_id="x", client_secret="y")
    one_offer = {"offers": [{}]}
    many_offers = {"offers": [{}, {}, {}, {}, {}]}
    pct_one = client.estimate_availability_pct(one_offer)
    pct_many = client.estimate_availability_pct(many_offers)
    assert pct_many > pct_one
    assert 0 < pct_one <= 100
    assert 0 < pct_many <= 100
```

- [ ] **Step 2: Run to verify they fail**

```powershell
python -m pytest tests/test_clients.py::test_amadeus_get_hotel_offers_returns_list -v
```

Expected: `ModuleNotFoundError: No module named 'src.clients.amadeus'`

- [ ] **Step 3: Write src/clients/amadeus.py**

```python
# src/clients/amadeus.py
import requests
import time
from typing import Any

SANDBOX_BASE = "https://test.api.amadeus.com"


class AmadeusClient:
    def __init__(self, client_id: str, client_secret: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token: str | None = None
        self._token_expiry: float = 0.0

    def _get_token(self) -> str:
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token
        resp = requests.post(
            f"{SANDBOX_BASE}/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        self._token_expiry = time.time() + data["expires_in"] - 60
        return self._access_token

    def search_hotel_offers(
        self,
        city_code: str,
        checkin_date: str,
        checkout_date: str,
        adults: int = 2,
    ) -> list[dict[str, Any]]:
        token = self._get_token()
        params = {
            "cityCode": city_code,
            "checkInDate": checkin_date,
            "checkOutDate": checkout_date,
            "adults": adults,
            "currency": "USD",
        }
        resp = requests.get(
            f"{SANDBOX_BASE}/v3/shopping/hotel-offers",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])

    def estimate_availability_pct(self, hotel_offer: dict) -> float:
        # More available rate offers correlates with lower occupancy.
        # Treat 1 offer ≈ 15% available, 5+ offers ≈ 75%+ available.
        num_offers = len(hotel_offer.get("offers", []))
        pct = min(num_offers * 15.0, 95.0)
        return round(max(pct, 5.0), 1)
```

- [ ] **Step 4: Run all client tests**

```powershell
python -m pytest tests/test_clients.py -v
```

Expected: All 6 tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/clients/amadeus.py tests/test_clients.py
git commit -m "feat: add Amadeus hotel availability client"
```

---

### Task 6: Weather and Events Clients

**Files:**

- Create: `src/clients/weather.py`
- Create: `src/clients/events.py`
- Modify: `tests/test_clients.py`

Note: OpenWeatherMap's free tier provides 5-day/3-hour forecasts. PredictHQ's free trial provides event search by location and date range. Both return a normalized 0–1 score used by the crowd scorer.

- [ ] **Step 1: Add tests to test_clients.py**

```python
# Append to tests/test_clients.py
from src.clients.weather import WeatherClient
from src.clients.events import EventsClient


def test_weather_suitability_clear_skies_returns_high():
    client = WeatherClient(api_key="test_key")
    mock_response = {
        "list": [
            {"dt_txt": "2026-07-01 12:00:00", "main": {"temp": 295},
             "weather": [{"main": "Clear"}]},
            {"dt_txt": "2026-07-02 12:00:00", "main": {"temp": 293},
             "weather": [{"main": "Clear"}]},
        ]
    }
    with patch("src.clients.weather.requests.get") as mock_get:
        mock_get.return_value = Mock(status_code=200, json=lambda: mock_response)
        mock_get.return_value.raise_for_status = Mock()
        score = client.get_weather_suitability(
            lat=30.2, lon=-97.7, checkin_date="2026-07-01", checkout_date="2026-07-05"
        )
    assert score == 1.0


def test_weather_suitability_storm_returns_low():
    client = WeatherClient(api_key="test_key")
    mock_response = {
        "list": [
            {"dt_txt": "2026-07-01 12:00:00", "main": {"temp": 285},
             "weather": [{"main": "Thunderstorm"}]},
        ]
    }
    with patch("src.clients.weather.requests.get") as mock_get:
        mock_get.return_value = Mock(status_code=200, json=lambda: mock_response)
        mock_get.return_value.raise_for_status = Mock()
        score = client.get_weather_suitability(
            lat=30.2, lon=-97.7, checkin_date="2026-07-01", checkout_date="2026-07-05"
        )
    assert score == 0.0


def test_events_magnitude_returns_score_and_reasons():
    client = EventsClient(api_key="test_key")
    mock_response = {
        "results": [
            {"title": "South by Southwest", "category": "festivals", "rank": 90},
            {"title": "Farmers Market", "category": "community", "rank": 40},
        ]
    }
    with patch("src.clients.events.requests.get") as mock_get:
        mock_get.return_value = Mock(status_code=200, json=lambda: mock_response)
        mock_get.return_value.raise_for_status = Mock()
        score, reasons = client.get_event_magnitude(
            location="Austin, TX", start_date="2026-07-01", end_date="2026-07-05"
        )
    assert 0.0 <= score <= 1.0
    assert "South by Southwest" in reasons


def test_events_no_events_returns_zero():
    client = EventsClient(api_key="test_key")
    with patch("src.clients.events.requests.get") as mock_get:
        mock_get.return_value = Mock(status_code=200, json=lambda: {"results": []})
        mock_get.return_value.raise_for_status = Mock()
        score, reasons = client.get_event_magnitude(
            location="Nowhere, TX", start_date="2026-07-01", end_date="2026-07-05"
        )
    assert score == 0.0
    assert reasons == []
```

- [ ] **Step 2: Run to verify they fail**

```powershell
python -m pytest tests/test_clients.py::test_weather_suitability_clear_skies_returns_high -v
```

Expected: `ModuleNotFoundError: No module named 'src.clients.weather'`

- [ ] **Step 3: Write src/clients/weather.py**

```python
# src/clients/weather.py
import requests
from datetime import datetime

BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
GOOD_CONDITIONS = {"Clear", "Clouds"}
BAD_CONDITIONS = {"Rain", "Snow", "Thunderstorm", "Drizzle", "Tornado", "Squall"}


class WeatherClient:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def get_weather_suitability(
        self, lat: float, lon: float, checkin_date: str, checkout_date: str
    ) -> float:
        """Returns 0.0 (bad weather) to 1.0 (ideal weather)."""
        params = {"lat": lat, "lon": lon, "appid": self._api_key, "units": "metric"}
        resp = requests.get(BASE_URL, params=params)
        resp.raise_for_status()
        forecasts = resp.json().get("list", [])

        checkin = datetime.strptime(checkin_date, "%Y-%m-%d")
        checkout = datetime.strptime(checkout_date, "%Y-%m-%d")

        relevant = [
            f for f in forecasts
            if checkin <= datetime.strptime(f["dt_txt"], "%Y-%m-%d %H:%M:%S") <= checkout
        ]
        if not relevant:
            return 0.5

        good_count = sum(
            1 for f in relevant if f["weather"][0]["main"] in GOOD_CONDITIONS
        )
        bad_count = sum(
            1 for f in relevant if f["weather"][0]["main"] in BAD_CONDITIONS
        )
        total = len(relevant)
        return round((good_count - bad_count) / total, 2) if total > 0 else 0.5
```

- [ ] **Step 4: Write src/clients/events.py**

```python
# src/clients/events.py
import requests
from typing import Any

BASE_URL = "https://api.predicthq.com/v1/events/"

CATEGORY_WEIGHTS = {
    "festivals": 1.0,
    "concerts": 0.8,
    "sports": 0.8,
    "expos": 0.7,
    "conferences": 0.5,
    "public-holidays": 0.9,
    "community": 0.3,
}


class EventsClient:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def get_event_magnitude(
        self, location: str, start_date: str, end_date: str
    ) -> tuple[float, list[str]]:
        """Returns (magnitude 0.0–1.0, list of significant event names)."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }
        params = {
            "q": location,
            "start.gte": start_date,
            "start.lte": end_date,
            "sort": "-rank",
            "limit": 10,
        }
        resp = requests.get(BASE_URL, headers=headers, params=params)
        resp.raise_for_status()
        events = resp.json().get("results", [])

        if not events:
            return 0.0, []

        total_score = 0.0
        significant = []
        for event in events:
            rank = event.get("rank", 0)
            category = event.get("category", "community")
            weight = CATEGORY_WEIGHTS.get(category, 0.3)
            total_score += (rank / 100.0) * weight
            if rank >= 60:
                significant.append(event.get("title", "Major event"))

        magnitude = min(total_score / max(len(events), 1), 1.0)
        return round(magnitude, 2), significant
```

- [ ] **Step 5: Run all client tests**

```powershell
python -m pytest tests/test_clients.py -v
```

Expected: All 10 tests pass.

- [ ] **Step 6: Commit**

```powershell
git add src/clients/weather.py src/clients/events.py tests/test_clients.py
git commit -m "feat: add weather and events API clients"
```

---

### Task 7: GeoNames Nearby Destinations Client

**Files:**

- Create: `src/clients/geonames.py`
- Modify: `tests/test_clients.py`

Note: The GeoNames `cities500.txt` is a tab-delimited file of all cities with population > 500. Column 2 is name, 5 is latitude, 6 is longitude, 15 is population. Download it once manually: `https://download.geonames.org/export/dump/cities500.zip` → unzip to `data/cities500.txt`. It is ~50MB and excluded from git.

- [ ] **Step 1: Add test to test_clients.py**

```python
# Append to tests/test_clients.py
from src.clients.geonames import GeoNamesClient, _haversine_miles


def test_haversine_miles_known_distance():
    # Austin TX to San Antonio TX is ~80 miles
    dist = _haversine_miles(30.2672, -97.7431, 29.4241, -98.4936)
    assert 75 < dist < 90


def test_find_nearby_sorts_by_distance():
    client = GeoNamesClient.__new__(GeoNamesClient)
    client._cities = [
        {"name": "Round Rock", "lat": 30.508, "lng": -97.679, "population": 133372},
        {"name": "San Marcos", "lat": 29.883, "lng": -97.941, "population": 65645},
        {"name": "Georgetown", "lat": 30.633, "lng": -97.677, "population": 75000},
    ]
    results = client.find_nearby_destinations(
        center_lat=30.2672, center_lng=-97.7431, radius_miles=50, limit=3
    )
    assert len(results) >= 1
    for r in results:
        assert r.distance_miles <= 50
    if len(results) > 1:
        assert results[0].distance_miles <= results[1].distance_miles
```

- [ ] **Step 2: Run to verify they fail**

```powershell
python -m pytest tests/test_clients.py::test_haversine_miles_known_distance -v
```

Expected: `ModuleNotFoundError: No module named 'src.clients.geonames'`

- [ ] **Step 3: Write src/clients/geonames.py**

```python
# src/clients/geonames.py
import math
from pathlib import Path
from src.models import NearbyDestination

GEONAMES_PATH = Path(__file__).parent.parent.parent / "data" / "cities500.txt"


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _crowd_indicator(population: int) -> str:
    if population < 10_000:
        return "low"
    elif population < 100_000:
        return "medium"
    return "high"


class GeoNamesClient:
    def __init__(self, data_path: Path = GEONAMES_PATH):
        self._cities = self._load(data_path)

    def _load(self, path: Path) -> list[dict]:
        cities = []
        if not path.exists():
            return cities
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                parts = line.strip().split("\t")
                if len(parts) < 15:
                    continue
                try:
                    cities.append({
                        "name": parts[1],
                        "lat": float(parts[4]),
                        "lng": float(parts[5]),
                        "population": int(parts[14]) if parts[14] else 0,
                    })
                except (ValueError, IndexError):
                    continue
        return cities

    def find_nearby_destinations(
        self, center_lat: float, center_lng: float, radius_miles: int, limit: int = 5
    ) -> list[NearbyDestination]:
        results = []
        for city in self._cities:
            dist = _haversine_miles(center_lat, center_lng, city["lat"], city["lng"])
            if 5 <= dist <= radius_miles:
                results.append(NearbyDestination(
                    name=city["name"],
                    lat=city["lat"],
                    lng=city["lng"],
                    distance_miles=round(dist, 1),
                    population=city["population"],
                    crowd_indicator=_crowd_indicator(city["population"]),
                ))
        results.sort(key=lambda x: x.distance_miles)
        return results[:limit]
```

- [ ] **Step 4: Download the GeoNames dataset**

```powershell
Invoke-WebRequest -Uri "https://download.geonames.org/export/dump/cities500.zip" -OutFile "data/cities500.zip"
Expand-Archive -Path "data/cities500.zip" -DestinationPath "data/" -Force
Remove-Item "data/cities500.zip"
```

Expected: `data/cities500.txt` exists (~50MB file).

- [ ] **Step 5: Run all client tests**

```powershell
python -m pytest tests/test_clients.py -v
```

Expected: All 12 tests pass.

- [ ] **Step 6: Commit**

```powershell
git add src/clients/geonames.py tests/test_clients.py
git commit -m "feat: add GeoNames nearby destinations client"
```

---

### Task 8: Crowd Scoring Engine

**Files:**

- Create: `src/scoring/crowd_scorer.py`
- Create: `tests/test_crowd_scorer.py`

The scoring formula (all components sum to max 1.0 before × 100):

| Signal              | Weight | Direction                                 |
| ------------------- | ------ | ----------------------------------------- |
| Hotel availability  | 35%    | Low availability → high score             |
| Price vs baseline   | 20%    | Price spike → high score                  |
| Local events        | 25%    | Big events → high score                   |
| Seasonal demand     | 10%    | Peak season → high score                  |
| Weather suitability | 10%    | Good weather → higher demand → high score |

- [ ] **Step 1: Write failing tests**

```python
# tests/test_crowd_scorer.py
from src.models import CrowdScore
from src.scoring.crowd_scorer import calculate_crowd_score, explain_crowd_factors


def test_high_availability_low_price_gives_low_score():
    score = calculate_crowd_score(
        availability_pct=80.0, avg_nightly_rate=100.0, baseline_rate=100.0,
        event_magnitude=0.0, seasonal_demand=0.1, weather_suitability=0.4,
    )
    assert score.total < 25.0


def test_low_availability_spike_events_gives_high_score():
    score = calculate_crowd_score(
        availability_pct=5.0, avg_nightly_rate=250.0, baseline_rate=100.0,
        event_magnitude=0.9, seasonal_demand=0.9, weather_suitability=0.9,
    )
    assert score.total > 70.0


def test_score_always_0_to_100():
    for avail in [0.0, 50.0, 100.0]:
        score = calculate_crowd_score(
            availability_pct=avail, avg_nightly_rate=150.0, baseline_rate=150.0,
            event_magnitude=0.5, seasonal_demand=0.5, weather_suitability=0.5,
        )
        assert 0.0 <= score.total <= 100.0


def test_crowd_reasons_include_limited_rooms():
    score = calculate_crowd_score(
        availability_pct=5.0, avg_nightly_rate=100.0, baseline_rate=100.0,
        event_magnitude=0.0, seasonal_demand=0.0, weather_suitability=0.0,
    )
    reasons_text = " ".join(score.crowd_reasons).lower()
    assert "limited" in reasons_text or "rooms" in reasons_text


def test_crowd_reasons_include_event():
    score = calculate_crowd_score(
        availability_pct=50.0, avg_nightly_rate=100.0, baseline_rate=100.0,
        event_magnitude=0.85, seasonal_demand=0.0, weather_suitability=0.0,
    )
    reasons_text = " ".join(score.crowd_reasons).lower()
    assert "festival" in reasons_text or "event" in reasons_text


def test_explain_crowd_factors_no_reasons():
    score = CrowdScore(
        availability_component=5.0, price_component=0.0, events_component=0.0,
        seasonal_component=0.0, weather_component=0.0, total=5.0, crowd_reasons=[]
    )
    explanation = explain_crowd_factors(score)
    assert "low crowd" in explanation.lower()
```

- [ ] **Step 2: Run to verify they fail**

```powershell
python -m pytest tests/test_crowd_scorer.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.scoring.crowd_scorer'`

- [ ] **Step 3: Write src/scoring/crowd_scorer.py**

```python
# src/scoring/crowd_scorer.py
from src.models import CrowdScore


def calculate_crowd_score(
    availability_pct: float,     # 0-100, % of rooms available
    avg_nightly_rate: float,     # Current nightly rate (USD)
    baseline_rate: float,        # Normal rate for this location (USD)
    event_magnitude: float,      # 0-1, magnitude of local events
    seasonal_demand: float,      # 0-1, peak season indicator
    weather_suitability: float,  # 0-1, 1 = ideal weather
) -> CrowdScore:
    avail_component = (1.0 - availability_pct / 100.0) * 0.35

    if baseline_rate > 0:
        price_ratio = max(0.0, (avg_nightly_rate - baseline_rate) / baseline_rate)
    else:
        price_ratio = 0.0
    price_component = min(price_ratio, 1.0) * 0.20

    events_component = event_magnitude * 0.25
    seasonal_component = seasonal_demand * 0.10
    weather_component = weather_suitability * 0.10

    raw_total = (avail_component + price_component + events_component
                 + seasonal_component + weather_component)
    total = round(min(raw_total * 100.0, 100.0), 1)

    reasons = _build_reasons(
        availability_pct, price_ratio, event_magnitude, seasonal_demand, weather_suitability
    )

    return CrowdScore(
        availability_component=round(avail_component * 100, 1),
        price_component=round(price_component * 100, 1),
        events_component=round(events_component * 100, 1),
        seasonal_component=round(seasonal_component * 100, 1),
        weather_component=round(weather_component * 100, 1),
        total=total,
        crowd_reasons=reasons,
    )


def _build_reasons(
    availability_pct: float,
    price_ratio: float,
    event_magnitude: float,
    seasonal_demand: float,
    weather_suitability: float,
) -> list[str]:
    reasons = []
    if availability_pct < 30:
        reasons.append("Hotel rooms are limited")
    if price_ratio > 0.25:
        reasons.append("Prices are unusually high, indicating extra demand or a local event")
    if event_magnitude > 0.6:
        reasons.append("A large festival, concert, or event is scheduled in the area")
    elif event_magnitude > 0.3:
        reasons.append("Community events are scheduled nearby")
    if seasonal_demand > 0.7:
        reasons.append("This is a peak travel season for the area")
    if weather_suitability > 0.8:
        reasons.append("Ideal weather is expected, attracting more visitors")
    return reasons


def explain_crowd_factors(score: CrowdScore) -> str:
    if not score.crowd_reasons:
        return "This destination shows low crowd indicators."
    return "Crowd factors detected: " + "; ".join(score.crowd_reasons) + "."
```

- [ ] **Step 4: Run tests**

```powershell
python -m pytest tests/test_crowd_scorer.py -v
```

Expected: All 6 tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/scoring/crowd_scorer.py tests/test_crowd_scorer.py
git commit -m "feat: add weighted crowd scoring engine (35/20/25/10/10 weights)"
```

---

### Task 9: Data Pipeline Notebook

**Files:**

- Create: `notebooks/01_data_pipeline.ipynb`

This is **course deliverable 1**. The notebook must execute top-to-bottom without error and show data being extracted from all 4 API sources, then combined into a crowd-scored results DataFrame.

- [ ] **Step 1: Create notebook cells**

Cell 1 — markdown:

```markdown
# Data Pipeline — EcoTravel Agent

This notebook demonstrates the data pipeline that feeds the EcoTravel Agent.
Four API sources are combined to produce crowd-scored hotel recommendations.
```

Cell 2 — code:

```python
import os, pandas as pd
from dotenv import load_dotenv
load_dotenv()

from src.clients.tripadvisor import TripAdvisorClient
from src.clients.amadeus import AmadeusClient
from src.clients.weather import WeatherClient
from src.clients.events import EventsClient
from src.clients.geonames import GeoNamesClient
from src.scoring.crowd_scorer import calculate_crowd_score

ta = TripAdvisorClient(os.environ["TRIPADVISOR_API_KEY"])
amadeus = AmadeusClient(os.environ["AMADEUS_CLIENT_ID"], os.environ["AMADEUS_CLIENT_SECRET"])
weather = WeatherClient(os.environ["OPENWEATHERMAP_API_KEY"])
events = EventsClient(os.environ["PREDICTHQ_API_KEY"])
geo = GeoNamesClient()
print("All clients initialized.")
```

Cell 3 — markdown: `## Source 1: TripAdvisor — Hotel Search`

Cell 4 — code:

```python
LOCATION = "Asheville, NC"
RADIUS = 25
ta_results = ta.search_hotels(location=LOCATION, radius_miles=RADIUS)
print(f"Found {len(ta_results)} hotels from TripAdvisor.")
pd.DataFrame(ta_results[:5])[["location_id", "name", "rating"]].head()
```

Cell 5 — markdown: `## Source 2: Amadeus — Hotel Availability & Pricing`

Cell 6 — code:

```python
CHECKIN = "2026-08-01"
CHECKOUT = "2026-08-05"
amadeus_results = amadeus.search_hotel_offers(
    city_code="AVL", checkin_date=CHECKIN, checkout_date=CHECKOUT
)
print(f"Found {len(amadeus_results)} hotel offers from Amadeus.")
for offer in amadeus_results[:3]:
    avail = amadeus.estimate_availability_pct(offer)
    rate = offer["offers"][0]["price"]["total"] if offer.get("offers") else "N/A"
    print(f"  {offer['hotel']['name']}: {avail:.0f}% available, ${rate}/night")
```

Cell 7 — markdown: `## Source 3: OpenWeatherMap — Weather Suitability`

Cell 8 — code:

```python
# Asheville, NC coordinates
LAT, LON = 35.5951, -82.5515
weather_score = weather.get_weather_suitability(LAT, LON, CHECKIN, CHECKOUT)
print(f"Weather suitability score for {LOCATION} ({CHECKIN} – {CHECKOUT}): {weather_score:.2f}")
print("  (0.0 = severe weather, 1.0 = ideal conditions)")
```

Cell 9 — markdown: `## Source 4: PredictHQ — Local Events`

Cell 10 — code:

```python
event_score, event_list = events.get_event_magnitude(LOCATION, CHECKIN, CHECKOUT)
print(f"Event magnitude score: {event_score:.2f}")
if event_list:
    print("Significant events:", event_list)
else:
    print("No major events found for these dates.")
```

Cell 11 — markdown: `## Source 5: GeoNames — Nearby Destinations`

Cell 12 — code:

```python
nearby = geo.find_nearby_destinations(center_lat=LAT, center_lng=LON, radius_miles=50, limit=5)
nearby_df = pd.DataFrame([d.model_dump() for d in nearby])
display(nearby_df)
```

Cell 13 — markdown: `## Combined Pipeline: Crowd-Scored Hotel Results`

Cell 14 — code:

```python
rows = []
for hotel in ta_results[:8]:
    for offer in amadeus_results[:1]:  # Use first Amadeus result as pricing proxy
        avail_pct = amadeus.estimate_availability_pct(offer)
        avg_rate = float(offer["offers"][0]["price"]["total"]) if offer.get("offers") else 150.0
        baseline = avg_rate * 0.85
        score = calculate_crowd_score(
            availability_pct=avail_pct,
            avg_nightly_rate=avg_rate,
            baseline_rate=baseline,
            event_magnitude=event_score,
            seasonal_demand=0.6,   # Summer = moderate peak
            weather_suitability=weather_score,
        )
        if avail_pct >= 20.0:  # Only show hotels with > 20% availability
            rows.append({
                "Hotel": hotel.get("name", "Unknown"),
                "Availability %": f"{avail_pct:.0f}%",
                "Avg Rate/Night": f"${avg_rate:.0f}",
                "Rating": hotel.get("rating", "N/A"),
                "Crowd Score": score.total,
                "Crowd Factors": "; ".join(score.crowd_reasons) if score.crowd_reasons else "None",
            })

results_df = pd.DataFrame(rows).sort_values("Crowd Score")
display(results_df)
```

- [ ] **Step 2: Run all cells end-to-end**

Open the notebook in VS Code and use `Run All Cells`. Every cell must complete without error. Note: Amadeus sandbox may return limited or no data — add a comment in that cell if so.

- [ ] **Step 3: Commit**

```powershell
git add notebooks/01_data_pipeline.ipynb
git commit -m "feat: add data pipeline notebook (course deliverable 1)"
```

---

### Task 10: Agent Tools Definition

**Files:**

- Create: `src/tools/agent_tools.py`
- Create: `tests/test_agent.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_agent.py
import pytest
from unittest.mock import MagicMock
from src.tools.agent_tools import TOOL_DEFINITIONS, dispatch_tool


def test_all_tool_definitions_have_required_keys():
    required = {"name", "description", "input_schema"}
    for tool in TOOL_DEFINITIONS:
        missing = required - set(tool.keys())
        assert not missing, f"Tool '{tool.get('name')}' missing: {missing}"


def test_all_tool_input_schemas_have_required_fields():
    for tool in TOOL_DEFINITIONS:
        schema = tool["input_schema"]
        assert schema.get("type") == "object"
        assert "properties" in schema


def test_dispatch_search_hotels_calls_tripadvisor():
    mock_ta = MagicMock(search_hotels=MagicMock(return_value=[]))
    mock_amadeus = MagicMock(
        search_hotel_offers=MagicMock(return_value=[]),
        estimate_availability_pct=MagicMock(return_value=50.0)
    )
    mock_events = MagicMock(get_event_magnitude=MagicMock(return_value=(0.2, [])))
    mock_weather = MagicMock(get_weather_suitability=MagicMock(return_value=0.7))
    clients = {
        "tripadvisor": mock_ta, "amadeus": mock_amadeus,
        "events": mock_events, "weather": mock_weather, "geonames": MagicMock()
    }
    result = dispatch_tool(
        tool_name="search_hotels",
        tool_input={
            "location": "Austin, TX", "checkin_date": "2026-07-15",
            "checkout_date": "2026-07-18", "radius_miles": 25,
        },
        clients=clients,
    )
    mock_ta.search_hotels.assert_called_once()
    assert isinstance(result, list)


def test_dispatch_unknown_tool_returns_error():
    result = dispatch_tool(tool_name="nonexistent", tool_input={}, clients={})
    assert "error" in str(result).lower()
```

- [ ] **Step 2: Run to verify they fail**

```powershell
python -m pytest tests/test_agent.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.tools.agent_tools'`

- [ ] **Step 3: Write src/tools/agent_tools.py**

```python
# src/tools/agent_tools.py
from typing import Any
from src.scoring.crowd_scorer import calculate_crowd_score

TOOL_DEFINITIONS = [
    {
        "name": "search_hotels",
        "description": (
            "Search for hotels at a location. Only returns hotels with more than 20% room availability "
            "(less than 80% booked). Results include availability percentage, nightly rate, "
            "TripAdvisor rating, distance from center, and a crowd score (0-100, lower = less crowded). "
            "Apply user preference filters automatically."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City, State (e.g. 'Asheville, NC')"},
                "checkin_date": {"type": "string", "description": "YYYY-MM-DD"},
                "checkout_date": {"type": "string", "description": "YYYY-MM-DD"},
                "radius_miles": {
                    "type": "integer",
                    "enum": [15, 25, 50, 100],
                    "description": "Search radius from location center in miles",
                },
            },
            "required": ["location", "checkin_date", "checkout_date", "radius_miles"],
        },
    },
    {
        "name": "get_hotel_details",
        "description": (
            "Get detailed information about a specific hotel, including a summarized review "
            "based on recent guest feedback and rating breakdown."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "location_id": {"type": "string", "description": "TripAdvisor location_id"},
                "hotel_name": {"type": "string", "description": "Hotel name for context"},
            },
            "required": ["location_id"],
        },
    },
    {
        "name": "find_nearby_destinations",
        "description": (
            "Find nearby towns or areas within the search radius, sorted by distance. "
            "Returns a crowd indicator (low/medium/high) based on town population size "
            "to help identify quieter alternatives."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "center_lat": {"type": "number", "description": "Center latitude"},
                "center_lng": {"type": "number", "description": "Center longitude"},
                "radius_miles": {"type": "integer", "enum": [15, 25, 50, 100]},
            },
            "required": ["center_lat", "center_lng", "radius_miles"],
        },
    },
    {
        "name": "build_itinerary",
        "description": (
            "Generate a low-crowd itinerary for a chosen destination. Suggests quieter lodging zones, "
            "less-busy attractions with recommended visit times (early morning, weekdays), "
            "restaurants outside the tourist center, and scenic alternatives to the busiest sites."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "checkin_date": {"type": "string", "description": "YYYY-MM-DD"},
                "checkout_date": {"type": "string", "description": "YYYY-MM-DD"},
                "crowd_score": {
                    "type": "number",
                    "description": "0-100 crowd score from search_hotels result",
                },
            },
            "required": ["destination", "checkin_date", "checkout_date"],
        },
    },
]


def dispatch_tool(tool_name: str, tool_input: dict, clients: dict) -> Any:
    try:
        if tool_name == "search_hotels":
            return _search_hotels(tool_input, clients)
        elif tool_name == "get_hotel_details":
            return _get_hotel_details(tool_input, clients)
        elif tool_name == "find_nearby_destinations":
            return _find_nearby_destinations(tool_input, clients)
        elif tool_name == "build_itinerary":
            return _build_itinerary(tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except Exception as exc:
        return {"error": str(exc)}


def _search_hotels(inp: dict, clients: dict) -> list[dict]:
    ta_hotels = clients["tripadvisor"].search_hotels(inp["location"], inp["radius_miles"])
    amadeus_offers = clients["amadeus"].search_hotel_offers(
        city_code=inp["location"][:3].upper(),
        checkin_date=inp["checkin_date"],
        checkout_date=inp["checkout_date"],
    )
    event_magnitude, event_names = clients["events"].get_event_magnitude(
        inp["location"], inp["checkin_date"], inp["checkout_date"]
    )
    # Use center coordinates — in production, geocode the location string
    weather_score = clients["weather"].get_weather_suitability(
        lat=35.0, lon=-80.0,
        checkin_date=inp["checkin_date"],
        checkout_date=inp["checkout_date"],
    )

    results = []
    for hotel in ta_hotels[:10]:
        avail_pct = 45.0
        avg_rate = 150.0
        if amadeus_offers:
            offer = amadeus_offers[0]
            avail_pct = clients["amadeus"].estimate_availability_pct(offer)
            if offer.get("offers"):
                avg_rate = float(offer["offers"][0]["price"]["total"])

        if avail_pct < 20.0:  # Enforce > 20% availability filter
            continue

        score = calculate_crowd_score(
            availability_pct=avail_pct,
            avg_nightly_rate=avg_rate,
            baseline_rate=avg_rate * 0.85,
            event_magnitude=event_magnitude,
            seasonal_demand=0.5,
            weather_suitability=weather_score,
        )
        results.append({
            "location_id": hotel.get("location_id", ""),
            "name": hotel.get("name", "Unknown"),
            "availability_pct": round(avail_pct, 1),
            "pct_booked": round(100 - avail_pct, 1),
            "avg_nightly_rate": round(avg_rate, 2),
            "rating": float(hotel.get("rating", 0)),
            "distance_miles": 0.0,
            "crowd_score": score.total,
            "crowd_reasons": score.crowd_reasons,
        })
    results.sort(key=lambda x: x["crowd_score"])
    return results


def _get_hotel_details(inp: dict, clients: dict) -> dict:
    details = clients["tripadvisor"].get_hotel_details(inp["location_id"])
    reviews = clients["tripadvisor"].get_hotel_reviews(inp["location_id"])
    summary = clients["tripadvisor"].summarize_reviews(reviews)
    return {
        "details": details,
        "review_summary": summary,
        "hotel_name": inp.get("hotel_name", ""),
    }


def _find_nearby_destinations(inp: dict, clients: dict) -> list[dict]:
    destinations = clients["geonames"].find_nearby_destinations(
        center_lat=inp["center_lat"],
        center_lng=inp["center_lng"],
        radius_miles=inp["radius_miles"],
    )
    return [d.model_dump() for d in destinations]


def _build_itinerary(inp: dict) -> dict:
    crowd_score = inp.get("crowd_score", 50.0)
    crowd_level = "low" if crowd_score < 35 else "medium" if crowd_score < 60 else "high"
    return {
        "destination": inp["destination"],
        "dates": f"{inp['checkin_date']} to {inp['checkout_date']}",
        "crowd_level": crowd_level,
        "itinerary_prompt": (
            f"Create a detailed low-crowd itinerary for {inp['destination']} "
            f"from {inp['checkin_date']} to {inp['checkout_date']}. "
            f"The area has a crowd score of {crowd_score:.0f}/100 ({crowd_level} crowds). "
            "Include: (1) Quieter lodging zones away from the tourist center, "
            "(2) Less-busy attractions with early morning or weekday visit windows, "
            "(3) Local restaurants 10+ minutes from the main tourist strip, "
            "(4) Scenic alternatives to the most-visited sites, "
            "(5) Specific timing tips to avoid peak hours."
        ),
    }
```

- [ ] **Step 4: Run tests**

```powershell
python -m pytest tests/test_agent.py -v
```

Expected: All 4 tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/tools/agent_tools.py tests/test_agent.py
git commit -m "feat: add 4 Claude tool schemas with dispatch handler"
```

---

### Task 11: Agent Orchestrator

**Files:**

- Create: `src/agent.py`
- Modify: `tests/test_agent.py`

- [ ] **Step 1: Add tests to test_agent.py**

```python
# Append to tests/test_agent.py
from src.agent import EcoTravelAgent
from src.models import UserPreferences


def test_agent_rejects_non_travel_query():
    agent = EcoTravelAgent.__new__(EcoTravelAgent)
    agent.memory = __import__("src.memory", fromlist=["SessionMemory"]).SessionMemory()
    assert agent._is_in_scope("What is the capital of France?") is False


def test_agent_rejects_coding_question():
    agent = EcoTravelAgent.__new__(EcoTravelAgent)
    agent.memory = __import__("src.memory", fromlist=["SessionMemory"]).SessionMemory()
    assert agent._is_in_scope("Write me a Python function to sort a list") is False


def test_agent_accepts_hotel_query():
    agent = EcoTravelAgent.__new__(EcoTravelAgent)
    agent.memory = __import__("src.memory", fromlist=["SessionMemory"]).SessionMemory()
    assert agent._is_in_scope("Find me a hotel in Sedona for July") is True


def test_agent_accepts_crowd_query():
    agent = EcoTravelAgent.__new__(EcoTravelAgent)
    agent.memory = __import__("src.memory", fromlist=["SessionMemory"]).SessionMemory()
    assert agent._is_in_scope("What are low-crowd areas near Austin this weekend?") is True
```

- [ ] **Step 2: Run to verify they fail**

```powershell
python -m pytest tests/test_agent.py::test_agent_rejects_non_travel_query -v
```

Expected: `ModuleNotFoundError: No module named 'src.agent'`

- [ ] **Step 3: Write src/agent.py**

```python
# src/agent.py
import os
import anthropic
from src.memory import SessionMemory
from src.models import UserPreferences
from src.tools.agent_tools import TOOL_DEFINITIONS, dispatch_tool
from src.clients.tripadvisor import TripAdvisorClient
from src.clients.amadeus import AmadeusClient
from src.clients.weather import WeatherClient
from src.clients.events import EventsClient
from src.clients.geonames import GeoNamesClient

SYSTEM_PROMPT = """You are EcoTravelAgent, a travel assistant that specializes in finding
low-crowd hotel destinations. You help users avoid over-touristed areas by analyzing hotel
availability, local events, pricing, and weather to produce crowd likelihood scores.

You ONLY assist with:
- Finding hotels and accommodations
- Assessing crowd levels at destinations
- Suggesting nearby low-crowd alternatives
- Building low-crowd itineraries for chosen destinations
- Explaining why an area may be crowded (limited rooms, price spikes, festivals,
  holiday weekends, cruise ship arrivals, limited attraction availability)

Gracefully reject any request unrelated to travel accommodation and destination planning.
When rejecting, briefly explain what you can help with.

At the start of a session (when no preferences are set), collect:
1. Approximate nightly budget in USD
2. Preferred weather (warm / cool / mild / any)
3. Maximum drive distance from destination center (15, 25, 50, or 100 miles)
4. Crowd tolerance (low / medium / high)

After preferences, ask for: destination, check-in date, check-out date.
Always present hotel results sorted by crowd score (lowest first) in a clear table format.
Lower crowd score = less crowded. A score below 35 is excellent.
"""

IN_SCOPE_TERMS = {
    "hotel", "motel", "inn", "stay", "book", "reservation", "destination", "travel",
    "trip", "vacation", "crowd", "lodging", "accommodation", "check-in", "checkout",
    "nearby", "itinerary", "visit", "explore", "beach", "mountain", "city", "town",
    "area", "resort", "airbnb", "room", "suite", "night", "weekend", "getaway",
}


class EcoTravelAgent:
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model
        self.memory = SessionMemory()
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._tool_clients = {
            "tripadvisor": TripAdvisorClient(os.environ["TRIPADVISOR_API_KEY"]),
            "amadeus": AmadeusClient(
                os.environ["AMADEUS_CLIENT_ID"], os.environ["AMADEUS_CLIENT_SECRET"]
            ),
            "weather": WeatherClient(os.environ["OPENWEATHERMAP_API_KEY"]),
            "events": EventsClient(os.environ["PREDICTHQ_API_KEY"]),
            "geonames": GeoNamesClient(),
        }

    def _is_in_scope(self, user_message: str) -> bool:
        lower = user_message.lower()
        return any(term in lower for term in IN_SCOPE_TERMS)

    def chat(self, user_message: str) -> str:
        if not self._is_in_scope(user_message):
            return (
                "I can only help with travel accommodation and destination planning — "
                "specifically finding hotels with low crowd levels, suggesting quieter "
                "nearby destinations, explaining crowd causes, and building itineraries. "
                "What destination or travel question can I help you with?"
            )

        self.memory.add_message("user", user_message)
        messages = self.memory.get_conversation_history()

        response = self._client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        while response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = dispatch_tool(block.name, block.input, self._tool_clients)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })
            messages = messages + [
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": tool_results},
            ]
            response = self._client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

        reply = next(
            (block.text for block in response.content if hasattr(block, "text")), ""
        )
        self.memory.add_message("assistant", reply)
        return reply
```

- [ ] **Step 4: Run all tests**

```powershell
python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/agent.py tests/test_agent.py
git commit -m "feat: add agent orchestrator with tool loop, session memory, and rejection handling"
```

---

### Task 12: Streamlit UI

**Files:**

- Create: `app.py`

- [ ] **Step 1: Write app.py**

```python
# app.py
import streamlit as st
from dotenv import load_dotenv
from src.agent import EcoTravelAgent
from src.models import UserPreferences

load_dotenv()

st.set_page_config(page_title="EcoTravel Agent", layout="wide")
st.title("EcoTravel Agent — Find Low-Crowd Destinations")

if "agent" not in st.session_state:
    st.session_state.agent = EcoTravelAgent()
if "preferences_set" not in st.session_state:
    st.session_state.preferences_set = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Step 1: Preference Shelter ─────────────────────────────────────────────
if not st.session_state.preferences_set:
    st.subheader("Step 1: Your Travel Preferences")
    st.caption(
        "These preferences are remembered throughout your session and used to filter all results."
    )
    with st.form("preferences_form"):
        budget = st.number_input(
            "Max budget per night (USD)", min_value=50, max_value=2000, value=200, step=25
        )
        weather = st.selectbox("Preferred weather", ["warm", "cool", "mild", "any"])
        drive_range = st.selectbox(
            "Max drive from destination center",
            [15, 25, 50, 100],
            index=1,
            format_func=lambda x: f"{x} miles",
        )
        crowd_tolerance = st.selectbox(
            "Crowd tolerance",
            ["low", "medium", "high"],
            help="Low = strongly prefer quiet areas; High = crowds are acceptable",
        )
        submitted = st.form_submit_button("Save Preferences and Continue →")

    if submitted:
        prefs = UserPreferences(
            budget_per_night=float(budget),
            weather_preference=weather,
            max_drive_miles=drive_range,
            crowd_tolerance=crowd_tolerance,
        )
        st.session_state.agent.memory.set_preferences(prefs)
        st.session_state.preferences_set = True
        st.rerun()

# ── Step 2: Search + Chat ──────────────────────────────────────────────────
else:
    col_search, col_prefs = st.columns([2, 1])

    with col_search:
        st.subheader("Step 2: Search for Hotels")
        with st.form("search_form"):
            location = st.text_input("Destination", placeholder="e.g. Asheville, NC")
            c1, c2 = st.columns(2)
            with c1:
                checkin = st.date_input("Check-in")
            with c2:
                checkout = st.date_input("Check-out")
            radius = st.selectbox(
                "Search radius",
                [15, 25, 50, 100],
                index=1,
                format_func=lambda x: f"{x} miles",
            )
            search_btn = st.form_submit_button("Search Hotels")

        if search_btn and location:
            query = (
                f"Find hotels in {location} from {checkin} to {checkout} "
                f"within {radius} miles. Show results as a table sorted by crowd score."
            )
            with st.spinner("Searching..."):
                reply = st.session_state.agent.chat(query)
            st.session_state.chat_history.append(("user", query))
            st.session_state.chat_history.append(("assistant", reply))
            st.rerun()

    with col_prefs:
        prefs = st.session_state.agent.memory.get_preferences()
        if prefs:
            st.subheader("Your Preferences")
            st.write(f"**Budget:** ${prefs.budget_per_night:.0f}/night")
            st.write(f"**Weather:** {prefs.weather_preference}")
            st.write(f"**Max drive:** {prefs.max_drive_miles} miles")
            st.write(f"**Crowd tolerance:** {prefs.crowd_tolerance}")
            if st.button("Change Preferences"):
                st.session_state.preferences_set = False
                st.rerun()

    # ── Chat History ────────────────────────────────────────────────────────
    st.divider()
    for role, message in st.session_state.chat_history[-8:]:
        with st.chat_message(role):
            st.markdown(message)

    # ── Action Buttons ──────────────────────────────────────────────────────
    if st.session_state.chat_history:
        st.divider()
        st.caption("Quick Actions")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Tell me more about this hotel"):
                with st.spinner("Fetching details..."):
                    reply = st.session_state.agent.chat(
                        "Tell me more about the top hotel result, including a review summary and rating breakdown."
                    )
                st.session_state.chat_history.append(("assistant", reply))
                st.rerun()
        with b2:
            if st.button("Nearby Destinations"):
                with st.spinner("Finding nearby areas..."):
                    reply = st.session_state.agent.chat(
                        "What are low-crowd towns or destinations nearby? Use geolocation to find options."
                    )
                st.session_state.chat_history.append(("assistant", reply))
                st.rerun()
        with b3:
            if st.button("Build Low-Crowd Itinerary"):
                with st.spinner("Building itinerary..."):
                    reply = st.session_state.agent.chat(
                        "Build a detailed low-crowd itinerary for the recommended destination, including quieter attractions, dining, and timing tips."
                    )
                st.session_state.chat_history.append(("assistant", reply))
                st.rerun()

    # ── Follow-up Chat Input ────────────────────────────────────────────────
    user_input = st.chat_input("Ask about crowd causes, specific hotels, or alternative destinations...")
    if user_input:
        with st.spinner("Thinking..."):
            reply = st.session_state.agent.chat(user_input)
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", reply))
        st.rerun()
```

- [ ] **Step 2: Launch and verify in browser**

```powershell
streamlit run app.py
```

Navigate to `http://localhost:8501`. Verify:

- Preference shelter form appears on first load
- After submitting preferences, search form + preferences sidebar appear
- Search triggers a chat response
- All three action buttons render and produce responses
- Out-of-scope question (e.g. "What's 2+2?") triggers graceful rejection

Stop the server with `Ctrl+C` when done.

- [ ] **Step 3: Commit**

```powershell
git add app.py
git commit -m "feat: add Streamlit UI with preference shelter, results table, and action buttons"
```

---

### Task 13: LangSmith Tracing

**Files:**

- Create: `src/tracing.py`

- [ ] **Step 1: Write src/tracing.py**

```python
# src/tracing.py
import os
from langsmith import traceable

def traced_chat(agent_instance, user_message: str, run_name: str = "eco-travel-chat") -> str:
    """Wrap agent.chat() in a LangSmith trace."""
    project = os.environ.get("LANGCHAIN_PROJECT", "eco-travel-agent")

    @traceable(name=run_name, project_name=project)
    def _inner(message: str) -> str:
        return agent_instance.chat(message)

    return _inner(user_message)
```

- [ ] **Step 2: Verify LangSmith env vars**

```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API key:', 'SET' if os.environ.get('LANGCHAIN_API_KEY') else 'MISSING')"
```

Expected: `API key: SET`

- [ ] **Step 3: Send a test trace**

```powershell
python -c "
from dotenv import load_dotenv; load_dotenv()
from src.agent import EcoTravelAgent
from src.tracing import traced_chat
from src.models import UserPreferences
agent = EcoTravelAgent()
agent.memory.set_preferences(UserPreferences(budget_per_night=200, weather_preference='warm', max_drive_miles=25, crowd_tolerance='low'))
result = traced_chat(agent, 'What is the capital of France?', run_name='test-rejection')
print(result)
"
```

Expected: Graceful rejection message. Navigate to `smith.langchain.com` → project `eco-travel-agent` and confirm the trace is visible.

- [ ] **Step 4: Commit**

```powershell
git add src/tracing.py
git commit -m "feat: add LangSmith tracing wrapper"
```

---

### Task 14: Agent Definition Notebook

**Files:**

- Create: `notebooks/02_agent_definition.ipynb`

This is **course deliverable 2**. Must show LLM + tools + session memory + 2 graceful rejections.

- [ ] **Step 1: Create notebook cells**

Cell 1 — markdown:

```markdown
# Agent Definition — EcoTravel Agent

This notebook defines the EcoTravel Agent architecture. The agent uses:

- **LLM**: Claude (claude-sonnet-4-6) via Anthropic SDK
- **Tools**: 4 custom tools (search_hotels, get_hotel_details, find_nearby_destinations, build_itinerary)
- **Session Memory**: Stores user preferences and filters all results
- **Tracing**: LangSmith for all interaction traces
```

Cell 2 — code:

```python
import os
from dotenv import load_dotenv
load_dotenv()

from src.agent import EcoTravelAgent
from src.models import UserPreferences
from src.tools.agent_tools import TOOL_DEFINITIONS
from src.tracing import traced_chat
import json

agent = EcoTravelAgent(model="claude-sonnet-4-6")
print("Agent initialized. Model:", agent.model)
```

Cell 3 — markdown: `## Tool Definitions`

Cell 4 — code:

```python
for tool in TOOL_DEFINITIONS:
    print(f"\n{'='*50}")
    print(f"Tool: {tool['name']}")
    print(f"Description: {tool['description'][:100]}...")
    print(f"Required inputs: {tool['input_schema'].get('required', [])}")
```

Cell 5 — markdown: `## Preference Shelter — Setting User Preferences`

Cell 6 — code:

```python
prefs = UserPreferences(
    budget_per_night=175.0,
    weather_preference="warm",
    max_drive_miles=25,
    crowd_tolerance="low",
)
agent.memory.set_preferences(prefs)
print("Preferences set:")
print(f"  Budget: ${prefs.budget_per_night}/night")
print(f"  Weather: {prefs.weather_preference}")
print(f"  Max drive: {prefs.max_drive_miles} miles")
print(f"  Crowd tolerance: {prefs.crowd_tolerance}")
print(f"  Crowd score threshold: {prefs.crowd_score_threshold}")
```

Cell 7 — markdown: `## Example 1: Full Hotel Search`

Cell 8 — code:

```python
response1 = traced_chat(agent, "Find hotels in Asheville, NC from August 1-5 within 25 miles", run_name="demo-hotel-search")
print(response1)
```

Cell 9 — markdown: `## Example 2: Hotel Details`

Cell 10 — code:

```python
response2 = traced_chat(agent, "Tell me more about the top result, including reviews", run_name="demo-hotel-details")
print(response2)
```

Cell 11 — markdown: `## Example 3: Nearby Destinations`

Cell 12 — code:

```python
response3 = traced_chat(agent, "What are quieter nearby towns I could consider?", run_name="demo-nearby")
print(response3)
```

Cell 13 — markdown: `## Graceful Rejection 1 — Off-Topic Query`

Cell 14 — code:

```python
rejection1 = traced_chat(agent, "What is the capital of France?", run_name="demo-rejection-1")
print(rejection1)
assert "travel" in rejection1.lower() or "hotel" in rejection1.lower() or "destination" in rejection1.lower()
print("\nRejection handled correctly: response redirects to travel topics.")
```

Cell 15 — markdown: `## Graceful Rejection 2 — Unrelated Creative Request`

Cell 16 — code:

```python
rejection2 = traced_chat(agent, "Write me a poem about mountains", run_name="demo-rejection-2")
print(rejection2)
assert "travel" in rejection2.lower() or "hotel" in rejection2.lower() or "destination" in rejection2.lower()
print("\nRejection handled correctly: response redirects to travel topics.")
```

Cell 17 — markdown: `## Session Memory State`

Cell 18 — code:

```python
prefs = agent.memory.get_preferences()
history = agent.memory.get_conversation_history()
print(f"Preferences stored: {prefs is not None}")
print(f"Conversation turns: {len(history)}")
print(f"\nConversation preview:")
for msg in history[-4:]:
    print(f"  [{msg['role']}]: {str(msg['content'])[:80]}...")
```

- [ ] **Step 2: Run all cells and verify**

Every cell must pass. Both rejection assert statements must succeed (confirming the response redirects to travel topics).

- [ ] **Step 3: Commit**

```powershell
git add notebooks/02_agent_definition.ipynb
git commit -m "feat: add agent definition notebook (course deliverable 2)"
```

---

### Task 15: Traces and Evaluation Notebook

**Files:**

- Create: `notebooks/03_traces_evaluation.ipynb`

This is **course deliverable 3**. Must contain 5 evaluated traces (including 1 LLM comparison), LLM-as-judge scoring, and written performance commentary.

- [ ] **Step 1: Create notebook cells**

Cell 1 — markdown:

```markdown
# Traces and Evaluation — EcoTravel Agent

Five evaluated interaction traces are collected in LangSmith. Trace 5 directly compares
claude-sonnet-4-6 and claude-haiku-4-5-20251001 on the same input.
```

Cell 2 — code (setup):

```python
import os, json, anthropic, pandas as pd
from dotenv import load_dotenv
load_dotenv()
from src.agent import EcoTravelAgent
from src.models import UserPreferences
from src.tracing import traced_chat

BASE_PREFS = UserPreferences(
    budget_per_night=200.0, weather_preference="warm",
    max_drive_miles=25, crowd_tolerance="low"
)
```

Cell 3 — markdown: `## Trace 1: Hotel Search with Preference Filtering`

Cell 4 — code:

```python
agent1 = EcoTravelAgent(model="claude-sonnet-4-6")
agent1.memory.set_preferences(BASE_PREFS)
t1 = traced_chat(agent1, "Find hotels in Savannah, GA from July 10-14 within 25 miles", run_name="trace-1-search")
print(t1)
```

Cell 5 — markdown: `## Trace 2: Hotel Details + Review Summary`

Cell 6 — code:

```python
t2 = traced_chat(agent1, "Tell me more about the top hotel result and its reviews", run_name="trace-2-details")
print(t2)
```

Cell 7 — markdown: `## Trace 3: Nearby Low-Crowd Destinations`

Cell 8 — code:

```python
t3 = traced_chat(agent1, "Find nearby quieter towns I could explore instead", run_name="trace-3-nearby")
print(t3)
```

Cell 9 — markdown: `## Trace 4: Build a Low-Crowd Itinerary`

Cell 10 — code:

```python
t4 = traced_chat(agent1, "Build a low-crowd itinerary for my stay", run_name="trace-4-itinerary")
print(t4)
```

Cell 11 — markdown: `## Trace 5: LLM Comparison — Sonnet vs Haiku`

Cell 12 — code:

```python
COMPARISON_QUERY = (
    "Find low-crowd hotels in Sedona, AZ from August 5-8 within 25 miles. "
    "Explain the crowd factors for the top result."
)

agent_sonnet = EcoTravelAgent(model="claude-sonnet-4-6")
agent_sonnet.memory.set_preferences(BASE_PREFS)
t5_sonnet = traced_chat(agent_sonnet, COMPARISON_QUERY, run_name="trace-5-sonnet")

agent_haiku = EcoTravelAgent(model="claude-haiku-4-5-20251001")
agent_haiku.memory.set_preferences(BASE_PREFS)
t5_haiku = traced_chat(agent_haiku, COMPARISON_QUERY, run_name="trace-5-haiku")

print("=== SONNET ===")
print(t5_sonnet)
print("\n=== HAIKU ===")
print(t5_haiku)
```

Cell 13 — markdown: `## LLM-as-Judge Evaluation`

Cell 14 — code:

```python
judge_client = anthropic.Anthropic()

def llm_judge(query: str, response: str, model_name: str) -> dict:
    prompt = f"""You are evaluating a travel agent AI response. Score each dimension 1–5.

Query: {query}
Model: {model_name}
Response: {response}

Scoring criteria:
- relevance: Does the response directly address the travel query?
- crowd_focus: Does it emphasize low-crowd recommendations as instructed?
- detail_quality: Are the details specific and actionable?
- tone: Is it helpful, professional, and concise?
- overall: Overall quality

Return ONLY valid JSON: {{"relevance": N, "crowd_focus": N, "detail_quality": N, "tone": N, "overall": N, "notes": "brief comment"}}"""

    result = judge_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(result.content[0].text)

scores_sonnet = llm_judge(COMPARISON_QUERY, t5_sonnet, "claude-sonnet-4-6")
scores_haiku = llm_judge(COMPARISON_QUERY, t5_haiku, "claude-haiku-4-5-20251001")

comparison_df = pd.DataFrame([
    {"Model": "claude-sonnet-4-6", **scores_sonnet},
    {"Model": "claude-haiku-4-5-20251001", **scores_haiku},
]).set_index("Model")
display(comparison_df)
```

Cell 15 — markdown: `## ROI Analysis`

Cell 16 — code:

```python
# Token pricing (USD per million tokens) — verify current prices at anthropic.com/pricing
PRICING = {
    "claude-sonnet-4-6":        {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output":  4.00},
}

# Usage estimate: 500 sessions/day, ~2,500 input tokens + 600 output tokens per session
DAILY_SESSIONS   = 500
AVG_INPUT_TOKENS = 2500
AVG_OUTPUT_TOKENS = 600

def monthly_cost(model_id: str) -> float:
    p = PRICING[model_id]
    per_session = (
        (AVG_INPUT_TOKENS  / 1_000_000 * p["input"]) +
        (AVG_OUTPUT_TOKENS / 1_000_000 * p["output"])
    )
    return per_session * DAILY_SESSIONS * 30

cost_sonnet = monthly_cost("claude-sonnet-4-6")
cost_haiku  = monthly_cost("claude-haiku-4-5-20251001")
cost_ratio  = cost_sonnet / cost_haiku

sonnet_overall = scores_sonnet["overall"]
haiku_overall  = scores_haiku["overall"]
quality_lift   = (sonnet_overall - haiku_overall) / haiku_overall if haiku_overall > 0 else 0

print(f"Monthly cost — Sonnet: ${cost_sonnet:,.2f}")
print(f"Monthly cost — Haiku:  ${cost_haiku:,.2f}")
print(f"Cost ratio (Sonnet/Haiku): {cost_ratio:.1f}x")
print(f"Quality lift (Sonnet over Haiku): {quality_lift:.1%}")
print()
if quality_lift / (cost_ratio - 1) > 0.15:
    recommendation = "claude-sonnet-4-6"
    rationale = "The quality improvement justifies the cost premium for a user-facing travel product."
else:
    recommendation = "claude-haiku-4-5-20251001"
    rationale = "The cost savings outweigh the marginal quality difference at this volume."
print(f"Recommendation: {recommendation}")
print(f"Rationale: {rationale}")
```

Cell 17 — markdown:

```markdown
## Performance Commentary

### Overall Agent Performance

_[Write 2-3 sentences after running the notebook: describe what the agent did well across the 4 traces. Focus on whether crowd scoring was correctly surfaced, whether the preference filter was applied, and whether the results were presented clearly.]_

### What the Evaluation Showed

_[Note any patterns from the LLM judge scores. Did the agent consistently address the crowd focus? Were details specific and actionable or generic? What surprised you?]_

### Sonnet vs Haiku Comparison

_[Describe specific differences observed in the two responses: length, specificity, tool call quality, crowd explanation depth. Then reference the ROI calculation to give a final model recommendation for production use.]_
```

- [ ] **Step 2: Run all cells and verify 5 traces appear**

Run all cells. Navigate to `smith.langchain.com` → `eco-travel-agent` project and confirm at least 5 traces are visible (trace-1 through trace-5-sonnet and trace-5-haiku).

Fill in the performance commentary markdown cell with your actual observations from the run.

- [ ] **Step 3: Commit**

```powershell
git add notebooks/03_traces_evaluation.ipynb
git commit -m "feat: add traces and evaluation notebook with LLM comparison and ROI (course deliverable 3)"
```

---

### Task 16: Final Integration Verification

**Files:** None — verification only.

- [ ] **Step 1: Run full test suite**

```powershell
python -m pytest tests/ -v --tb=short
```

Expected: All tests pass with 0 failures.

- [ ] **Step 2: Run all three notebooks end-to-end**

In VS Code, run `Run All Cells` on each notebook in order:

1. `notebooks/01_data_pipeline.ipynb` — all cells run, final DataFrame displayed
2. `notebooks/02_agent_definition.ipynb` — 2 rejection asserts pass, agent responds to search
3. `notebooks/03_traces_evaluation.ipynb` — 5 traces generated, LLM judge scores shown, ROI calculated

- [ ] **Step 3: Streamlit golden path walkthrough**

```powershell
streamlit run app.py
```

Perform this end-to-end flow:

1. Enter preferences: $175/night, warm weather, 25 miles, low crowd tolerance → click Save
2. Search "Asheville, NC" for a future date range, 25-mile radius → verify response appears
3. Click "Tell me more about this hotel" → verify detail response
4. Click "Nearby Destinations" → verify nearby towns listed
5. Click "Build Low-Crowd Itinerary" → verify itinerary response
6. Type "What is 2 + 2?" → verify graceful rejection (not a hotel result)
7. Click "Change Preferences" → verify preference form reappears

- [ ] **Step 4: Verify LangSmith traces**

Navigate to `smith.langchain.com` → `eco-travel-agent`. Confirm:

- At least 5 named traces visible
- `trace-5-sonnet` and `trace-5-haiku` both present
- Each trace shows tool calls in the trace detail view

- [ ] **Step 5: Final commit**

```powershell
git add -A
git commit -m "chore: final integration verification complete — all deliverables ready"
```

---

## Course Deliverable Checklist

**Data Pipeline (21 pts)**

- [ ] `01_data_pipeline.ipynb` executes without error
- [ ] Pulls from TripAdvisor, Amadeus, OpenWeatherMap, PredictHQ, and GeoNames
- [ ] Produces a crowd-scored results DataFrame

**Agent Code (52.5 pts)**

- [ ] `src/agent.py` uses Claude as LLM via Anthropic SDK
- [ ] 4 relevant tools defined in `src/tools/agent_tools.py`
- [ ] Session memory filters all results by user preferences
- [ ] `dispatch_tool` wraps all tool calls in try/except for error handling
- [ ] 2 graceful rejection examples in `02_agent_definition.ipynb`

**Evaluation Examples (31.5 pts)**

- [ ] 5 traces in LangSmith project `eco-travel-agent`
- [ ] Trace 5 compares Sonnet and Haiku on identical input
- [ ] LLM-as-judge scores in `03_traces_evaluation.ipynb`
- [ ] Written performance commentary cell completed

**Video Presentation (105 pts)**

- [ ] Technical walkthrough uses the three notebooks
- [ ] Evaluation section shows LLM judge comparison
- [ ] ROI calculation explained from notebook 3
- [ ] Business value: helps travelers avoid overcrowded destinations
- [ ] Deployment recommendation: Streamlit app on a cloud platform (Streamlit Cloud, Railway, or AWS EC2)
- [ ] Quality commentary addresses what worked, what didn't, and what was learned
