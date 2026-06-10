# src/tools/

Claude tool definitions and dispatch handler. This is the bridge between the LLM's
`tool_use` decisions and the actual API clients.

## Files

| File | Purpose |
|---|---|
| `agent_tools.py` | `TOOL_DEFINITIONS` list (JSON schemas Claude reads) + `dispatch_tool()` router |
| `__init__.py` | Package marker |

## The 4 tools

| Tool name | What Claude can ask it to do |
|---|---|
| `search_hotels` | Search TripAdvisor hotels at a location for given dates, score each result, return sorted list |
| `get_hotel_details` | Fetch full details + summarized guest reviews for a specific hotel by `location_id` |
| `find_nearby_destinations` | Find towns within a radius sorted by distance, tagged with crowd indicator |
| `build_itinerary` | Generate a structured low-crowd itinerary prompt for a chosen destination and dates |

## How dispatch works

```
Claude returns tool_use block
        ↓
dispatch_tool(tool_name, tool_input, clients)
        ↓
_search_hotels / _get_hotel_details / ...
        ↓
API clients → crowd scorer → normalized dict
        ↓
Returned to Claude as tool_result
```

`dispatch_tool()` wraps every call in `try/except` so a failed API call returns a
descriptive error string to Claude rather than crashing the loop.

## Adding a new tool

1. Add a JSON schema entry to `TOOL_DEFINITIONS` in `agent_tools.py`.
2. Add a corresponding `elif tool_name == "your_tool":` branch in `dispatch_tool()`.
3. Implement the private `_your_tool(inp, clients)` function below.
4. Add tests to `tests/test_agent.py`.
