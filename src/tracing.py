# src/tracing.py
import os
from langsmith import traceable


def traced_chat(agent_instance, user_message: str, run_name: str = "eco-travel-chat") -> str:
    """Wrap agent.chat() in a LangSmith trace."""
    project = os.environ.get("LANGCHAIN_PROJECT", "eco-travel-agent")

    @traceable(name=run_name, project_name=project)
    def _inner(message: str) -> str:
        return agent_instance.chat(message)

    return _inner(user_message)
