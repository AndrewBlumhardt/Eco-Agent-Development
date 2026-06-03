# tests/test_agent.py
import pytest
from unittest.mock import MagicMock
from src.tools.agent_tools import TOOL_DEFINITIONS, dispatch_tool


def test_all_tool_definitions_have_required_keys():
    required = {"name", "description", "input_schema"}
    for tool in TOOL_DEFINITIONS:
        missing = required - set(tool.keys())
        assert not missing, f"Tool '{tool.get('name')}' missing: {missing}"


def test_all_tool_input_schemas_have_required_fields():
    for tool in TOOL_DEFINITIONS:
        schema = tool["input_schema"]
        assert schema.get("type") == "object"
        assert "properties" in schema


def test_dispatch_search_hotels_calls_tripadvisor():
    mock_ta = MagicMock(search_hotels=MagicMock(return_value=[]))
    mock_amadeus = MagicMock(
        search_hotel_offers=MagicMock(return_value=[]),
        estimate_availability_pct=MagicMock(return_value=50.0)
    )
    mock_events = MagicMock(get_event_magnitude=MagicMock(return_value=(0.2, [])))
    mock_weather = MagicMock(get_weather_suitability=MagicMock(return_value=0.7))
    clients = {
        "tripadvisor": mock_ta, "amadeus": mock_amadeus,
        "events": mock_events, "weather": mock_weather, "geonames": MagicMock()
    }
    result = dispatch_tool(
        tool_name="search_hotels",
        tool_input={
            "location": "Austin, TX", "checkin_date": "2026-07-15",
            "checkout_date": "2026-07-18", "radius_miles": 25,
        },
        clients=clients,
    )
    mock_ta.search_hotels.assert_called_once()
    assert isinstance(result, list)


def test_dispatch_unknown_tool_returns_error():
    result = dispatch_tool(tool_name="nonexistent", tool_input={}, clients={})
    assert "error" in str(result).lower()
