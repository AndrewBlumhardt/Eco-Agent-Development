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
    assert history[0]["content"] == "hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "hi there"
