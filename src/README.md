# src/

Core Python package for the EcoTravel Agent. All application logic lives here.

## Files

| File | Purpose |
|---|---|
| `agent.py` | Main agent orchestrator — Claude tool-use loop, scope guard, session memory wiring |
| `memory.py` | `SessionMemory` class — stores user preferences, applies budget/crowd filters to results |
| `models.py` | Pydantic v2 data models shared across the whole package |
| `tracing.py` | LangSmith `traced_chat()` wrapper — wraps any agent call with a named trace |
| `__init__.py` | Package marker |

## Subpackages

| Folder | Contents |
|---|---|
| `clients/` | One module per external API (TripAdvisor, Amadeus, weather, events, GeoNames) |
| `scoring/` | Crowd score calculation engine |
| `tools/` | Claude tool schemas and dispatch handler |

## Key design decisions

- `agent.py` owns the full Claude `messages` loop and handles `tool_use` blocks by calling `dispatch_tool()`.
- `SessionMemory` is injected into every tool call so all results are filtered against user preferences before being returned to Claude.
- `tracing.py` is a thin wrapper — swap LangSmith for any other tracing provider without touching agent logic.
