"""Unit tests for Text MCP server."""

import pytest


class TestHashText:
    """Tests for hash_text tool."""

    def test_sha256_default(self) -> None:
        from servers.text_server import hash_text

        result = hash_text("hello")
        assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

    def test_md5(self) -> None:
        from servers.text_server import hash_text

        result = hash_text("hello", algorithm="md5")
        assert result == "5d41402abc4b2a76b9719d911017c592"

    def test_invalid_algorithm(self) -> None:
        from servers.text_server import hash_text

        with pytest.raises(ValueError, match="Unsupported algorithm"):
            hash_text("hello", algorithm="sha512")


class TestBase64:
    """Tests for encode_base64 / decode_base64 tools."""

    def test_encode(self) -> None:
        from servers.text_server import encode_base64

        assert encode_base64("hello") == "aGVsbG8="

    def test_decode(self) -> None:
        from servers.text_server import decode_base64

        assert decode_base64("aGVsbG8=") == "hello"

    def test_roundtrip_unicode(self) -> None:
        from servers.text_server import decode_base64, encode_base64

        text = "Привет, мир!"
        assert decode_base64(encode_base64(text)) == text

    def test_decode_invalid(self) -> None:
        from servers.text_server import decode_base64

        with pytest.raises(ValueError, match="Invalid base64"):
            decode_base64("not valid base64 !!!")


class TestGenerateUuid:
    """Tests for generate_uuid tool."""

    def test_format(self) -> None:
        from servers.text_server import generate_uuid

        result = generate_uuid()
        assert len(result) == 36
        assert result.count("-") == 4

    def test_unique(self) -> None:
        from servers.text_server import generate_uuid

        assert generate_uuid() != generate_uuid()


class TestWordCount:
    """Tests for word_count tool."""

    def test_counts(self) -> None:
        from servers.text_server import word_count

        result = word_count("hello world\nfoo")
        assert "Слов: 3" in result
        assert "Строк: 2" in result

    def test_empty(self) -> None:
        from servers.text_server import word_count

        result = word_count("")
        assert "Слов: 0" in result
        assert "Строк: 0" in result
