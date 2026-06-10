# src/tools/agent_tools.py
from typing import Any
from src.clients.static_reviews import StaticReviewsClient
from src.scoring.crowd_scorer import calculate_crowd_score

TOOL_DEFINITIONS = [
    {
        "name": "search_hotels",
        "description": (
            "Search for hotels at a location. Only returns hotels with more than 20% room availability "
            "(less than 80% booked). Results include availability percentage, nightly rate, "
            "TripAdvisor rating, distance from center, and a crowd score (0-100, lower = less crowded). "
            "Apply user preference filters automatically."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City, State (e.g. 'Asheville, NC')"},
                "checkin_date": {"type": "string", "description": "YYYY-MM-DD"},
                "checkout_date": {"type": "string", "description": "YYYY-MM-DD"},
                "radius_miles": {
                    "type": "integer",
                    "enum": [15, 25, 50, 100],
                    "description": "Search radius from location center in miles",
                },
            },
            "required": ["location", "checkin_date", "checkout_date", "radius_miles"],
        },
    },
    {
        "name": "get_hotel_details",
        "description": (
            "Get detailed information about a specific hotel, including a summarized review "
            "based on recent guest feedback and rating breakdown."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "location_id": {"type": "string", "description": "TripAdvisor location_id"},
                "hotel_name": {"type": "string", "description": "Hotel name for context"},
            },
            "required": ["location_id"],
        },
    },
    {
        "name": "find_nearby_destinations",
        "description": (
            "Find nearby towns or areas within the search radius, sorted by distance. "
            "Returns a crowd indicator (low/medium/high) based on town population size "
            "to help identify quieter alternatives."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "center_lat": {"type": "number", "description": "Center latitude"},
                "center_lng": {"type": "number", "description": "Center longitude"},
                "radius_miles": {"type": "integer", "enum": [15, 25, 50, 100]},
            },
            "required": ["center_lat", "center_lng", "radius_miles"],
        },
    },
    {
        "name": "build_itinerary",
        "description": (
            "Generate a low-crowd itinerary for a chosen destination. Suggests quieter lodging zones, "
            "less-busy attractions with recommended visit times (early morning, weekdays), "
            "restaurants outside the tourist center, and scenic alternatives to the busiest sites."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "checkin_date": {"type": "string", "description": "YYYY-MM-DD"},
                "checkout_date": {"type": "string", "description": "YYYY-MM-DD"},
                "crowd_score": {
                    "type": "number",
                    "description": "0-100 crowd score from search_hotels result",
                },
            },
            "required": ["destination", "checkin_date", "checkout_date"],
        },
    },
]


def dispatch_tool(tool_name: str, tool_input: dict, clients: dict) -> Any:
    """Route a Claude tool_use block to the appropriate client function."""
    {
        "name": "search_reviews",
        "description": (
            "Search a dataset of 20,000 real TripAdvisor hotel reviews for reviews "
            "matching specific keywords or sentiment. Use this to find what guests say "
            "about quiet, peaceful, uncrowded stays (use sentiment='low_crowd') or about "
            "busy, noisy, crowded hotels (use sentiment='high_crowd'). You can also search "
            "any custom keyword (e.g. 'mountain view', 'breakfast', 'parking'). "
            "Results include the review text snippet and star rating."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sentiment": {
                    "type": "string",
                    "enum": ["low_crowd", "high_crowd", "custom"],
                    "description": (
                        "'low_crowd' = search for quiet/peaceful/uncrowded mentions in 4-5 star reviews; "
                        "'high_crowd' = search for crowded/noisy mentions in 1-3 star reviews; "
                        "'custom' = search using the keywords field"
                    ),
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Custom keywords to search for. Only used when sentiment='custom'.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of reviews to return (default 5, max 10).",
                },
            },
            "required": ["sentiment"],
        },
    },
]


