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
