# src/agent.py
import os
import anthropic
from src.memory import SessionMemory
from src.models import UserPreferences
from src.tools.agent_tools import TOOL_DEFINITIONS, dispatch_tool
from src.clients.tripadvisor import TripAdvisorClient
from src.clients.amadeus import AmadeusClient
from src.clients.weather import WeatherClient
from src.clients.events import EventsClient
from src.clients.geonames import GeoNamesClient

SYSTEM_PROMPT = """You are EcoTravelAgent, a travel assistant that specializes in finding
low-crowd hotel destinations. You help users avoid over-touristed areas by analyzing hotel
availability, local events, pricing, and weather to produce crowd likelihood scores.

You ONLY assist with:
- Finding hotels and accommodations
- Assessing crowd levels at destinations
- Suggesting nearby low-crowd alternatives
- Building low-crowd itineraries for chosen destinations
- Explaining why an area may be crowded (limited rooms, price spikes, festivals,
  holiday weekends, cruise ship arrivals, limited attraction availability)

Gracefully reject any request unrelated to travel accommodation and destination planning.
When rejecting, briefly explain what you can help with.

At the start of a session (when no preferences are set), collect:
1. Approximate nightly budget in USD
2. Preferred weather (warm / cool / mild / any)
3. Maximum drive distance from destination center (15, 25, 50, or 100 miles)
4. Crowd tolerance (low / medium / high)

After preferences, ask for: destination, check-in date, check-out date.
Always present hotel results sorted by crowd score (lowest first) in a clear table format.
Lower crowd score = less crowded. A score below 35 is excellent.
"""

IN_SCOPE_TERMS = {
    "hotel", "motel", "inn", "stay", "book", "reservation", "destination", "travel",
    "trip", "vacation", "crowd", "lodging", "accommodation", "check-in", "checkout",
    "nearby", "itinerary", "visit", "explore", "beach", "mountain", "city", "town",
    "area", "resort", "airbnb", "room", "suite", "night", "weekend", "getaway",
}


class EcoTravelAgent:
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model
        self.memory = SessionMemory()
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._tool_clients = {
            "tripadvisor": TripAdvisorClient(os.environ["TRIPADVISOR_API_KEY"]),
            "amadeus": AmadeusClient(
                os.environ["AMADEUS_CLIENT_ID"], os.environ["AMADEUS_CLIENT_SECRET"]
            ),
            "weather": WeatherClient(os.environ["OPENWEATHERMAP_API_KEY"]),
            "events": EventsClient(os.environ["PREDICTHQ_API_KEY"]),
            "geonames": GeoNamesClient(),
        }

    def _is_in_scope(self, user_message: str) -> bool:
        # Check whether the message contains any travel-related keyword
        lower = user_message.lower()
        return any(term in lower for term in IN_SCOPE_TERMS)

    def chat(self, user_message: str) -> str:
        if not self._is_in_scope(user_message):
            return (
                "I can only help with travel accommodation and destination planning — "
                "specifically finding hotels with low crowd levels, suggesting quieter "
                "nearby destinations, explaining crowd causes, and building itineraries. "
                "What destination or travel question can I help you with?"
            )

        self.memory.add_message("user", user_message)
        messages = self.memory.get_conversation_history()

        response = self._client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Handle tool_use stop reason — Claude may call multiple tools before finishing
        while response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = dispatch_tool(block.name, block.input, self._tool_clients)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })
            messages = messages + [
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": tool_results},
            ]
            response = self._client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

        reply = next(
            (block.text for block in response.content if hasattr(block, "text")), ""
        )
        self.memory.add_message("assistant", reply)
        return reply
