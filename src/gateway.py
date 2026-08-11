"""MCP gateway: mounts the servers/* tool modules behind a single MCP endpoint.

Which domains are exposed is controlled by the MCP_SERVERS environment
variable (comma-separated registry keys, or unset/"all" for everything).
Only the selected domains are imported, so picking a subset also skips the
import cost of the domains you didn't ask for (e.g. matplotlib, opencv, sympy).
"""

import importlib
import os

from fastmcp import FastMCP

SERVER_REGISTRY: dict[str, str] = {
    "filesystem": "servers.filesystem",
    "github": "servers.github",
    "google_sheets": "servers.google_sheets",
    "weather": "servers.weather",
    "datetime": "servers.datetime_tools",
    "sqlite": "servers.sqlite_server",
    "excel": "servers.excel_server",
    "csv": "servers.csv_server",
    "pdf": "servers.pdf_server",
    "archive": "servers.archive_server",
    "text": "servers.text_server",
    "random": "servers.random_server",
    "math": "servers.math_server",
    "linalg": "servers.linalg_server",
    "validate": "servers.validate_server",
    "image": "servers.image_server",
    "chart": "servers.chart_server",
    "qr": "servers.qr_server",
    "barcode": "servers.barcode_server",
    "translate": "servers.translate_server",
    "equation": "servers.equation_server",
    "currency": "servers.currency_server",
    "units": "servers.units_server",
    "holidays": "servers.holidays_server",
}


def _select_servers(raw: str) -> list[str]:
    """Parse the MCP_SERVERS env value into a sorted list of registry keys."""
    normalized = raw.strip().lower()
    if normalized in ("", "all"):
        return sorted(SERVER_REGISTRY)

    keys = [key.strip().lower() for key in normalized.split(",") if key.strip()]
    unknown = [key for key in keys if key not in SERVER_REGISTRY]
    if unknown:
        raise ValueError(
            f"Unknown server(s): {', '.join(unknown)}. Available: {sorted(SERVER_REGISTRY)}"
        )
    return keys


def build_gateway() -> FastMCP[None]:
    """Assemble a gateway FastMCP instance from the servers selected via MCP_SERVERS."""
    gateway: FastMCP[None] = FastMCP("MCP AI Assistant")

    for key in _select_servers(os.getenv("MCP_SERVERS", "all")):
        module = importlib.import_module(SERVER_REGISTRY[key])
        gateway.mount(module.mcp, namespace=key)

    return gateway


def main() -> None:
    """Build the gateway and run it with the configured transport."""
    gateway = build_gateway()
    gateway.run(
        transport=os.getenv("MCP_TRANSPORT", "http"),  # type: ignore[arg-type]
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )


if __name__ == "__main__":
    main()
