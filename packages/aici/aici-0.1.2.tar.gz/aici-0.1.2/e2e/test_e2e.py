"""End-to-end tests for the aici CLI tool on Ubuntu.

These tests interact with the actual command-line interface and verify
the functionality in a real Ubuntu environment. Some tests may require
a valid DeepSeek API key to be set in the environment.
"""

import os
import sys
import subprocess
import tempfile
import pytest
from pathlib import Path

AICI_CMD = "python -m aici"

class TestAiciE2E:
    """End-to-end tests for the aici CLI tool."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        assert os.getenv('DEEPSEEK_API_KEY') is not None, "DEEPSEEK_API_KEY is not set"
        
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_file = Path(self.temp_dir.name) / "output.txt"
    
    def teardown_method(self):
        """Clean up after each test."""
        self.temp_dir.cleanup()
    
    def test_version_output(self):
        """Test that the version command returns the correct version."""
        result = subprocess.run(
            f"{AICI_CMD} -v", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0
        from aici import __version__
        assert __version__ in result.stdout
    
    def test_basic_query(self):
        """Test a basic query with real API call (requires API key)."""
        prompt = "Hello, please respond with a single word: Test"
        result = subprocess.run(
            f"{AICI_CMD} '{prompt}' --complete", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0
        assert "Test" in result.stdout or "test" in result.stdout.lower()
    
    def test_output_to_file(self):
        """Test writing output to a file."""
        prompt = "Hello, please respond with exactly: FileOutputTest"
        result = subprocess.run(
            f"{AICI_CMD} '{prompt}' --complete > {self.output_file}", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0
        
        assert self.output_file.exists()
        content = self.output_file.read_text()
        assert len(content) > 0
        assert "FileOutputTest" in content
    
    def test_stdin_input(self):
        """Test reading input from stdin."""
        prompt = "Hello, please respond with exactly: StdinTest"
        result = subprocess.run(
            f"echo '{prompt}' | {AICI_CMD} -", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0
        assert "StdinTest" in result.stdout
    
    def test_model_selection(self):
        """Test specifying a different model."""
        prompt = "Hello, please respond with exactly: ModelTest"
        result = subprocess.run(
            f"{AICI_CMD} '{prompt}' --model=deepseek-reasoner --complete", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0
        assert "ModelTest" in result.stdout
    
    def test_system_message(self):
        """Test specifying a custom system message."""
        prompt = "What language are you using?"
        system = "You are a helpful assistant that only speaks French."
        result = subprocess.run(
            f"{AICI_CMD} '{prompt}' --system=\"{system}\" --complete", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0
        french_words = ["je", "suis", "français", "bonjour", "merci"]
        assert any(word in result.stdout.lower() for word in french_words)

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-xvs", __file__]))
