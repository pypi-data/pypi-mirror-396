"""Tests for UTF-8 encoding configuration."""
import sys


def test_stdout_encoding_after_import():
    """Verify stdout uses UTF-8 encoding after importing semiautomatic."""
    import semiautomatic  # noqa: F401

    # On Windows, importing semiautomatic should configure UTF-8
    # On other platforms, encoding depends on locale but should still work
    if sys.platform == "win32":
        assert sys.stdout.encoding.lower() == "utf-8"
        assert sys.stderr.encoding.lower() == "utf-8"


def test_subprocess_wrapper_defaults():
    """Verify subprocess wrapper has UTF-8 defaults."""
    from semiautomatic.lib.subprocess import run, PIPE

    # Run a simple command that outputs text
    if sys.platform == "win32":
        result = run(["cmd", "/c", "echo hello"], capture_output=True)
    else:
        result = run(["echo", "hello"], capture_output=True)

    # With encoding='utf-8' default, stdout should be a string, not bytes
    assert isinstance(result.stdout, str)
    assert "hello" in result.stdout


def test_subprocess_wrapper_reexports():
    """Verify commonly used subprocess items are re-exported."""
    from semiautomatic.lib import subprocess

    assert hasattr(subprocess, 'run')
    assert hasattr(subprocess, 'PIPE')
    assert hasattr(subprocess, 'DEVNULL')
    assert hasattr(subprocess, 'CalledProcessError')
