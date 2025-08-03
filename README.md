# Coding Agent

A simple coding agent built with Claude that can view/edit files, search the web, and execute bash commands—all in ~200 lines.

You can find an interactive version at https://claude-codes.replit.app

## Quick start

1. **Create virtual environment and install dependencies**:
   ```bash
   # Option 1: uv installed
   uv venv
   source .venv/bin/activate # On Windows: .venv\Scripts\activate
   uv sync

   # Option 2: Without uv
   python -m venv .venv
   source .venv/bin/activate # On Windows: .venv\Scripts\activate
   pip install uv
   uv sync

   # Option 3: I hate uv
   python3 -m venv .venv
   source .venv/bin/activate # On Windows: .venv\Scripts\activate
   pip install -e . 
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

## What it does

- **Fix broken files**: `"can you help me fix broken_file.py?"`
- **Research and implement**: `"research new Python 3.13 features and write a file that demonstrates a simple example"`
- **Create new code**: `"write a simple tip splitting calculator python file"`

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

For that reason, I opted for a loop with a tool handler function. For a more complex agent, I'd likely take
an object-oriented approach.

## Why this demonstration

I work for an agentic coding startup. Everyone hears about agentic coding and it's almost guaranteed
that devs working with the Anthropic API have some access to tools like Claude Code.

It's a tool devs use every day—but how many know how it works? (I didn't)

More than that, many prescribe "magical" properties to LLMs, even some devs.

More than that, how many know that you can implement an agent that edits code in ~200 lines?

As someone who's technically inclined, I often use my intuition to guide what others might be interested in. I can empathize with developers:

- Devs building with Anthropic are likely using AI Agents, some use them every day
- They seem new, cutting edge, and complicated
- At their core, they are simple

This simplicity brings the "wow" and leads the way for learning and understanding. It's grounding to bring practicality to a technology that feels magical.

## How this helps developers understand Claude's potential

This demo bridges the gap between the tools we use every day and how they can be built with Claude.

There's an appreciation for a tool you get when you understand how it works.

Moreover, there's a common misconception that an agentic framework is a prerequisite to starting a project.

Here, we demonstrate how anyone with basic Python knowledge can build an agent with Anthropic. 

There's an audience for technical projects and walkthroughs too, but I think the art of education lies in the simple.

## What makes builders want to learn more

First, the "wow" moment of prompting an agent and seeing it edit a file—this is why I stacked the architecture diagram and example at the top of the file.

These are the hooks, which are then backed up by the code teardown.

Using Marimo, it was possible to build in a chat interface that doesn't require cell execution and host the notebook remotely. This reduces the friction to getting started and engaging with the notebook.

Second, I think presentation is everything—this doesn't feel like another notebook, it feels like something special.

It's the attention to detail that draws the reader in and makes this feel unique and precious. That's what drew me to Anthropic's brand and that's why this is a powerful example.

It's what makes posts like [How to Build an Agent](https://ampcode.com/how-to-build-an-agent) stand out.

Attention to detail in educational assets can't be overlooked.

## How Claude was used in creating this demo

I use Claude for the following:

### Ideation

I relied heavily on Claude Code for ideation. I used this to understand what was possible before digging in.

For example, I explored a hiking tool:

```text
Help me build a very simple agent with access to the following tools:

- web search
- an open streetmap tool for finding trails.

I should be able to send a prompt like "find trails within 10mi of san francisco".

This requires:
- A geocoding tool to convert a location to coordinates
- An OSM tool for looking up details

You should do research on the Overpass API for OSM.

It should use best practices in the Anthropic API. We should use the Anthropic API and only the API.

Keep the app hyper-minimalist and use the simplest implementation possible
```

Eventually, I turned this into another mini-app that was capable of plotting the GeoJSON.

This could be another interesting project. 

The main point is that I can start with something that works, then tear it down to understand concepts.

This is often how I approach learning.

Through the process of iterating on this project, I was able to understand the API,
then present them in a way for others to understand.

### Background research and summarization

I have never built an agent with solely the Anthropic SDK. There are many nuances and intricacies to the API that are not immediately obvious.

I have plenty of feedback for Anthropic's docs. 

The following prompts were useful in understanding the structure and some talking points:

```text
https://docs.anthropic.com

Do research on the Anthropic documentation. Help me understand best practices for building coding agents. What are some useful resources I could explore to learn more?
```

```text
https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

Help me understand prompt caching. I'd like to know what is cached and when. Can you provide a sample implementation?
```

```text
https://docs.marimo.io/guides/state/

I'm trying to understand Marimo state. How can I automatically update state in code? For example, I want to update a variable in a code block and update the state to match so I can visualize the value changing
```

There were many other similar prompts to Claude for explanation, search, and information retrieval.

#### Vibe coding

This app was heavily vibe coded to start. As discussed in [Ideation](#ideation), vibe coding can be a good tool for learning.

Once I knew I wanted to build a coding agent, I vibe coded a sample implementation.

The code was an absolute mess and very weird.

I then rewrote the structure of the app, once I understood enough about the API to have a
reasonable opinion on how it should be written.

I find a good pattern for building out more sensible apps is to leave `#TODO`'s throughout the code, then have Claude
fill them in.

For example, writing pseudo-code or the code's structure, then prompting function by function to fill in the details.

It's this focus of being hyper-specific that often yields the best results in projects that are being showcased externally.

I also took inspiration from [examples](https://github.com/anthropics/anthropic-cookbook/blob/main/tool_use/calculator_tool.ipynb) online.

Vibe coding is all about context management and being specific.

#### Checks and refactoring

I also used Claude for all tedium related to refactoring code and doing final checks.

I feel it's important to personally write all content, since my voice is not easily replicated by AI.

In other projects, I have a series of prompts that I'll chain through `@` for writing, but it's still not truly representative for important work.

I used prompts for the following:

- Formatting: `Ensure all headers are sentence case and list items do not end in periods`
- Spell checks: `Please iterate through all markdown blocks in @notebook and check spelling`
- Moving `simple_agent.py` into `notebook.py`: `Help me adapt @simple_agent.py to a Marimo notebook, here is the marimo documentation: https://docs.marimo.com`
  - More complex Marimo functionality: `We need to implement state handling for our Marimo chat, here are the docs: https://docs.marimo.io/api/inputs/chat/`
- Adapting the notebook to work with our agent

## Future improvements

This is not a complex app. 

That's sort of the point, but there are a number of interesting areas that could be explored further:

1. Implement more robust stop reason handling, retry logic, and try / except blocks
2. Implement streaming for more responsive messages
3. Turn our simple agent into a [_Multi-agent Architecture_](https://www.anthropic.com/engineering/built-multi-agent-research-system) with Opus as an [orchestrator](https://github.com/anthropics/anthropic-cookbook/blob/main/patterns/agents/orchestrator_workers.ipynb) and Haiku for lightweight tasks
4. Play with [remote code execution](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/code-execution-tool) for a sandboxed approach
5. [Reduce latency](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-latency) in our responses
6. The [evaluation / optimizer](https://github.com/anthropics/anthropic-cookbook/blob/main/patterns/agents/evaluator_optimizer.ipynb) pattern seems interesting as well