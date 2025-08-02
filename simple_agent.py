import subprocess
from pathlib import Path
import os
from dotenv import load_dotenv

import anthropic

load_dotenv()

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_MODEL or not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_MODEL and ANTHROPIC_API_KEY must be set")

ANTHROPIC_TOOLS = [
    {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"},
    {"type": "web_search_20250305", "name": "web_search", "max_uses": 5},
    {"type": "bash_20250124", "name": "bash", "cache_control": {"type": "ephemeral"}}, # cache tools
]


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
                timeout=30,  # Add timeout for safety
            )

            # Return both stdout and stderr, mark as error if non-zero exit code
            output = f"stdout: {result.stdout}\nstderr: {result.stderr}"
            return {"content": output, "is_error": result.returncode != 0}
        else:
            return {"content": f"Error: Unknown tool '{tool_name}'", "is_error": True}
    except Exception as e:
        return {"content": f"Error executing {tool_name}: {str(e)}", "is_error": True}


if __name__ == "__main__":

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    while True:
        user_input = input("💬 User: ")
        messages = [{"role": "user", "content": user_input}]

        while True:

            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                system=[
                    {
                        "type": "text",
                        "text": Path("prompts/code_editor_fix.md").read_text(),
                        "cache_control": {"type": "ephemeral"},  # cache system prompt
                    }
                ],
                max_tokens=4096,
                messages=messages,  # type: ignore
                tools=ANTHROPIC_TOOLS,  # type: ignore
            )
            if response.stop_reason in ["tool_use", "end_turn"]: # TODO: stop reason handling
                tool_results = []
                tool_calls = []

                # First pass: collect all tool calls and display text
                for block in response.content:
                    if hasattr(block, "text"):
                        print(block.text)
                    if block.type == "server_tool_use":
                        print(f"Searched for: {block.input.get('query')}")
                    if hasattr(block, "citations") and block.citations:
                        print(f"Cited sources: {len(block.citations)}")
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
                    print(f"Executing {len(tool_calls)} tool(s)...")
                    for tool_call in tool_calls:
                        tool_name = tool_call["tool_name"]
                        tool_use_id = tool_call["tool_use_id"]
                        tool_input = tool_call["tool_input"]

                        print(f"Executing tool: {tool_name}")

                        result = execute_tool(tool_name, tool_input)
                        print(result["content"])

                        # Handle structured error results
                        tool_result = {
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": result["content"],
                        }

                        if result["is_error"]:
                            tool_result["is_error"] = True

                        tool_results.append(tool_result)
                messages.append(
                    {
                        "role": "assistant",
                        "content": [block for block in response.content],
                    }
                )
                if tool_results:
                    messages.append({"role": "user", "content": tool_results})

                continue
            else:
                print(response.stop_reason)
                break
