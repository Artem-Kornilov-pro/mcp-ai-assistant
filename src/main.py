"""Terminal chat interface for MCP AI Assistant with tool calling."""

import asyncio
import json
import re
import sys
from typing import Any

from src.config import load_config
from src.llm import LLMClient
from src.mcp_manager import MCPManager


def print_banner() -> None:
    """Print welcome banner."""
    print()
    print("╔══════════════════════════════════════╗")
    print("║       MCP AI Assistant v0.1.0        ║")
    print("║   Personal AI powered by MCP servers ║")
    print("╠══════════════════════════════════════╣")
    print("║  Commands:                           ║")
    print("║    /exit   - quit                    ║")
    print("║    /clear  - reset conversation      ║")
    print("║    /help   - show this message       ║")
    print("║    /tools  - list available tools    ║")
    print("╚══════════════════════════════════════╝")
    print()


def print_tool_call(name: str, args: dict[str, Any]) -> None:
    """Display a tool call being made."""
    print(f"\n  🔧 Calling tool: {name}")
    for key, value in args.items():
        val_str = str(value)
        if len(val_str) > 80:
            val_str = val_str[:77] + "..."
        print(f"     {key}: {val_str}")


def print_tool_result(result: str) -> None:
    """Display tool call result."""
    lines = result.strip().split("\n")
    if len(lines) == 1 and len(lines[0]) <= 100:
        print(f"  📄 Result: {lines[0]}")
    else:
        preview = lines[0][:100]
        print(f"  📄 Result: {preview}{'...' if len(lines[0]) > 100 else ''}")
        if len(lines) > 1:
            print(f"     ({len(lines)} lines total)")


def handle_user_input(user_input: str, messages: list[dict[str, Any]]) -> bool:
    """Process user input. Returns False if should exit."""
    user_input = user_input.strip()

    if not user_input:
        return True

    if user_input == "/exit":
        print("\n  Goodbye! 👋\n")
        return False

    if user_input == "/clear":
        messages[:] = [messages[0]]
        print("  🧹 Conversation cleared.\n")
        return True

    if user_input == "/help":
        print_banner()
        return True

    if user_input == "/tools":
        sys_msg = messages[0]["content"] if messages else ""
        print(f"  🔩 {sys_msg}\n")
        return True

    messages.append({"role": "user", "content": user_input})
    return True


def parse_tool_calls(text: str) -> list[dict[str, Any]]:
    """Parse XML-style tool calls from model response text."""
    tool_calls: list[dict[str, Any]] = []

    # Try JSON code blocks first
    json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            if isinstance(data, dict):
                tool_calls.append(
                    {
                        "name": data.get("name", data.get("tool", "")),
                        "arguments": data.get("arguments", data.get("args", {})),
                    }
                )
                return tool_calls
            if isinstance(data, list):
                for item in data:
                    tool_calls.append(
                        {
                            "name": item.get("name", item.get("tool", "")),
                            "arguments": item.get("arguments", item.get("args", {})),
                        }
                    )
                return tool_calls
        except json.JSONDecodeError:
            pass

    # Try XML-style
    xml_match = re.findall(r"<(\w+)>(.*?)</\1>", text, re.DOTALL)
    top_level_tags: set[str] = set()
    skip_tags = {
        "function",
        "owner",
        "repo",
        "path",
        "title",
        "content",
        "query",
        "name",
        "range",
        "values",
        "pattern",
        "spreadsheet_id",
        "range_name",
        "body",
    }
    for tag, _ in xml_match:
        if tag.lower() not in skip_tags:
            top_level_tags.add(tag)

    for tool_name in top_level_tags:
        pattern = rf"<{tool_name}>(.*?)</{tool_name}>"
        matches = re.findall(pattern, text, re.DOTALL)
        for body in matches:
            args: dict[str, Any] = {}
            child_tags = re.findall(r"<(\w+)>(.*?)</\1>", body, re.DOTALL)
            for child_name, child_value in child_tags:
                args[child_name] = child_value.strip()
            if args:
                tool_calls.append({"name": tool_name, "arguments": args})

    return tool_calls


def _map_tool_name(name: str) -> str:
    """Map model-generated names to actual tool names."""
    mapping: dict[str, str] = {
        "read_github_repository": "github__get_file",
        "read_github_file": "github__get_file",
        "get_file": "github__get_file",
        "list_repos": "github__list_repos",
        "create_issue": "github__create_issue",
        "search_code": "github__search_code",
        "read_file": "filesystem__read_file",
        "write_file": "filesystem__write_file",
        "list_directory": "filesystem__list_directory",
        "search_files": "filesystem__search_files",
    }
    return mapping.get(name, name)


