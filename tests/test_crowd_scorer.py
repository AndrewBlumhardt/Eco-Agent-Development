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
