# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a coding agent demonstration project that shows how to build an AI coding assistant using Anthropic's Claude with less than 200 lines of code. The project implements an agent that can view/edit files, search the web, and execute bash commands.

## Core architecture

The project consists of two main implementations:

- **`simple_agent.py`**: CLI version of the coding agent with a command-line interface
- **`notebook.py`**: Marimo notebook version that provides an interactive web interface and documentation

Both implementations follow the same core pattern:
1. **Agent Loop**: Continuous while loop handling user input
2. **Tool Execution**: Local tool router (`execute_tool()`) that handles file operations and bash commands
3. **Message Management**: Anthropic API integration with proper tool use and caching

### Key components

- **Tool Router**: The `execute_tool()` function routes between file operations (`view`, `create`, `str_replace`) and bash commands
- **Prompt Caching**: Uses ephemeral caching on system prompts and initial instructions for cost optimization
- **Error Handling**: Structured error responses following Anthropic's `is_error` flag pattern

## Development commands

### Running the agents
```bash
# Run CLI agent (requires ANTHROPIC_API_KEY in .env)
uv run simple_agent.py

# Run Marimo notebook interface
uv run marimo run notebook.py
```

### Dependencies management
```bash
# Install dependencies
uv sync

# Add new dependencies
uv add package-name
```

### Python execution
- Always use `uv run` instead of `python` for execution (as specified in public/instructions.md)
- Project requires Python >=3.13

## Environment setup

Required environment variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `ANTHROPIC_MODEL`: Optional, defaults to "claude-sonnet-4-0"

Create a `.env` file in the project root with these variables.

## File structure

- `public/instructions.md`: System prompt and instructions for the agent
- `public/broken_file.py`: Example broken file for testing agent capabilities
- `public/claude.png`: Logo used in notebook interface
- `layouts/notebook.slides.json`: Notebook layout configuration

## Agent capabilities

The coding agent is designed to:
- Fix broken Python files and validate output
- Research new techniques and implement examples
- Create novel code implementations
- Handle file operations (view, create, edit)
- Execute bash commands with timeout protection
- Search the web for up-to-date information

## Key implementation details

### Prompt structure
- Uses XML tags for structured prompts (`<role>`, `<thinking_process>`, `<instructions>`)
- Separates system prompt (role) from user instructions for better performance
- Implements chain-of-thought reasoning in `<thinking_process>` blocks

### Tool use best practices
- Parallel tool execution when possible
- Structured error responses with detailed logging
- Timeout protection for bash commands (30s default)
- Proper file path handling with pathlib

### Caching strategy
- Caches tools, system prompt, and first user message
- Uses ephemeral cache control for cost optimization
- Cache window is 5 minutes by default