async def run_async() -> None:
    """Run the terminal chat loop with MCP integration."""
    try:
        config = load_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    client = LLMClient(
        api_key=config.llm.api_key,
        folder_id=config.llm.folder_id,
        model=config.llm.model,
        temperature=config.llm.temperature,
        max_tokens=config.llm.max_tokens,
        timeout=config.llm.timeout,
    )

    manager = MCPManager()

    # Register filesystem tools
    from servers.filesystem import list_directory, read_file, search_files, write_file

    manager.register_tool(
        "filesystem__read_file",
        "Read contents of a file from the workspace directory. Args: path (file path)",
        read_file,
    )
    manager.register_tool(
        "filesystem__write_file",
        "Write content to a file in the workspace directory. Args: path, content",
        write_file,
    )
    manager.register_tool(
        "filesystem__list_directory",
        "List files and directories in a folder. Args: path (default '.')",
        list_directory,
    )
    manager.register_tool(
        "filesystem__search_files",
        "Search for files by name pattern. Args: pattern (e.g. '*.py')",
        search_files,
    )

    # Register github tools
    from servers.github import create_issue, get_file, list_repos, search_code

    manager.register_tool(
        "github__list_repos",
        "List all repositories for the authenticated user",
        list_repos,
    )
    manager.register_tool(
        "github__create_issue",
        "Create a new issue in a GitHub repository. Args: repo (full name), title, body",
        create_issue,
    )
    manager.register_tool(
        "github__search_code",
        "Search for code in GitHub repositories. Args: query, repo (optional)",
        search_code,
    )
    manager.register_tool(
        "github__get_file",
        """Get contents of a file from a GitHub repository.
        Args: repo (like 'user/repo'), path (file path inside repo)""",
        get_file,
    )

    all_tools = manager.get_tools_for_openai()
    print(f"  ✅ {len(all_tools)} tools loaded.\n")
    print("  Available tools:")
    for t in all_tools:
        print(f"    - {t['name']} — {t['description']}")
    print()

    tool_list = "\n".join(f"- {t['name']} — {t['description']}" for t in all_tools)

    system_prompt = (
        "You are a helpful AI assistant with access to tools.\n\n"
        "When you need to use a tool, write EXACTLY like this:\n\n"
        "<tool_name>\n  <param1>value1</param1>\n  <param2>value2</param2>\n</tool_name>\n\n"
        "Available tools:\n"
        f"{tool_list}\n\n"
        "After getting tool results, continue the conversation. "
        "Respond in Russian if the user writes in Russian."
    )

    print_banner()

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
    ]

    running = True
    while running:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye! 👋\n")
            break

        running = handle_user_input(user_input, messages)
        if not running:
            break
        if not user_input or user_input.startswith("/"):
            continue

        try:
            max_tool_rounds = 5
            for _ in range(max_tool_rounds):
                print("  🤔 Thinking...", end="", flush=True)
                response = client.chat(messages)
                print("\r" + " " * 20 + "\r", end="")

                content = response.get("content", "")
                tool_calls = parse_tool_calls(content)

                if not tool_calls:
                    print(f"  🤖 Assistant: {content}\n")
                    messages.append({"role": "assistant", "content": content})
                    break

                for tc in tool_calls:
                    raw_name = tc["name"]
                    tool_name = _map_tool_name(raw_name)
                    tool_args = tc["arguments"]

                    print_tool_call(tool_name, tool_args)
                    try:
                        result = await manager.call_tool(tool_name, tool_args)
                        print_tool_result(result)
                        messages.append(
                            {
                                "role": "user",
                                "content": f"Tool result for {tool_name}:\n{result}",
                            }
                        )
                    except Exception as e:
                        error_msg = f"Error: {e}"
                        print(f"  ❌ {error_msg}")
                        messages.append(
                            {
                                "role": "user",
                                "content": f"Tool error for {tool_name}: {error_msg}",
                            }
                        )
            else:
                print("  ⚠️  Max tool rounds reached.\n")

        except Exception as e:
            print(f"\r  ❌ Error: {e}\n")
            if messages and messages[-1]["role"] == "user":
                messages.pop()


def run() -> None:
    """Entry point - runs the async chat loop."""
    asyncio.run(run_async())


if __name__ == "__main__":
    run()
