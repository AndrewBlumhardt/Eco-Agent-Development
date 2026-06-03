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
