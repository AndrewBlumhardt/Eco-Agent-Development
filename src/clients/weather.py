import requests
from datetime import datetime

BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
GOOD_CONDITIONS = {"Clear", "Clouds"}
BAD_CONDITIONS = {"Rain", "Snow", "Thunderstorm", "Drizzle", "Tornado", "Squall"}


class WeatherClient:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def get_weather_suitability(
        self, lat: float, lon: float, checkin_date: str, checkout_date: str
    ) -> float:
        """Returns 0.0 (bad weather) to 1.0 (ideal weather)."""
        params = {"lat": lat, "lon": lon, "appid": self._api_key, "units": "metric"}
        resp = requests.get(BASE_URL, params=params)
        resp.raise_for_status()
        forecasts = resp.json().get("list", [])

        checkin = datetime.strptime(checkin_date, "%Y-%m-%d")
        checkout = datetime.strptime(checkout_date, "%Y-%m-%d")

        relevant = [
            f for f in forecasts
            if checkin <= datetime.strptime(f["dt_txt"], "%Y-%m-%d %H:%M:%S") <= checkout
        ]
        if not relevant:
            return 0.5

        good_count = sum(
            1 for f in relevant if f["weather"][0]["main"] in GOOD_CONDITIONS
        )
        bad_count = sum(
            1 for f in relevant if f["weather"][0]["main"] in BAD_CONDITIONS
        )
        total = len(relevant)
        score = (good_count - bad_count) / total if total > 0 else 0.5
        return round(max(0.0, min(1.0, score)), 2)
