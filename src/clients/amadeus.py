# src/clients/amadeus.py
import requests
import time
from typing import Any

SANDBOX_BASE = "https://test.api.amadeus.com"


class AmadeusClient:
    def __init__(self, client_id: str, client_secret: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token: str | None = None
        self._token_expiry: float = 0.0

    def _get_token(self) -> str:
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token
        resp = requests.post(
            f"{SANDBOX_BASE}/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        self._token_expiry = time.time() + data["expires_in"] - 60
        return self._access_token

    def search_hotel_offers(
        self,
        city_code: str,
        checkin_date: str,
        checkout_date: str,
        adults: int = 2,
    ) -> list[dict[str, Any]]:
        token = self._get_token()
        params = {
            "cityCode": city_code,
            "checkInDate": checkin_date,
            "checkOutDate": checkout_date,
            "adults": adults,
            "currency": "USD",
        }
        resp = requests.get(
            f"{SANDBOX_BASE}/v3/shopping/hotel-offers",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])

    def estimate_availability_pct(self, hotel_offer: dict) -> float:
        # More available rate offers correlates with lower occupancy.
        # Treat 1 offer ≈ 15% available, 5+ offers ≈ 75%+ available.
        num_offers = len(hotel_offer.get("offers", []))
        pct = min(num_offers * 15.0, 95.0)
        return round(max(pct, 5.0), 1)
