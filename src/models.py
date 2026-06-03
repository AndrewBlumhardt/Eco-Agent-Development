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
