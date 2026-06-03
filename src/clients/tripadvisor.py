# src/clients/tripadvisor.py
import requests
from typing import Any

BASE_URL = "https://api.content.tripadvisor.com/api/v1"


class TripAdvisorClient:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._headers = {"accept": "application/json"}

    def search_hotels(self, location: str, radius_miles: int) -> list[dict[str, Any]]:
        params = {
            "key": self._api_key,
            "searchQuery": location,
            "category": "hotels",
            "radius": radius_miles,
            "radiusUnit": "mi",
            "language": "en",
        }
        resp = requests.get(f"{BASE_URL}/location/search", params=params, headers=self._headers)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_hotel_details(self, location_id: str) -> dict[str, Any]:
        params = {"key": self._api_key, "language": "en", "currency": "USD"}
        resp = requests.get(f"{BASE_URL}/location/{location_id}/details", params=params, headers=self._headers)
        resp.raise_for_status()
        return resp.json()

    def get_hotel_reviews(self, location_id: str, limit: int = 5) -> list[dict[str, Any]]:
        params = {"key": self._api_key, "language": "en", "limit": limit}
        resp = requests.get(f"{BASE_URL}/location/{location_id}/reviews", params=params, headers=self._headers)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def summarize_reviews(self, reviews: list[dict]) -> str:
        if not reviews:
            return "No reviews available."
        avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews)
        snippets = "; ".join(r.get("text", "")[:120] for r in reviews[:3])
        return f"Average rating: {avg_rating:.1f}/5. Recent guest highlights: {snippets}"
