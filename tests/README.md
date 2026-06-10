# tests/

pytest test suite covering all major modules. Tests are organized by module and follow
the same TDD pattern used throughout the project (write failing test → implement → pass).

## Files

| File | What it tests | Key assertions |
|---|---|---|
| `test_models.py` | Pydantic data models (`UserPreferences`, `HotelResult`, etc.) | Crowd score thresholds, preference matching, field validation |
| `test_memory.py` | `SessionMemory` class | Preference storage/retrieval, conversation history, filter application |
| `test_crowd_scorer.py` | `calculate_crowd_score()` and `explain_crowd_factors()` | Score always 0–100, correct weight contributions, reason text generation |
| `test_clients.py` | All 5 API clients (mocked) | HTTP calls made correctly, response parsing, fallback behavior |
| `test_agent.py` | Tool schemas, `dispatch_tool()`, `EcoTravelAgent._is_in_scope()` | Tools have required keys, dispatch routes correctly, scope guard rejects/accepts correctly |
| `__init__.py` | Package marker | — |

## Running tests

```powershell
# Run all tests with verbose output
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_crowd_scorer.py -v

# Run a single test by name
python -m pytest tests/test_agent.py::test_agent_rejects_non_travel_query -v
```

## Expected results

All tests should pass. A clean run looks like:

```
tests/test_models.py         ......    6 passed
tests/test_memory.py         ....      4 passed
tests/test_crowd_scorer.py   ......    6 passed
tests/test_clients.py        ............  12 passed
tests/test_agent.py          ........  8 passed
```

## Notes

- API client tests use `unittest.mock.patch` — no real API keys needed to run tests.
- `test_clients.py` for `geonames.py` uses a tiny in-memory city list, not the full `cities500.txt`.
- If you add a new client or tool, add corresponding tests before submitting.
