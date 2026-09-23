# Nebius Token Factory : Start Here

## Table of Contents

- [0 - Sign up](#0-sign-up)
- [1 - Try the UI](#1---try-the-ui)
- [2 - Your first API call](#2---your-first-api-call)
- [3 - Building Your First Agents](#3---building-your-first-agents)
- [4 - Understanding Agentic Operations and Cost](#4---understanding-agentic-operations-and-cost)
- [5 - Deep Research Agents](#5---deep-research-agents)
- [6 - Coding with Token Factory Models](#6---coding-with-token-factory-models)
- [7 - Build a fun app / demo with your coding agent](#7---build-a-fun-app--demo-with-your-coding-agent)
- [8 - Collect Production logs using Data Lab](#8---collect-production-logs-using-data-lab)
- [9 - Post training your models](#9---post-training-your-models)

## 0 - Sign up

- Sign up at https://tokenfactory.nebius.com
- If you have credits, apply them. [how to video](https://www.youtube.com/watch?v=YKY6k6kSDZY)
- Get your API key

## 1 - Try the UI
https://tokenfactory.nebius.com/

- Take a model for a spin.
- Compare model outputs

## 2 - Your first API call

[api call](../api/README.md)

## 3 - Building Your First Agents

**Simple research agent**

Try [simple research agent](../agents/langchain/deep-agent-example-1/research_agent_1.py).  This  agent will only use built in knowledge.

Follow instructions from [this project](../agents/langchain/deep-agent-example-1/README.md).  


**Tavily powered agent**

In the same example, we have a [research agent powered by Tavily](../agents/langchain/deep-agent-example-1/tavily_agent.py).  It will use web search in real time to fetch results.

Run them both and compare the resulting outputs.

Note: Using Tavily Agent will require TAVILY_API_KEY.  You can get a free one here : https://app.tavily.com/

## 4 - Understanding Agentic Operations and Cost

How many turns does it take for an agent to accomplish a task?  How much does it cost?

Try this [example](../agents/agent-cost-comparison-1/)

## 5 - Deep Research Agents

Here are couple of examples of **deep research agents** 

- [competitive research agent](../agents/langchain/competitive-intelligence-agent/) - built with Tavily + Langchain + Token Factory
- [pr review bot](../agents/langchain/pr-review-bot/)

## 6 - Coding with Token Factory Models

Connect your coding agent (claude, codex, opencode .etc) with models running on Token Factory.

[Here is the guide](../coding/README.md)

## 7 - Build a fun app / demo with your coding agent

Browse [Cool Apps / Demos](../apps/README.md) for inspiration, then build your own.

---

## Advanced

## 8 - Collect Production logs using Data Lab

[Turn your production logs into training data](../workshops/token-factory-workshop/collecting-production-logs.md)

## 9 - Post training your models

- [fine tuning example](../post-training/fine-tuning-1)
- [distillation example](../distillation/distillation-1)
