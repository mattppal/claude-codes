import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium", app_title="✴ Claude Code(s)")


@app.cell
def _():
    import marimo as mo
    import subprocess
    from pathlib import Path
    import os
    from dotenv import load_dotenv

    import anthropic

    return Path, anthropic, load_dotenv, mo, os, subprocess


@app.cell(hide_code=True)
def _(mo):
    intro_paragraph = mo.md(
        r"""
    # <img src="public/claude.png" style="display: inline; max-height: 50px; margin: 0; border-radius: 0;" /> Claude Code(s)

    There are many coding agents, but how do they work? 

    Surely, they must be complicated...

    As it would turn out, all you need for an agent is: an LLM, a loop, and some tools.

    This is a notebook demonstarting how to build a coding agent with web search & code execution in less than 200 lines—the only external dependency being `anthropic`. 

    Our agent will be able to 

    - View and edit files (Create and modify code)
    - Search the web
    - Execute bash commands (Test and run files)

    This notebook is adapted from the `simple_agent.py` file in the root directory of this project.
    """
    )

    intro_flowchart = mo.mermaid(
        """
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
    """
    )

    mo.hstack(
        [
            intro_paragraph.style({"max-width": "750px", "overflow-wrap": "normal"}),
            intro_flowchart,
        ],
        widths=[1.25, 1],
    )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Jumping in

    Normally, tools are defined using a [JSON schema](https://json-schema.org/), for example a web search implementation might look like:

    ```python
    def web_search(topic):
        print(f"pretending to search the web for {topic}")

    web_search_tool = {
        "name": "web_search",
        "description": "A tool to retrieve up to date information on a given topic by searching the web",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to search the web for"
                },
            },
            "required": ["topic"]
        }
    }
    ```

    We'll use tools built-in to Claude, which don't require JSON schema definitions, but do have a few other charateristics
    """
    )
    return


@app.cell
def _(mo):
    intro_tool_text = mo.md(
        f"""
    ## Init

    Claude comes with a set of predefined tools that require much shorter definitions: [_Text Editor_](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/text-editor-tool), [_Web Search_](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/web-search-tool), and [_Bash_](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/bash-tool). 

    As it would turn out, those are the only tools we'll need for this demonstration. We start with some imports and tool definitions.

    Setting web search `max_uses` to 5 ensures our agent doesn't enter a research loop (this happens to humans, too).
    """
    )

    imports_code = """
    load_dotenv()

    ANTHROPIC_MODEL = "claude-sonnet-4-0"
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY must be set")

    ANTHROPIC_TOOLS = [
        {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"},
        {"type": "web_search_20250305", "name": "web_search", "max_uses": 5},
        {"type": "bash_20250124", "name": "bash"},
    ]
    """

    mo.hstack(
        [
            intro_tool_text.style({"max-width": "650px", "overflow-wrap": "normal"}),
            mo.ui.code_editor(imports_code, disabled=True).style(
                {"max-width": "650px", "overflow-wrap": "normal"}
            ),
        ],
        widths="auto",
        align="start",
    )
    return


@app.cell
def _(Path, mo):
    prompting = """
    ## Prompting
    Now, we'll take a look at our prompt—it's recommended that the system prompt _only_ contain the [model's role](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts). 

    We split the prompt in our code and load only the `role` tag, the rest is in the first user message.

    Using [best practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices#example-formatting-preferences), for prompts helps with tool execution and reasoning

    ### XML
    We define prompt blocks in XML tags for structure and interpretability by the model.

    This is a best practice that I've found useful in my own projects. A nice side effect
    is that prompts are more human-readible, too.

    ### Context & role

    We build context around the task and clearly define the role of the agent

    ### Instructions

    We use explicit, declarative instructions on exactly how the model should perform a given task.
    This includes the steps the model should take on each turn.

    ### Thinking
    Using the `<thinking_process>` block, we encourage the model to think through each problem.

    This is also known as ["chain of thought"](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought#example-writing-donor-emails-guided-cot). 

    ### Tool use

    We define tool use best practices to ensure parallel tool calls and proper work checking.

    By default, parallel tool use is enabled, but [explicit prompts](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#maximizing-parallel-tool-use) can maximize parallel use.
    """
    prompt = Path("./public/instructions.md").read_text()
    mo.hstack(
        [
            mo.md(prompting).style({"max-width": "650px", "overflow-wrap": "normal"}),
            mo.ui.code_editor(value=prompt, language="xml", disabled=True).style(
                {"max-width": "700px", "overflow-wrap": "normal"}
            ),
        ],
        widths="auto",
        align="start",
    )

    return


@app.cell
def _(Path, subprocess):
    def restore_broken_file():
        if Path("broken_file.py").exists():
            Path("broken_file.py").unlink()
            (
                Path("./broken_file.py").write_text(
                    Path("./public/broken_file.py").read_text()
                )
            )

    def execute_tool(tool_name: str, tool_input: dict) -> dict:
        """Execute a tool and return structured result with error handling."""
        try:
            if tool_name == "view":
                print(f"Executing: {tool_name}")
                path = Path(str(tool_input.get("path")))
                if path.is_file():
                    content = path.read_text()
                    return {"content": content, "is_error": False}
                elif path.is_dir():
                    content = "\n".join(sorted([f.name for f in path.iterdir()]))
                    return {"content": content, "is_error": False}
                else:
                    return {
                        "content": f"Error: {path} does not exist",
                        "is_error": True,
                    }
            elif tool_name == "create":
                print(f"Executing: {tool_name}")
                path = Path(str(tool_input.get("path")))
                content = str(tool_input.get("file_text"))
                if not content:
                    return {
                        "content": "Error: No content provided in file_text parameter",
                        "is_error": True,
                    }
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
                return {
                    "content": f"File {path} written successfully",
                    "is_error": False,
                }
            elif tool_name == "str_replace":
                print(f"Executing: {tool_name}")
                path = Path(str(tool_input.get("path")))
                old_str = str(tool_input.get("old_str"))
                new_str = str(tool_input.get("new_str"))
                if not path.exists():
                    return {
                        "content": f"Error: File {path} does not exist",
                        "is_error": True,
                    }

                content = path.read_text()
                if old_str not in content:
                    return {
                        "content": f"Error: String '{old_str}' not found in {path}",
                        "is_error": True,
                    }

                new_content = content.replace(old_str, new_str, 1)
                path.write_text(new_content)
                return {
                    "content": f"Replaced '{old_str}' with '{new_str}' in {path}",
                    "is_error": False,
                }
            elif tool_name == "bash":
                print(f"Executing: {tool_name}")
                command = tool_input.get("command")
                if not command:
                    return {
                        "content": "Error: No command provided in command parameter",
                        "is_error": True,
                    }
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                output = f"stdout: {result.stdout}\nstderr: {result.stderr}"
                return {"content": output, "is_error": result.returncode != 0}
            else:
                return {
                    "content": f"Error: Unknown tool '{tool_name}'",
                    "is_error": True,
                }
        except Exception as e:
            return {
                "content": f"Error executing {tool_name}: {str(e)}",
                "is_error": True,
            }

    return (execute_tool, restore_broken_file)


@app.cell
def _(Path, mo):

    tool_text = mo.md(
        text="""
    ## Handling Tools
    **An important point:** though we have one server tool (web search) for others we'll still need to execute local operations. 

    This function defines a group of tool actions that we'll give access to our model to execute.

    ### `execute_tool`

    We accept a `tool_name` and `tool_input`, then route tool requests to the appropriate operation. This provides a nice way to implement error and retry logic close to the tool implementations.

    Some best practices when executing tools:

    - Adding an `is_error` [property to the response](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#troubleshooting-errors), which we can then pass to Claude
    - Using proper try / except logic with detailed logging for the agent
    - Ensuring reasonable timeouts for our bash tool

    For this implementation, we only log errors. You could imagine wrapping these `ifs` with retry logic as suitible for your agent.
    """
    )

    split_tool_example = (
        """def execute_tool(tool_name: str, tool_input: dict) -> dict:"""
    )
    split_main = """if __name__ == "__main__":"""

    tool_example = (
        split_tool_example
        + "\n\n"
        + Path("simple_agent.py")
        .read_text()
        .split(split_tool_example)[1]
        .strip()
        .split(split_main)[0]
        .strip()
    )

    mo.hstack(
        [
            tool_text.style({"max-width": "650px", "overflow-wrap": "normal"}),
            mo.ui.code_editor(tool_example, language="python", disabled=True).style(
                {"max-width": "600px", "overflow-wrap": "normal"}
            ),
        ],
        widths=[1, 0],
        align="start",
    )
    return (split_main,)


@app.cell
def _(Path, mo, split_main):
    agent_text = mo.md(
        """
    ## Building an agent
    Now, we'll take a look at our agent:

    /// admonition | Heads up
    We'll inspect code from `simple_agent.py`, which is simpler and easier to follow.
    Code in this notebook has been adapted for Marimo.
    ///

    The agent is a nested `While` that handles different cases.

    First, we initialize the Anthropic client and pass in our tools.
    The temperature is set to a low value to encourage [concise responses](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-latency#2-optimize-prompt-and-output-length).

    ### Caching

    Prompt caching caches the _full prefix_ up to the cache point in the following order: **tools**, **system**, **messages**.

    That means our cache point caches: the system prompt, tool use, & the first message.

    Since this is sent with every message, we get cost savings during the cache window (5m by default)

    ### Stop reasons

    Next, we handle `stop_reasons`, which is the client's way of communicating why the chat ended.

    A best practice is to implement [robust stop reason handling](https://docs.anthropic.com/en/api/handling-stop-reasons).
    We keep handling short for our demo, but we recommend handlign _all_ possible reasons.

    ### Responses

    Now, we loop through responses and check for events: `text`, `tool_use` and `citations` (from our web results).
    These are surfaced to the user _and_ our agent.

    ### Tools

    If tools were requested, we make conditional calls to our executor function by [extracting relevant details](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#handling-results-from-client-tools).

    You might notice our web search handling differs from the string replace & bash tools. That's because web search is a **server** tool with a [different output structure](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#handling-results-from-server-tools).

    ### Response

    We return the results to the client and raise an error if one occurred.

    This `while` loop makes another good structure for top-level retries or error handling logic. 

    We simply raise an execption, but you could imagine some number of more complex iterations. 
    Messages and tool results are tracked through message blocks, returned to the client.
    """
    )

    agent = (
        split_main
        + "\n\n"
        + Path("simple_agent.py").read_text().split(split_main)[1].strip()
    )

    mo.hstack(
        [
            agent_text.style({"max-width": "650px"}),
            mo.ui.code_editor(
                value=agent, language="python", disabled=True, show_copy_button=True
            ).style(max_width="600px", overflow="auto"),
        ],
        widths=[1, 1],
        align="start",
    )

    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Running our agent

    Our agent is good at:

    - Fixing broken files and validating output `"fix broken_file.py"` (or use `/` to run a sample prompt)
    - Doing research and implementing new calls `"research new techniques in python 3.13 and write a simple file demostrating one"`
    - Writing novel output `"write me a simple file that splits tips among a group of friends"`

    You can interact with the agent below or run `uv run simple_agent.py` in a shell.
    """
    )
    return


@app.cell
def _(load_dotenv, mo):
    load_dotenv()

    input_key = mo.ui.text(label="Anthropic API key", kind="password")

    ANTHROPIC_MODEL = "claude-sonnet-4-0"

    ANTHROPIC_TOOLS = [
        {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"},
        {"type": "web_search_20250305", "name": "web_search", "max_uses": 5},
        {"type": "bash_20250124", "name": "bash"},
    ]
    return ANTHROPIC_MODEL, ANTHROPIC_TOOLS, input_key


@app.cell
def _(input_key, os):
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or input_key.value
    return (ANTHROPIC_API_KEY,)


@app.cell(hide_code=True)
def _(
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    ANTHROPIC_TOOLS,
    Path,
    anthropic,
    execute_tool,
):
    def handle_message(messages, config):
        """Handle incoming chat messages and return AI response."""
        if not messages:
            return "Hello! I'm your AI coding assistant. How can I help you today?"

        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

            # Load and parse prompt
            prompt_content = Path("./public/instructions.md").read_text()

            system_prompt = prompt_content[
                prompt_content.find("<role>") + 6 : prompt_content.find("</role>")
            ].strip()

            instructions_content = prompt_content[
                prompt_content.find("<thinking_process>") :
            ].strip()

            # Convert chat messages to Anthropic format with caching structure
            anthropic_messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": instructions_content,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                }
            ]

            for msg in messages:
                anthropic_messages.append(
                    {
                        "role": "user" if msg.role == "user" else "assistant",
                        "content": msg.content,
                    }
                )

            accumulated_output = ""

            while True:
                response = client.messages.create(
                    model=ANTHROPIC_MODEL,
                    system=[{"type": "text", "text": system_prompt}],
                    max_tokens=4096,
                    temperature=0.2,
                    messages=anthropic_messages,
                    tools=ANTHROPIC_TOOLS,
                )

                if response.stop_reason in ["tool_use"]:
                    tool_results = []
                    tool_calls = []
                    response_text = ""

                    # First pass: collect all tool calls and display text
                    for block in response.content:
                        if hasattr(block, "text"):
                            response_text += block.text
                        if block.type == "server_tool_use":
                            search_text = (
                                f"\n**Searched for:** {block.input.get('query')}\n\n"
                            )
                            response_text += search_text
                        if hasattr(block, "citations") and block.citations:
                            citation_text = (
                                f"**Cited sources:** {len(block.citations)}\n\n"
                            )
                            response_text += citation_text
                        if block.type == "tool_use":
                            if block.name == "bash":
                                tool_name = block.name
                            elif block.name == "str_replace_based_edit_tool":
                                tool_name = block.input.get("command", None)

                            tool_calls.append(
                                {
                                    "tool_name": tool_name,
                                    "tool_use_id": block.id,
                                    "tool_input": block.input,
                                }
                            )

                    # Second pass: execute all tools
                    if tool_calls:
                        response_text += (
                            f"\n**Executing {len(tool_calls)} tool(s)...**\n\n"
                        )
                        for tool_call in tool_calls:
                            tool_name = tool_call["tool_name"]
                            tool_use_id = tool_call["tool_use_id"]
                            tool_input = tool_call["tool_input"]

                            response_text += f"**Executing tool:** {tool_name}\n\n"

                            result = execute_tool(tool_name, tool_input)
                            response_text += "```\n" + result["content"] + "\n```\n\n"

                            # Handle structured error results
                            tool_result = {
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": result["content"],
                            }

                            if result["is_error"]:
                                tool_result["is_error"] = True

                            tool_results.append(tool_result)

                    anthropic_messages.append(
                        {
                            "role": "assistant",
                            "content": [block for block in response.content],
                        }
                    )

                    # Accumulate this iteration's output
                    accumulated_output += response_text

                    if tool_results:
                        anthropic_messages.append(
                            {"role": "user", "content": tool_results}
                        )
                        continue
                    else:
                        return accumulated_output or "Task completed."
                else:
                    # Handle non-tool responses
                    response_text = ""
                    if response.stop_reason not in ["end_turn"]:
                        response_text += f"Stop reason: {response.stop_reason}\n"

                    for block in response.content:
                        if hasattr(block, "text"):
                            response_text += block.text

                    return accumulated_output + response_text

        except Exception as e:
            return f"Error: {str(e)}"

    return (handle_message,)


@app.cell(hide_code=True)
def _(handle_message, input_key, mo):
    chat_text = mo.md(
        """
    ## Let's Chat
    We can implement a modified version for Marimo notebooks that returns the full output in a chat interface, with progressive tool execution updates

    /// admonition | Heads up
    Marimo does not yet support multiple messages or message streaming for dynamic visualization of tool calls. To visualize, use `uv run simple_agent.py` in your terminal.

    We'll print tool executions below the chat for visualization & the agent will return all tools in the final message.

    ///

    You may enter your api key in `.env` if run locally, or here if on the web.
    """
    )

    chat = mo.ui.chat(
        handle_message,
        prompts=[
            "Create a new, simple program that prints the current time",
            "Help me fix the broken file broken_file.py",
            "Research new features in python 3.13 and write a very simple file demonstrating one",
        ],
        show_configuration_controls=False,
        allow_attachments=False,
    )

    mo.vstack(
        [
            chat_text.style({"max-width": "650", "overflow-wrap": "normal"}),
            input_key,
            chat.style({"max-width": "650", "overflow-wrap": "normal"}),
        ]
    )
    return


@app.cell(hide_code=True)
def _(Path, mo):
    # Cleanup cell: Remove all Python files except notebook.py and simple_agent.py
    # Then copy broken_file.py from prompts to root
    def cleanup_files():
        root_dir = Path(".")
        kept_files = {"notebook.py", "simple_agent.py"}

        # Remove all .py files except the ones we want to keep
        for py_file in root_dir.glob("*.py"):
            if py_file.name not in kept_files:
                py_file.unlink()
                print(f"Removed: {py_file.name}")

        # Copy broken_file.py from prompts to root
        broken_file_source = Path("public/broken_file.py")
        broken_file_dest = Path("broken_file.py")

        if broken_file_source.exists():
            broken_file_dest.write_text(broken_file_source.read_text())
            print(f"Copied {broken_file_source} to {broken_file_dest}")
        else:
            print(f"Warning: {broken_file_source} not found")

    cleanup_button = mo.ui.button(
        label="🧹 Cleanup Python Files", on_click=lambda _: cleanup_files()
    )

    mo.md(
        f"""
    ## File Cleanup

    This will remove all `.py` files in the root directory except: `notebook.py` & `simple_agent.py`

    Then copy `public/broken_file.py` to the root directory.

    {cleanup_button}
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Next steps

    1. Implement more robust stop reason handling, retry logic, and try / except blocks
    2. Implement streaming for more responsive messages
    3. Turn our simple agent into a [_Multi-agent Architecture_](https://www.anthropic.com/engineering/built-multi-agent-research-system) with Opus as an orchestrator and Haiku for lightweight tasks
    4. Play with [remote code execution](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/code-execution-tool) for a sandboxed approach
    5. [Reduce latency](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-latency) in our responses
    6. Continue exploring optimization techniques

    ## Resources

    - [Anthropic documentation](https://docs.anthropic.com)
    - [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)
    - [Marimo docs](https://docs.marimo.io/)
    """
    )
    return


if __name__ == "__main__":
    app.run()
