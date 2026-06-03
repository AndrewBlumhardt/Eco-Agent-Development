# src/clients/geonames.py
import math
from pathlib import Path
from src.models import NearbyDestination

GEONAMES_PATH = Path(__file__).parent.parent.parent / "data" / "cities500.txt"


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _crowd_indicator(population: int) -> str:
    if population < 10_000:
        return "low"
    elif population < 100_000:
        return "medium"
    return "high"


class GeoNamesClient:
    def __init__(self, data_path: Path = GEONAMES_PATH):
        self._cities = self._load(data_path)

    def _load(self, path: Path) -> list[dict]:
        cities = []
        if not path.exists():
            return cities
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                parts = line.strip().split("\t")
                if len(parts) < 15:
                    continue
                try:
                    cities.append({
                        "name": parts[1],
                        "lat": float(parts[4]),
                        "lng": float(parts[5]),
                        "population": int(parts[14]) if parts[14] else 0,
                    })
                except (ValueError, IndexError):
                    continue
        return cities

    def find_nearby_destinations(
        self, center_lat: float, center_lng: float, radius_miles: int, limit: int = 5
    ) -> list[NearbyDestination]:
        results = []
        for city in self._cities:
            dist = _haversine_miles(center_lat, center_lng, city["lat"], city["lng"])
            if 5 <= dist <= radius_miles:
                results.append(NearbyDestination(
                    name=city["name"],
                    lat=city["lat"],
                    lng=city["lng"],
                    distance_miles=round(dist, 1),
                    population=city["population"],
                    crowd_indicator=_crowd_indicator(city["population"]),
                ))
        results.sort(key=lambda x: x.distance_miles)
        return results[:limit]
