"""End-to-end tests for the aici CLI tool's clipboard functionality on Ubuntu.

These tests verify the clipboard integration using Xvfb for headless testing.
"""

import os
import sys
import subprocess
import tempfile
import pytest
import unittest.mock
from pathlib import Path
from unittest.mock import patch, MagicMock

AICI_CMD = "python -m aici"

@pytest.fixture(scope="module", autouse=True)
def mock_deepseek_api():
    """Mock the DeepSeek API for all tests in this module."""
    with patch('openai.resources.chat.completions.Completions.create') as mock_create:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Clipboard Test Response"
        mock_create.return_value = mock_response
        
        yield mock_create

class TestAiciClipboard:
    """Tests for the clipboard functionality of the aici CLI tool."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        if not os.getenv('DEEPSEEK_API_KEY'):
            os.environ['DEEPSEEK_API_KEY'] = 'sk-dummy-api-key-for-testing'
    
    def test_clipboard_output(self):
        """Test that output can be sent to the clipboard."""
        prompt = "Hello, please respond with a clipboard test"
        
        result = subprocess.run(
            f"{AICI_CMD} '{prompt}' --output=clip --complete", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0
        
        clipboard_content = subprocess.run(
            "xclip -o -selection clipboard", 
            shell=True, 
            capture_output=True, 
            text=True
        ).stdout
        
        assert len(clipboard_content) > 0
        assert "Clipboard Test Response" in clipboard_content
    
    def test_clipboard_with_system_message(self):
        """Test clipboard output with a custom system message."""
        prompt = "Hello clipboard"
        system = "You are a helpful assistant for clipboard testing."
        
        result = subprocess.run(
            f"{AICI_CMD} '{prompt}' --output=clip --system=\"{system}\" --complete", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0
        
        clipboard_content = subprocess.run(
            "xclip -o -selection clipboard", 
            shell=True, 
            capture_output=True, 
            text=True
        ).stdout
        
        assert len(clipboard_content) > 0
        assert "Clipboard Test Response" in clipboard_content

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-xvs", __file__]))
