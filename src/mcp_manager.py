"""MCP manager - direct tool calling without MCP transport."""

from typing import Any


class MCPManager:
    """Manages tools from server modules and provides direct access."""

    def __init__(self) -> None:
        self._tools: dict[str, dict[str, Any]] = {}

    def register_tool(
        self, name: str, description: str, func: Any, parameters: dict[str, Any] | None = None
    ) -> None:
        """Register a single tool."""
        self._tools[name] = {
            "name": name,
            "description": description,
            "func": func,
            "parameters": parameters or {},
        }

    def register_from_module(
        self, prefix: str, module: Any, tools_config: list[dict[str, Any]]
    ) -> None:
        """Register tools from a server module."""
        for config in tools_config:
            name = f"{prefix}__{config['name']}"
            func = getattr(module, config["name"])
            self.register_tool(
                name=name,
                description=config.get("description", ""),
                func=func,
                parameters=config.get("parameters", {}),
            )

    def get_tools_for_openai(self) -> list[dict[str, Any]]:
        """Get tools in OpenAI function calling format."""
        return [
            {
                "name": t["name"],
                "description": t["description"],
            }
            for t in self._tools.values()
        ]

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Call a tool and return result as string."""
        if tool_name not in self._tools:
            raise ValueError(f"Tool not found: {tool_name}")

        func = self._tools[tool_name]["func"]
        result = func(**arguments)
        return str(result)
