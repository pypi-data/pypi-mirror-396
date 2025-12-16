"""
Test path normalization for Windows compatibility
"""
import os
import sys
import platform

# モジュールを直接インポート
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib
aici_main_module = importlib.import_module('aici.main')
normalize_path = aici_main_module.normalize_path


def test_normalize_path_unix_style():
    """Test normalization of Unix-style paths"""
    # Unix style path with forward slashes
    path = "~/Documents/test/file.txt"
    result = normalize_path(path)

    # Should expand ~ and normalize separators
    assert "~" not in result
    # Path should be normalized (no guarantee about final separator on different OS)
    assert os.path.isabs(os.path.expanduser(result)) or result.startswith(os.path.expanduser("~"))


def test_normalize_path_windows_style():
    """Test normalization of Windows-style paths"""
    # Windows style path with backslashes
    path = r"C:\Users\test\file.txt"
    result = normalize_path(path)

    # Should be normalized
    assert result == os.path.normpath(path)


def test_normalize_path_mixed_slashes():
    """Test normalization of paths with mixed slashes"""
    # Mixed slashes (common mistake on Windows)
    if platform.system() == 'Windows':
        path = "C:/Users/test\\file.txt"
        result = normalize_path(path)
        # On Windows, should convert all to backslashes
        assert "/" not in result or result.count("/") == 0  # All forward slashes should be gone
        assert "\\" in result or ":" in result  # Should have backslashes or be a drive letter
    else:
        # On Unix, just normalize
        path = "/home/test/file.txt"
        result = normalize_path(path)
        assert result == os.path.normpath(path)


def test_normalize_path_with_expanduser():
    """Test that tilde expansion works"""
    path = "~/.config/aici/config"
    result = normalize_path(path)

    # Tilde should be expanded
    assert "~" not in result
    # Should contain the actual home directory
    home = os.path.expanduser("~")
    assert result.startswith(home)


def test_normalize_path_forward_slash_on_windows():
    """Test that forward slashes are converted on Windows"""
    # Simulate a path that might be set in environment variable with forward slashes
    if platform.system() == 'Windows':
        path = "C:/Program Files/aici/config.txt"
        result = normalize_path(path)
        # Should be normalized to Windows format
        expected = os.path.normpath(path)
        assert result == expected
        # Normpath should convert to backslashes on Windows
        assert "\\" in result or result == path  # Either has backslashes or is unchanged (drive root)
