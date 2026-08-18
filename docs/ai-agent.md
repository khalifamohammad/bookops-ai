# BookOps AI — AI Agent

## Overview

BookOps AI uses LangChain and LangGraph to organize booking analysis and daily business summaries.

The AI layer is integrated directly into the FastAPI backend.

Production currently runs:

- LangChain 1.x
- LangGraph 1.x

The system does not require a paid hosted LLM to operate. The workflows are deterministic and structured, which keeps the project reliable while still demonstrating agent orchestration with LangGraph and LangChain tools.

---

## Booking Analysis Graph

The booking analysis workflow is implemented as a LangGraph StateGraph.

Flow:

```text
START
  ↓
Assess Priority
  ↓
Detect Conflict
  ↓
Recommend Upsell
  ↓
Compose Confirmation
  ↓
Persist Booking Analysis
  ↓
END
