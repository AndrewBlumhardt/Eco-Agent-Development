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


from src.clients.amadeus import AmadeusClient
from src.clients.weather import WeatherClient
from src.clients.events import EventsClient


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


from src.clients.geonames import GeoNamesClient, _haversine_miles


def test_haversine_miles_known_distance():
    # Austin TX to San Antonio TX is approximately 80 miles
    dist = _haversine_miles(30.2672, -97.7431, 29.4241, -98.4936)
    assert 70 < dist < 85


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
