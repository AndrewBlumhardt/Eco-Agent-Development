# src/clients/

One module per external data source. Each client wraps API calls, handles auth, and returns normalized Python dicts or Pydantic model instances.

## Files

| File | API | What it fetches | Free tier |
|---|---|---|---|
| `tripadvisor.py` | TripAdvisor Content API v2 | Hotel search results, ratings, and guest reviews | 5,000 calls/month |
| `amadeus.py` | Amadeus Hotel Search API (sandbox) | Room availability percentage and nightly pricing | Free sandbox |
| `weather.py` | OpenWeatherMap 5-day forecast API | Weather forecast; returns a 0–1 suitability score | 1,000 calls/day |
| `events.py` | PredictHQ Events API | Local events (festivals, concerts, sports); returns a 0–1 magnitude score | Free trial |
| `geonames.py` | GeoNames `cities500.txt` (local file) | Nearby cities within a radius sorted by distance; derives crowd indicator from population | No API key needed |
| `__init__.py` | — | Package marker | — |

## Adding a new client

1. Create `src/clients/yourclient.py` with a class that takes API credentials in `__init__`.
2. Add a corresponding test block to `tests/test_clients.py`.
3. Wire the client into `src/tools/agent_tools.py` under `_tool_clients`.
4. Add the API key to `.env.example` and `Instructions.txt`.

## Notes

- `geonames.py` reads from `data/cities500.txt` at startup. Download it once — see [data/README.md](../../data/README.md).
- Amadeus sandbox may return empty results for some destinations. The crowd scorer uses a fallback availability value of 45% when no Amadeus data is available.
- All clients raise `requests.HTTPError` on bad API responses — `dispatch_tool()` catches these and returns a user-friendly error string to Claude.
