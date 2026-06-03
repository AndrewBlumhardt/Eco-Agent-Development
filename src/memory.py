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
