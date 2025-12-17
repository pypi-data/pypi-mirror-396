# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastroAI is a lightweight AI orchestration library built on PydanticAI. It provides production-ready primitives for building AI applications with automatic cost tracking, DAG-based pipelines, and distributed tracing.

## Development Commands

```bash
# Install dependencies (uses uv package manager)
uv sync

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_agent.py

# Run a specific test
uv run pytest tests/test_agent.py::TestAgentConfig::test_default_values

# Type checking
uv run mypy fastroai

# Linting and formatting
uv run ruff check .
uv run ruff format .
```

## Architecture

### Core Components

**FastroAgent** (`fastroai/agent/agent.py`): Stateless wrapper around PydanticAI's Agent. Adds automatic cost calculation in microcents, distributed tracing integration, and consistent ChatResponse format. Supports both `run()` for single responses and `run_stream()` for streaming. Accepts custom PydanticAI agents via escape hatch.

**Pipeline** (`fastroai/pipelines/pipeline.py`): DAG-based workflow orchestration. Steps declare dependencies, and the executor (`executor.py`) automatically runs independent steps in parallel. Uses `BaseStep` abstract class for step implementations. Supports early termination via `ConversationStatus.INCOMPLETE`.

**@safe_tool** (`fastroai/tools/decorators.py`): Decorator for production-safe AI tools. Adds timeout, exponential backoff retry, and graceful error handling - returns error messages instead of raising exceptions so the AI can handle failures.

**CostCalculator** (`fastroai/usage/calculator.py`): Calculates token costs using integer microcents (1/1,000,000 dollar) to avoid floating-point precision errors in billing. Includes `DEFAULT_PRICING` dict for major models (OpenAI, Anthropic, Google, Groq).

**Tracer Protocol** (`fastroai/tracing/tracer.py`): Protocol-based tracing interface for observability integration. Includes `SimpleTracer` for logging-based tracing and `NoOpTracer` for testing.

### Pipeline Step Pattern

Steps extend `BaseStep[DepsT, OutputT]` and implement `execute(context: StepContext[DepsT]) -> OutputT`:
- Access pipeline inputs via `context.get_input("key")`
- Access dependency step outputs via `context.get_dependency("step_id", Type)`
- Access application deps (db session, user, etc.) via `context.deps`

### Key Design Decisions

- **Stateless agents**: Conversation history is caller-managed, not stored in agent
- **Microcents for billing**: Integer arithmetic prevents precision errors
- **Protocol-based tracing**: Implement `Tracer` protocol for any observability backend
- **Type-safe contexts**: Generic types flow through pipeline steps

## Testing

Tests use `pytest-asyncio` with `asyncio_mode = "auto"`. Mock PydanticAI agents using `model="test"` or `TestModel()`. Strict mypy is disabled for test files.
