import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium", css_file="")


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
    # Claude Codes

    There are many coding agents, but how do they work? Surely they're complicated.

    As it would turn out, there's a simple implementation.

    This is a simple notebook demonstarting how to build a coding agent with web search & testing functionality in less than 200 lines _without_ external frameworks or dependencies. 

    Our agent will be able to 

    - View and edit files
    - Search the web
    - Execute bash commands (testing, installation, etc)
    - Create and modify code
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    Normall, tools are defined using a [JSON schema](https://json-schema.org/), for example a web search implementation might look like:

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

    However, Claude comes with a set of predefined tools that require much shorter definitions: [_Text Editor_](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/text-editor-tool), [_Web Search_](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/web-search-tool), and [_Bash_](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/bash-tool). 

    As it would turn out, those are the only tools we'll need for this demonstration:
    """
    )
    return


@app.cell(hide_code=True)
def _():
    return


@app.cell
def _(load_dotenv, mo, os):
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
    mo.show_code()
    return ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ANTHROPIC_TOOLS


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    An important point: though these tools handle things on the server, we'll still need to make the edits on the client themselves. 

    A good way to do this is define an `execute_tool` helper that handles the routing for various local operations. 

    We accept a `tool_name` and `tool_input`, then route tool requests to the appropriate operation. This provides a nice way to implement error and retry logic close to the tool implementations.

    Some best practices when executing tools:

    - Adding an `is_error` [property to the response](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#troubleshooting-errors), which we can then pass to Claude
    - Using proper try / except logic with detailed
    """
    )
    return


@app.cell
def _(Path, mo, subprocess):
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
    mo.show_code()
    return (execute_tool,)


@app.cell
def _(mo):
    mo.md(r"""First, we'll take a look at our prompt:""")
    return


@app.cell
def _(Path, mo):
    prompting = """
    Using [best practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices#example-formatting-preferences), we:

    - Define prompt blocks in XML tags
    - Use explicit instructions and language
    - Build context around the task and clearly define the role of the agent
    - Leverage thinking with `<thinking_process>`
    - Define tool use best practices to ensure parallel tool calls and proper work checking
    """
    prompt = Path("prompts/code_editor_fix.md").read_text()
    mo.hstack(
            [
            mo.md(prompting),
                mo.ui.code_editor(value=prompt, language="xml"),
            ],
        widths=[1,1]
        )

    return


@app.cell
def _(mo):
    mo.md(r"""Now, we'll take a look at our agent""")
    return


@app.cell
def _(Path, mo):
    split = """if __name__ == "__main__":"""

    agent = split + "\n\n" + Path("simple_agent.py").read_text().split(split)[1].strip()



    mo.ui.code_editor(value=agent, language="python")
    return


@app.cell
def _(mo):
    # Create state for progressive tool execution updates
    get_tool_output, set_tool_output = mo.state("")
    return get_tool_output, set_tool_output


