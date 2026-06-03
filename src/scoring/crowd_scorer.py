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
