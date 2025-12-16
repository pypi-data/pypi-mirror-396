"""
ZENTAXA Python SDK
==================

Agent Observability & Debugging Platform SDK.
The flight recorder for multi-agent LLM systems.

Quick Start (≤3 lines):
    from zentaxa import observe_agent, start_session

    session = start_session(project="my-agent")
    
    @observe_agent(session=session, agent="planner")
    def plan(input_data):
        return "plan output"

Framework Integrations:
    from zentaxa import ZentaxaClient
    from zentaxa.integrations.langchain import ZentaxaCallbackHandler
    
    client = ZentaxaClient()
    handler = ZentaxaCallbackHandler(client=client, agent_id="my-agent")
    llm = ChatOpenAI(callbacks=[handler])

Supported Frameworks:
  - LangChain / LangGraph
  - CrewAI
  - AutoGen
  - LlamaIndex

Installation:
    pip install zentaxa

Version: 1.1.0
"""

from .client import ZentaxaClient
from .session import (
    Session,
    start_session,
    observe_agent,
    observe_tool,
    Event,
)

__version__ = "1.1.0"
__all__ = [
    "ZentaxaClient",
    "Session",
    "start_session",
    "observe_agent",
    "observe_tool",
    "Event",
]

# Lazy loading for framework integrations - import only when needed
def __getattr__(name):
    if name == "ZentaxaCallbackHandler":
        from .integrations.langchain import ZentaxaCallbackHandler
        return ZentaxaCallbackHandler
    elif name == "LangGraphObserver":
        from .integrations.langgraph import LangGraphObserver
        return LangGraphObserver
    elif name == "CrewAIObserver":
        from .integrations.crewai import CrewAIObserver
        return CrewAIObserver
    elif name == "AutoGenTracer":
        from .integrations.autogen import AutoGenTracer
        return AutoGenTracer
    elif name == "LlamaIndexObserver":
        from .integrations.llamaindex import LlamaIndexObserver
        return LlamaIndexObserver
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
