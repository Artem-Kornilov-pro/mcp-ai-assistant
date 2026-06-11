"""Terminal chat interface for MCP AI Assistant."""

import sys
from typing import Any

from src.config import load_config
from src.llm import LLMClient


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
    print("╚══════════════════════════════════════╝")
    print()


def print_tool_call(name: str, args: dict[str, Any]) -> None:
    """Display a tool call being made."""
    print(f"\n  🔧 Calling tool: {name}")
    if args:
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
        print(f"  📄 Result: {lines[0][:100]}{'...' if len(lines[0]) > 100 else ''}")
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
        messages.clear()
        print("  🧹 Conversation cleared.\n")
        return True

    if user_input == "/help":
        print_banner()
        return True

    messages.append({"role": "user", "content": user_input})
    return True


def run() -> None:
    """Run the terminal chat loop."""
    try:
        config = load_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Make sure .env file exists with required variables.")
        sys.exit(1)

    client = LLMClient(
        api_key=config.llm.api_key,
        folder_id=config.llm.folder_id,
        model=config.llm.model,
        temperature=config.llm.temperature,
        max_tokens=config.llm.max_tokens,
        timeout=config.llm.timeout,
    )

    print_banner()

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant with access to tools. "
                "Use tools when appropriate to answer questions. "
                "Be concise and friendly. "
                "Respond in Russian if the user writes in Russian."
            ),
        }
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
            print("\n  🤔 Thinking...", end="", flush=True)
            response = client.chat(messages)
            print("\r" + " " * 20 + "\r", end="")  # Clear "Thinking..."
            print(f"  🤖 Assistant: {response}\n")
            messages.append({"role": "assistant", "content": response})

        except Exception as e:
            print(f"\r  ❌ Error: {e}\n")
            # Remove the user message that failed
            if messages and messages[-1]["role"] == "user":
                messages.pop()


if __name__ == "__main__":
    run()