def dispatch_tool
    try:
        if tool_name == "search_hotels":
            return _search_hotels(tool_input, clients)
        elif tool_name == "get_hotel_details":
            return _get_hotel_details(tool_input, clients)
        elif tool_name == "find_nearby_destinations":
            return _find_nearby_destinations(tool_input, clients)
        elif tool_name == "build_itinerary":
            return _build_itinerary(tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
            elif tool_name == "search_reviews":
                return _search_reviews(tool_input)
    except Exception as exc:
        return {"error": str(exc)}


def _search_hotels(inp: dict, clients: dict) -> list[dict]:
    ta_hotels = clients["tripadvisor"].search_hotels(inp["location"], inp["radius_miles"])
    amadeus_offers = (
        clients["amadeus"].search_hotel_offers(
            city_code=inp["location"][:3].upper(),
            checkin_date=inp["checkin_date"],
            checkout_date=inp["checkout_date"],
        )
        if clients.get("amadeus") else []
    )
    event_magnitude, event_names = (
        clients["events"].get_event_magnitude(
            inp["location"], inp["checkin_date"], inp["checkout_date"]
        )
        if clients.get("events") else (0.0, [])
    )
    # Use approximate center coordinates — geocoding integration can be added later
    weather_score = clients["weather"].get_weather_suitability(
        lat=35.0, lon=-80.0,
        checkin_date=inp["checkin_date"],
        checkout_date=inp["checkout_date"],
    )

    results = []
    for hotel in ta_hotels[:10]:
        avail_pct = 45.0
        avg_rate = 150.0
        if amadeus_offers and clients.get("amadeus"):
            offer = amadeus_offers[0]
            avail_pct = clients["amadeus"].estimate_availability_pct(offer)
            if offer.get("offers"):
                avg_rate = float(offer["offers"][0]["price"]["total"])

        if avail_pct < 20.0:  # Enforce >20% availability filter
            continue

        score = calculate_crowd_score(
            availability_pct=avail_pct,
            avg_nightly_rate=avg_rate,
            baseline_rate=avg_rate * 0.85,
            event_magnitude=event_magnitude,
            seasonal_demand=0.5,
            weather_suitability=weather_score,
        )
        results.append({
            "location_id": hotel.get("location_id", ""),
            "name": hotel.get("name", "Unknown"),
            "availability_pct": round(avail_pct, 1),
            "pct_booked": round(100 - avail_pct, 1),
            "avg_nightly_rate": round(avg_rate, 2),
            "rating": float(hotel.get("rating", 0)),
            "distance_miles": 0.0,
            "crowd_score": score.total,
            "crowd_reasons": score.crowd_reasons,
        })
    results.sort(key=lambda x: x["crowd_score"])
    return results


def _get_hotel_details(inp: dict, clients: dict) -> dict:
    details = clients["tripadvisor"].get_hotel_details(inp["location_id"])
    reviews = clients["tripadvisor"].get_hotel_reviews(inp["location_id"])
    summary = clients["tripadvisor"].summarize_reviews(reviews)
    return {
        "details": details,
        "review_summary": summary,
        "hotel_name": inp.get("hotel_name", ""),
    }


def _find_nearby_destinations(inp: dict, clients: dict) -> list[dict]:
    destinations = clients["geonames"].find_nearby_destinations(
        center_lat=inp["center_lat"],
        center_lng=inp["center_lng"],
        radius_miles=inp["radius_miles"],
    )
    return [d.model_dump() for d in destinations]


def _build_itinerary(inp: dict) -> dict:
    crowd_score = inp.get("crowd_score", 50.0)
    crowd_level = "low" if crowd_score < 35 else "medium" if crowd_score < 60 else "high"
    return {
        "destination": inp["destination"],
        "dates": f"{inp['checkin_date']} to {inp['checkout_date']}",
        "crowd_level": crowd_level,
        "itinerary_prompt": (
            f"Create a detailed low-crowd itinerary for {inp['destination']} "
            f"from {inp['checkin_date']} to {inp['checkout_date']}. "
            f"The area has a crowd score of {crowd_score:.0f}/100 ({crowd_level} crowds). "
            "Include: (1) Quieter lodging zones away from the tourist center, "
            "(2) Less-busy attractions with early morning or weekday visit windows, "
            "(3) Local restaurants 10+ minutes from the main tourist strip, "
            "(4) Scenic alternatives to the most-visited sites, "
            "(5) Specific timing tips to avoid peak hours."
        ),
    }


    _static_reviews_client: StaticReviewsClient | None = None


    def _get_static_reviews_client() -> StaticReviewsClient:
        """Lazy-load the static reviews client (CSV read once, cached for session)."""
        global _static_reviews_client
        if _static_reviews_client is None:
            _static_reviews_client = StaticReviewsClient()
        return _static_reviews_client


    def _search_reviews(inp: dict) -> dict:
        client = _get_static_reviews_client()
        if not client.is_available:
            return {
                "available": False,
                "message": (
                    "Static review dataset not loaded. "
                    "Download tripadvisor_hotel_reviews.csv via kagglehub and place in data/. "
                    "See data/README.md for instructions."
                ),
            }
        sentiment = inp.get("sentiment", "low_crowd")
        limit = min(int(inp.get("limit", 5)), 10)
        if sentiment == "low_crowd":
            results = client.search_low_crowd_reviews(limit=limit)
            label = "quiet / uncrowded (4-5 star reviews)"
        elif sentiment == "high_crowd":
            results = client.search_high_crowd_reviews(limit=limit)
            label = "crowded / noisy (1-3 star reviews)"
        else:
            keywords = inp.get("keywords", [])
            if not keywords:
                return {"error": "keywords list is required when sentiment='custom'"}
            results = client.search_by_keywords(keywords=keywords, limit=limit)
            label = f"custom keywords: {keywords}"
        return {
            "sentiment_searched": label,
            "total_dataset_reviews": client.total_reviews,
            "results_returned": len(results),
            "reviews": results,
        }
