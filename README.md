# Coding agent

A simple coding agent built with Claude that can view/edit files, search the web, and execute bash commands—all in ~200 lines.

You can find an interactive version at <https://claude-codes.replit.app>

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

The agent follows a straightforward pattern with three core components:

### Prompt structure

```xml
<role>
You are an expert software engineering assistant...
</role>

<thinking_process>
Before taking any action, think through the problem step by step...
</thinking_process>

<instructions>
When working with code:
1. Understanding First: Always examine existing files...
2. Targeted Changes: Use precise `str_replace` operations...
</instructions>
```

**Best practices:**

- Split system prompt (role) from user instructions for better caching
- Use XML tags for structured prompts and interpretability  
- Include chain-of-thought reasoning with `<thinking_process>` blocks
- Cache tools, system prompt, and first user message for cost optimization

### Tool execution router

```python
def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """Execute a tool and return structured result with error handling."""
    try:
        if tool_name == "view":
            # Handle file/directory viewing
        elif tool_name == "str_replace":
            # Handle targeted file edits
        elif tool_name == "bash":
            # Handle command execution with timeout
        # ...
    except Exception as e:
        return {"content": f"Error: {str(e)}", "is_error": True}
```

**Best practices:**

- Return structured responses with `is_error` flag for Claude
- Use proper timeout protection (30s default for bash)
- Include detailed error logging and handling
- Support both file operations and bash commands

### Agent loop

```python
while True:
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        system=[{"type": "text", "text": system_prompt}],
        messages=messages,
        tools=ANTHROPIC_TOOLS,
    )
    
    if response.stop_reason == "tool_use":
        # Execute tools in parallel when possible
        # Return results to Claude for continued processing
    else:
        # Handle final response
        break
```

**Best practices:**

- Handle all stop reasons robustly (tool_use, end_turn, etc.)
- Execute multiple tools in parallel when possible
- Maintain conversation state through message history
- Use low temperature (0.2) for consistent, focused responses

## Files

- `simple_agent.py` - CLI version
- `notebook.py` - Interactive Marimo notebook with documentation
- `public/instructions.md` - System prompt and instructions

## Requirements

- Python 3.13+
- Anthropic API key
