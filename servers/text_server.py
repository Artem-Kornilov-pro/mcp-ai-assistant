"""MCP server for text utilities (hashing, base64, UUID, word count)."""

import base64
import hashlib
import uuid

from fastmcp import FastMCP

mcp = FastMCP("Text")

_ALGORITHMS = {"md5", "sha1", "sha256"}


@mcp.tool()
def hash_text(text: str, algorithm: str = "sha256") -> str:
    """Compute a hash digest of a text string.

    Args:
        text: Text to hash.
        algorithm: One of 'md5', 'sha1', 'sha256'. Default: 'sha256'.

    Returns:
        Hex digest of the hash.
    """
    if algorithm not in _ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Use one of {sorted(_ALGORITHMS)}")
    return hashlib.new(algorithm, text.encode("utf-8")).hexdigest()


@mcp.tool()
def encode_base64(text: str) -> str:
    """Encode a text string as base64.

    Args:
        text: Text to encode.

    Returns:
        Base64-encoded string.
    """
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


@mcp.tool()
def decode_base64(data: str) -> str:
    """Decode a base64 string back to text.

    Args:
        data: Base64-encoded string.

    Returns:
        Decoded text.
    """
    try:
        return base64.b64decode(data).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Invalid base64 input: {e}") from e


@mcp.tool()
def generate_uuid() -> str:
    """Generate a random UUID4.

    Returns:
        UUID4 string.
    """
    return str(uuid.uuid4())


@mcp.tool()
def word_count(text: str) -> str:
    """Count words, characters, and lines in a text.

    Args:
        text: Text to analyze.

    Returns:
        Word, character, and line counts.
    """
    words = len(text.split())
    chars = len(text)
    lines = len(text.splitlines()) if text else 0
    return f"Слов: {words}\nСимволов: {chars}\nСтрок: {lines}"


if __name__ == "__main__":
    mcp.run()
