# src/tracing.py
import os


def traced_chat(agent_instance, user_message: str, run_name: str = "eco-travel-chat") -> str:
    """Wrap agent.chat() in a LangSmith trace when credentials are present, otherwise call directly."""
    langsmith_key = os.environ.get("LANGCHAIN_API_KEY")
    tracing_enabled = os.environ.get("LANGCHAIN_TRACING_V2", "false").lower() == "true"

    if langsmith_key and tracing_enabled:
        from langsmith import traceable
        project = os.environ.get("LANGCHAIN_PROJECT", "eco-travel-agent")

        @traceable(name=run_name, project_name=project)
        def _inner(message: str) -> str:
            return agent_instance.chat(message)

        return _inner(user_message)

    return agent_instance.chat(user_message)
