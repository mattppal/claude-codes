import marimo

__generated_with = "0.14.16"
app = marimo.App(
    width="medium",
    app_title="Claude Codes",
    layout_file="layouts/notebook.slides.json",
)


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
    mo.md(
        r"""
    # <img src="public/claude.png" style="display: inline; max-height: 50px; margin: 0; border-radius: 0;" /> Claude Code(s)

    There are many coding agents, but how do they work? Surely they're complicated.

    As it would turn out, agents can just be while loops and tool calls.

    This is a simple notebook demonstarting how to build a coding agent with web search & testing functionality in less than 200 lines _without_ external frameworks or dependencies. 

    Our agent will be able to 

    - View and edit files
    - Search the web
    - Execute bash commands (testing, installation, etc)
    - Create and modify code

    This notebook is adapted from the `simple_agent.py` file in the root directory of this project.
    """
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

    We'll use shorter tools, included in Claude for this demo
    """
    )
    return


@app.cell
def _(mo):
    intro_tool_text = mo.md("""
    ## Init

    Claude comes with a set of predefined tools that require much shorter definitions: [_Text Editor_](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/text-editor-tool), [_Web Search_](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/web-search-tool), and [_Bash_](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/bash-tool). 

    As it would turn out, those are the only tools we'll need for this demonstration. We start with some imports and tool definitions
    """)
    return (intro_tool_text,)


@app.cell
def _(intro_tool_text, load_dotenv, mo, os):
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
    mo.hstack([intro_tool_text.style({"max-width": "650px", "overflow-wrap": "normal"}), mo.show_code().style({"max-width": "650px", "overflow-wrap": "normal"})])
    return ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ANTHROPIC_TOOLS


@app.cell
def _(Path, mo):
    prompting = """
    ## Prompting
    Now, we'll take a look at our system prompt:

    Using [best practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices#example-formatting-preferences), for prompts helps with tool execution and reasoning

    - Define prompt blocks in XML tags
    - Use explicit instructions and language
    - Build context around the task and clearly define the role of the agent
    - Leverage thinking with `<thinking_process>`
    - Define tool use best practices to ensure parallel tool calls and proper work checking
    """
    prompt = Path("prompts/code_editor_fix.md").read_text()
    mo.hstack(
            [
            mo.md(prompting).style({"max-width": "650px", "overflow-wrap": "normal"}),
                mo.ui.code_editor(value=prompt, language="xml", disabled=True).style({"max-width": "650px", "overflow-wrap": "normal"}),
            ],
        widths=[1,1]
        )

    return


@app.cell
def _(Path, subprocess):
    def execute_tool(tool_name: str, tool_input: dict) -> dict:
        """Execute a tool and return structured result with error handling."""
        try:
            if tool_name == "view":
                path = Path(str(tool_input.get("path")))
                if path.is_file():
                    content = path.read_text()
                    return {"content": content, "is_error": False}
                elif path.is_dir():
                    content = "\n".join(sorted([f.name for f in path.iterdir()]))
                    return {"content": content, "is_error": False}
                else:
                    return {"content": f"Error: {path} does not exist", "is_error": True}
            elif tool_name == "create":
                path = Path(str(tool_input.get("path")))
                content = str(tool_input.get("file_text"))
                if not content:
                    return {
                        "content": "Error: No content provided in file_text parameter",
                        "is_error": True,
                    }
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
                return {"content": f"File {path} written successfully", "is_error": False}
            elif tool_name == "str_replace":
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
                command = tool_input.get("command")
                print(command)
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
                return {"content": f"Error: Unknown tool '{tool_name}'", "is_error": True}
        except Exception as e:
            return {"content": f"Error executing {tool_name}: {str(e)}", "is_error": True}
    return (execute_tool,)


@app.cell
def _(Path, mo):


    tool_text = mo.md(text="""
    ## Handling Tools
    An important point: though these tools handle things on the server, we'll still need to make the edits and take action on our machines ourselves. 

    A good way to do this is define an `execute_tool` helper that handles the routing for various local operations. 

    We accept a `tool_name` and `tool_input`, then route tool requests to the appropriate operation. This provides a nice way to implement error and retry logic close to the tool implementations.

    Some best practices when executing tools:

    - Adding an `is_error` [property to the response](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#troubleshooting-errors), which we can then pass to Claude
    - Using proper try / except logic with detailed logging for the agent

    For this simple implementation, we only log errors. You could imagine wrapping these `ifs` with retry logic as suitible for your agent.
    """)

    split_tool_example = """def execute_tool(tool_name: str, tool_input: dict) -> dict:"""
    split_main = """if __name__ == "__main__":"""

    tool_example = split_tool_example + "\n\n" + Path("simple_agent.py").read_text().split(split_tool_example)[1].strip().split(split_main)[0].strip()

    mo.hstack([tool_text.style({"max-width": "650px", "overflow-wrap": "normal"}), mo.ui.code_editor(tool_example, language='python', disabled=True).style({"max-width": "650px", "overflow-wrap": "normal"}),], widths=[1,0])
    return (split_main,)


@app.cell
def _(Path, mo, split_main):
    agent_text = mo.md("""
    ## Building an agent
    Now, we'll take a look at our agent:

    /// admonition | Heads up
    This code is used for the CLI, which is simpler and easier to follow. This has been adapted for the Marimo chat interface below.

    ///

    The agent is a simple nested `While` that handles different cases.

    First, we initialize the anthropic client. It's important to note that we're caching the system prompt, which is quite long. Since this is sent with every message, we get cost savings during the cache window (5m by default)

    ### Caching

    Prompt caching caches the _full prefix_ up to the cache point in the following order: **tools**, **system**, **messages**.

    That means our cache point in the system prompt with _also_ cache tool use.

    ### Stop reasons

    Next, we handle `stop_reasons`, which is the client's way of communicating why the chat ended.

    A best practice is to implement [robust stop reason handling](https://docs.anthropic.com/en/api/handling-stop-reasons).

    ### Responses

    Now, we loop through responses and check for events: `text`, `tool_use` and `citations` (from our web results).
    These are surfaced to the user _and_ our agent.

    ### Tools

    If tools were requested, we make conditional calls to our executor function by [extracting relevant details](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#handling-results-from-client-tools)

    ### Response

    We return the results to the client and raise an error if one occurred.

    This `while` loop makes another good structure for top-level retries or error handling logic. 

    We simply raise an execption, but you could imagine some number of more complex iterations.
    """)


    agent = split_main + "\n\n" + Path("simple_agent.py").read_text().split(split_main)[1].strip()



    mo.hstack([agent_text.style({"max-width": "650px", "overflow-wrap": "normal"}), mo.ui.code_editor(value=agent, language="python", disabled=True, show_copy_button=True).style({"max-width": "650px", "overflow": "auto"}),], widths="equal")


    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Our agent

    The agent is good at:

    - Fixing broken files and validating output `fix broken_file.py` (or use `/` to run a sample prompt)
    - Doing research and implementing new calls `research new techniques in python 3.13 and write a simple file demostrating one`
    - Writing novel output `write me a simple file that splits tips among a group of friends`
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r""" """)
    return


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

            # Convert chat messages to Anthropic format
            anthropic_messages = []
            for msg in messages:
                anthropic_messages.append({
                    "role": "user" if msg.role == "user" else "assistant",
                    "content": msg.content
                })

            accumulated_output = ""

            while True:
                response = client.messages.create(
                    model=ANTHROPIC_MODEL,
                    system=[
                        {
                            "type": "text",
                            "text": Path("prompts/code_editor_fix.md").read_text(),
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    max_tokens=4096,
                    messages=anthropic_messages,
                    tools=ANTHROPIC_TOOLS,
                )

                if response.stop_reason in ["tool_use", "end_turn"]:
                    tool_results = []
                    tool_calls = []
                    response_text = ""

                    # First pass: collect all tool calls and display text
                    for block in response.content:
                        if hasattr(block, "text"):
                            response_text += block.text
                        if block.type == "server_tool_use":
                            search_text = f"\n**Searched for:** {block.input.get('query')}\n\n"
                            response_text += search_text
                        if hasattr(block, "citations") and block.citations:
                            citation_text = f"**Cited sources:** {len(block.citations)}\n\n"
                            response_text += citation_text
                        if block.type == "tool_use":
                            if block.name == "bash":
                                tool_name = block.name
                            elif block.name == "str_replace_based_edit_tool":
                                tool_name = block.input.get("command", None)

                            tool_calls.append({
                                "tool_name": tool_name,
                                "tool_use_id": block.id,
                                "tool_input": block.input,
                            })

                    # Second pass: execute all tools
                    if tool_calls:
                        response_text += f"\n**Executing {len(tool_calls)} tool(s)...**\n\n"
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

                    anthropic_messages.append({
                        "role": "assistant",
                        "content": [block for block in response.content],
                    })

                    # Accumulate this iteration's output
                    accumulated_output += response_text

                    if tool_results:
                        anthropic_messages.append({"role": "user", "content": tool_results})
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


@app.cell
def _(handle_message, mo):
    chat_text = mo.md("""
    We can implement a modified version for Marimo notebooks that returns the full output in a chat interface, with progressive tool execution updates

    /// admonition | Heads up
    Marimo does not yet support multiple messages or message streaming for dynamic visualization of tool calls. To visualize, use `uv run simple_agent.py` in your terminal

    ///
    """)

    chat = mo.ui.chat(
        handle_message,
        prompts=[
            "Create a new, simple program that prints the current time",
            "Help me fix the broken file broken_file.py",
            "Research new features in python 3.13 and write a very simple file demonstrating one",
        ],
        show_configuration_controls=False,
        allow_attachments=False
    )

    mo.vstack([chat_text.style({"max-width": "650", "overflow-wrap": "normal"}), chat.style({"max-width": "650", "overflow-wrap": "normal"})])
    return


@app.cell
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
        broken_file_source = Path("prompts/broken_file.py")
        broken_file_dest = Path("broken_file.py")

        if broken_file_source.exists():
            broken_file_dest.write_text(broken_file_source.read_text())
            print(f"Copied {broken_file_source} to {broken_file_dest}")
        else:
            print(f"Warning: {broken_file_source} not found")

    cleanup_button = mo.ui.button(
        label="🧹 Cleanup Python Files", 
        on_click=lambda _: cleanup_files()
    )

    mo.md(f"""
    **File Cleanup**

    This will remove all `.py` files in the root directory except:
    - `notebook.py` 
    - `simple_agent.py`

    Then copy `prompts/broken_file.py` to the root directory.

    {cleanup_button}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
