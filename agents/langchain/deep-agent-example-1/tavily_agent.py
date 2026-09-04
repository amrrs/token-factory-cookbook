# Install required Python packages

* **langchain-nebius** — LangChain integration for accessing models powered by Nebius Token Factory.
* **langchain-tavily** — LangChain integration for Tavily Search, enabling the agent to perform web research.
* **tavily-python** — Tavily's Python SDK, used by the Tavily search integration.
* **deepagents** — Framework for building Deep Agents with planning, tool use, and research capabilities.
* **langchain** — Core LangChain framework used to connect models, tools, and agent components.
* **langchain-core** — Core LangChain abstractions and interfaces used by Deep Agents and tools.
* **openai** — OpenAI-compatible Python SDK for connecting directly to Nebius Token Factory APIs (optional).
"""

!pip install -q -U \
    deepagents \
    langchain \
    langchain-core \
    langchain-nebius \
    langchain-tavily \
    tavily-python

"""# Setup the Environment Variables from Nebius Token Factory and Tavily"""

import os;
os.environ['NEBIUS_API_KEY'] = 'v1.xxx'
os.environ['TAVILY_API_KEY']='tvly-dev-2fLsjb-'

"""# Import the Required Libraries"""

from deepagents import create_deep_agent
from langchain_nebius import ChatNebius
from langchain_tavily import TavilySearch
import json

"""# Tavily Configuration"""

tavily_search = TavilySearch(
    max_results=5,
    search_depth="advanced",
)

"""# Nebius Token Factory model

"""

model = ChatNebius(
    model="MiniMaxAI/MiniMax-M3"
)

"""# Create a Tavily-powered Deep Agent

"""

agent = create_deep_agent(
    model=model,
    tools=[tavily_search],
)

"""# Deep Research and Result"""

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "Research GPUs available in the US in 2026 and write a detailed report."
        }
    ]
})

print(json.dumps(result, indent=2, default=str))

"""# Final Result"""

print(result["messages"][-1].content)
