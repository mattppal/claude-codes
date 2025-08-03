# Coding Agent

A simple coding agent built with Claude that can view/edit files, search the web, and execute bash commands—all in ~200 lines.

You can find an interactive version at https://claude-codes.replit.app

## Quick start

1. **Create virtual environment and install dependencies**:
   ```bash
   # Option 1: uv (recommended)
   uv venv
   source .venv/bin/activate # On Windows: .venv\Scripts\activate
   uv sync

   # Option 2: Poetry
   python -m venv .venv
   source .venv/bin/activate # On Windows: .venv\Scripts\activate
   pip install poetry && poetry install

   # Option 3: Standard venv + pip
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

2. **Setup environment & add API key**:
   ```bash
   cp .env.example .env
   ```

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

## What it does

- **Fix broken files**: `"fix broken_file.py"`
- **Research and implement**: `"research new Python 3.13 features and write an example"`
- **Create new code**: `"write a tip splitting calculator"`

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

## Technical approach and key architectural decisions

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

My goal was to create the simplest agent I could that was able to create, edit, and test files.

For that reason, I opted for a simple loop with a tool handler function. For a more complex agent, I'd likely take
an object-oriented approach.

## Why this demonstration

I work for an agentic coding startup. Everyone hears about agentic coding and its almost guaranteed
that devs working with the anthropic api have some access to tools like Claude Code. 

Thus, it's a tool devs use everyday—but how many know how it works?

More than that, how many know that you can implement an agent that edits code in ~200 lines?

## How this helps developers understand Claude's potential

This demo bridges the gap between the tools we use everyday and how they can be built with claude

There's an appreciation for a tool you get when you understand how it works.

Moreover, there's a common misconception that an agentic framework is a prerequisite to starting a project.



## What makes builders want to learn more

The "wow" moment of prompting an agent and seeing it edit a file.

The attention to detail

## How Claude was used in creating this demo

## Future improvements