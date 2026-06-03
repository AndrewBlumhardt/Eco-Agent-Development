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
