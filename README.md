# Coding Agent

A simple coding agent built with Claude that can view/edit files, search the web, and execute bash commands—all in ~200 lines.

You can find an interactive version at https://claude-codes.replit.app

```mermaid
flowchart TD
   Start([Start]) --> UserInput[Get User Input]
   UserInput --> Claude[Send to Claude]
   Claude --> NeedsTools{Needs Tools?}

   NeedsTools -->|No| ShowResponse[Show Response]
   NeedsTools -->|Yes| ExecuteTools[Execute Tools]

   ExecuteTools --> SendResults[Send Results to Claude]
   SendResults --> Claude

   ShowResponse --> UserInput

   ExecuteTools -.-> Tools
```

## Quick start

1. **Create virtual environment and install dependencies**:
   ```bash
   # Option 1: uv installed
   uv venv
   source .venv/bin/activate # On Windows: .venv\Scripts\activate
   uv sync

   # Option 2: Without uv
   python3 -m venv .venv
   source .venv/bin/activate # On Windows: .venv\Scripts\activate
   pip3 install uv
   uv sync
   ```

2. **Setup environment & add API key**:
   ```bash
   cp .env.example .env
   ```
   Be sure to add your API key!

3. **Run the CLI agent**:
   ```bash
   uv run simple_agent.py
   ```

4. **Or run the interactive notebook**:
   ```bash
   # To run
   marimo run notebook.py

   # To edit
   marimo edit notebook.py
   ```

Note: `uv` and an appropriate virtualenv are prerequisites—our agent will use uv to execute Python scripts

## What it does

- **Fix broken files**: `"can you help me fix broken_file.py?"`
- **Research and implement**: `"research new Python 3.13 features and write a file that demonstrates a simple example"`
- **Create new code**: `"write a simple tip splitting calculator Python file"`

## Architecture

The agent uses a simple loop:
1. Get user input
2. Send to Claude with tools (file editor, web search, bash)
3. Execute any requested tools
4. Return results and repeat

## Files

- `simple_agent.py` - CLI version
- `notebook.py` - Interactive Marimo notebook with documentation
- `public/instructions.md` - System prompt and instructions

## Requirements

- Python 3.13+
- Anthropic API key