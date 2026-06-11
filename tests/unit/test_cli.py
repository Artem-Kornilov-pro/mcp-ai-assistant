"""Unit tests for CLI chat interface."""

import pytest


class TestHandleUserInput:
    """Tests for handle_user_input function."""

    def test_exit_command(self) -> None:
        from src.main import handle_user_input

        messages: list[dict] = []
        result = handle_user_input("/exit", messages)
        assert result is False
        assert messages == []

    def test_clear_command(self) -> None:
        from src.main import handle_user_input

        messages: list[dict] = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ]
        result = handle_user_input("/clear", messages)
        assert result is True
        assert messages == []

    def test_help_command(self) -> None:
        from src.main import handle_user_input

        messages: list[dict] = []
        result = handle_user_input("/help", messages)
        assert result is True
        assert messages == []

    def test_normal_message(self) -> None:
        from src.main import handle_user_input

        messages: list[dict] = []
        result = handle_user_input("Hello, AI!", messages)
        assert result is True
        assert messages == [{"role": "user", "content": "Hello, AI!"}]

    def test_empty_input(self) -> None:
        from src.main import handle_user_input

        messages: list[dict] = []
        result = handle_user_input("", messages)
        assert result is True
        assert messages == []

    def test_whitespace_input(self) -> None:
        from src.main import handle_user_input

        messages: list[dict] = []
        result = handle_user_input("   ", messages)
        assert result is True
        assert messages == []


class TestPrintToolCall:
    """Tests for tool call display functions."""

    def test_print_tool_call_no_args(self, capsys: pytest.CaptureFixture) -> None:
        from src.main import print_tool_call

        print_tool_call("read_file", {})
        captured = capsys.readouterr()
        assert "read_file" in captured.out

    def test_print_tool_call_with_args(self, capsys: pytest.CaptureFixture) -> None:
        from src.main import print_tool_call

        print_tool_call("write_file", {"path": "test.txt", "content": "hello"})
        captured = capsys.readouterr()
        assert "write_file" in captured.out
        assert "test.txt" in captured.out

    def test_print_tool_call_long_value_truncated(self, capsys: pytest.CaptureFixture) -> None:
        from src.main import print_tool_call

        long_val = "x" * 100
        print_tool_call("search", {"query": long_val})
        captured = capsys.readouterr()
        assert "..." in captured.out


class TestPrintToolResult:
    """Tests for tool result display functions."""

    def test_print_short_result(self, capsys: pytest.CaptureFixture) -> None:
        from src.main import print_tool_result

        print_tool_result("File written successfully")
        captured = capsys.readouterr()
        assert "File written successfully" in captured.out

    def test_print_long_result_truncated(self, capsys: pytest.CaptureFixture) -> None:
        from src.main import print_tool_result

        long_result = "x" * 200
        print_tool_result(long_result)
        captured = capsys.readouterr()
        assert "..." in captured.out

    def test_print_multiline_result(self, capsys: pytest.CaptureFixture) -> None:
        from src.main import print_tool_result

        multiline = "line1\nline2\nline3"
        print_tool_result(multiline)
        captured = capsys.readouterr()
        assert "3 lines" in captured.out
