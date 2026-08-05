"""MCP server for text validation and extraction (email, URL, slug)."""

import re

from fastmcp import FastMCP

mcp = FastMCP("Validate")

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_URL_RE = re.compile(r"https?://[^\s<>\"]+")


@mcp.tool()
def validate_email(text: str) -> str:
    """Check whether a string is a valid email address.

    Args:
        text: String to validate.

    Returns:
        'True' or 'False'.
    """
    return str(bool(_EMAIL_RE.fullmatch(text.strip())))


@mcp.tool()
def validate_url(text: str) -> str:
    """Check whether a string is a valid URL.

    Args:
        text: String to validate.

    Returns:
        'True' or 'False'.
    """
    return str(bool(_URL_RE.fullmatch(text.strip())))


@mcp.tool()
def extract_emails(text: str) -> str:
    """Extract all email addresses found in a text.

    Args:
        text: Text to search.

    Returns:
        Comma-separated list of found email addresses.
    """
    found = _EMAIL_RE.findall(text)
    return ", ".join(found) if found else "No emails found."


@mcp.tool()
def extract_urls(text: str) -> str:
    """Extract all URLs found in a text.

    Args:
        text: Text to search.

    Returns:
        Comma-separated list of found URLs.
    """
    found = _URL_RE.findall(text)
    return ", ".join(found) if found else "No URLs found."


@mcp.tool()
def slugify(text: str) -> str:
    """Convert text into a URL-safe slug.

    Args:
        text: Text to slugify.

    Returns:
        Lowercase, hyphen-separated slug.
    """
    slug = text.strip().lower()
    slug = re.sub(r"[^\w]+", "-", slug)
    return slug.strip("-")


if __name__ == "__main__":
    mcp.run()