@app.cell(hide_code=True)
def _(
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    ANTHROPIC_TOOLS,
    Path,
    anthropic,
    execute_tool,
    mo,
    set_tool_output,
):
    def handle_message(messages, config):
        """Handle incoming chat messages and return AI response."""
        if not messages:
            return "Hello! I'm your AI coding assistant. How can I help you today?"

        try:
            # Clear previous tool output and show we're starting
            set_tool_output("🔄 Starting to process your request...")

            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

            # Convert chat messages to Anthropic format (necessary for Marimo chat)
            anthropic_messages = []
            for msg in messages:
                anthropic_messages.append({
                    "role": "user" if msg.role == "user" else "assistant",
                    "content": msg.content
                })

            accumulated_output = ""
            tool_display_output = ""

            while True:
                # Define client
                response = client.messages.create(
                    model=ANTHROPIC_MODEL,
                    tools=ANTHROPIC_TOOLS,
                    system=[
                        {
                            "type": "text",
                            "text": Path("prompts/code_editor_fix.md").read_text(),
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    max_tokens=4096,
                    messages=anthropic_messages,
                )

                if response.stop_reason in ["tool_use", "end_turn"]:
                    tool_results = []
                    tool_calls = []
                    response_text = ""

                    # First pass: collect all tool calls and display text (like original)
                    for block in response.content:
                        if hasattr(block, "text") and block.text:
                            response_text += block.text
                        if block.type == "server_tool_use":
                            search_query = block.input.get('query')
                            search_text = f"\n\n**Searched for:** {search_query}"
                            response_text += search_text
                            tool_display_output += search_text
                            set_tool_output(tool_display_output)
                        if hasattr(block, "citations") and block.citations:
                            citation_text = f"\n**Cited sources:** {len(block.citations)}"
                            response_text += citation_text
                            tool_display_output += citation_text
                            set_tool_output(tool_display_output)
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

                    # Second pass: execute all tools (like original)
                    if tool_calls:
                        execution_text = f"\n\n**Executing {len(tool_calls)} tool(s)...**\n"
                        response_text += execution_text
                        tool_display_output += execution_text
                        set_tool_output(tool_display_output)

                        for tool_call in tool_calls:
                            tool_name = tool_call["tool_name"]
                            tool_use_id = tool_call["tool_use_id"]
                            tool_input = tool_call["tool_input"]

                            # Display detailed tool input (similar to simple_agent.py)
                            input_text = f"\n**Called the {tool_name} tool with the following input:**\n"
                            input_text += f"```json\n{tool_input}\n```\n"
                            response_text += input_text
                            tool_display_output += input_text
                            set_tool_output(tool_display_output)

                            # Show the bash command being executed (like original)
                            if tool_name == "bash":
                                command = tool_input.get("command")
                                command_text = f"**Executing command:**\n```bash\n{command}\n```\n"
                                response_text += command_text
                                tool_display_output += command_text
                                set_tool_output(tool_display_output)

                            result = execute_tool(tool_name, tool_input)

                            # Display detailed tool result (similar to simple_agent.py)
                            result_header = f"**Result of calling the {tool_name} tool:**\n"
                            response_text += result_header
                            tool_display_output += result_header

                            if result["is_error"]:
                                error_text = f"**Error:**\n```\n{result['content']}\n```\n"
                                response_text += error_text
                                tool_display_output += error_text
                            else:
                                # For file operations, show more structured output
                                if tool_name in ["view", "create", "str_replace"]:
                                    if tool_name == "view" and not result["is_error"]:
                                        # Format file content with line numbers (similar to simple_agent.py output)
                                        content = result["content"]
                                        if "\n" in content:
                                            numbered_lines = []
                                            for i, line in enumerate(content.split("\n"), 1):
                                                numbered_lines.append(f"{i:5}→{line}")
                                            content_text = "```\n" + "\n".join(numbered_lines) + "\n```\n"
                                        else:
                                            content_text = f"```\n{content}\n```\n"
                                        response_text += content_text
                                        tool_display_output += content_text
                                    else:
                                        success_text = f"**Success:**\n```\n{result['content']}\n```\n"
                                        response_text += success_text
                                        tool_display_output += success_text
                                else:
                                    output_text = f"```\n{result['content']}\n```\n"
                                    response_text += output_text
                                    tool_display_output += output_text

                            # Update the display after each tool execution
                            set_tool_output(tool_display_output)

                            tool_result = {
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": result["content"],
                            }

                            if result["is_error"]:
                                tool_result["is_error"] = True

                            tool_results.append(tool_result)

                    # Add assistant response to conversation
                    anthropic_messages.append({
                        "role": "assistant",
                        "content": [block for block in response.content],
                    })

                    # Accumulate this iteration's output
                    accumulated_output += response_text

                    if tool_results:
                        # Add tool results and continue conversation
                        anthropic_messages.append({"role": "user", "content": tool_results})
                        continue
                    else:
                        # No more tools to execute, clear tool output and return accumulated output
                        set_tool_output("✅ Task completed!")
                        return accumulated_output or "Task completed."
                else:
                    # Simple text response - show stop reason if unusual (like original)
                    if response.stop_reason not in ["end_turn"]:
                        response_text = f"Stop reason: {response.stop_reason}\n\n"
                    else:
                        response_text = ""

                    for block in response.content:
                        if hasattr(block, "text"):
                            response_text += block.text

                    set_tool_output("✅ Response completed!")
                    return accumulated_output + response_text

        except Exception as e:
            set_tool_output(f"❌ Error: {str(e)}")
            return f"**Error:** {str(e)}"
    mo.show_code()
    return (handle_message,)


@app.cell
def _(mo):
    mo.md(
        r"""
    The agent is good at:

    - Fixing broken files and validating output `fix broken_file.py` (or use `/` to run a sample prompt)
    - Doing research and implementing new calls `research new techniques in python 3.13 and write a simple file demostrating one`
    - Writing novel output `write me a simple file that splits tips among a group of friends`

    Some important things to call out:

    - Prompt caching
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""We can implement a modified version for Marimo notebooks that returns the full output in a chat interface, with progressive tool execution updates shown below:""")
    return


@app.cell
def _(get_tool_output, handle_message, mo):
    chat = mo.ui.chat(
        handle_message,
        prompts=[
            "Help me fix the broken file broken_file.py",
            "Create a new React component",
            "Explain this code snippet",
            "Run tests and fix any issues"
        ],
        show_configuration_controls=False,
        allow_attachments=False
    )

    mo.vstack([
        mo.md(get_tool_output() or ""),chat
    ])
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
        on_click=lambda: cleanup_files()
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
