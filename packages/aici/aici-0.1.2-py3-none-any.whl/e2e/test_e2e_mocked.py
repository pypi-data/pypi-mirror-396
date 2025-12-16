"""End-to-end tests for the aici CLI tool on Ubuntu with mocked API responses.

These tests interact with the actual command-line interface but mock the DeepSeek API
responses to avoid making real API calls. This allows for faster and more reliable testing.
"""

import os
import sys
import subprocess
import tempfile
import pytest
from pathlib import Path

AICI_CMD = "AICI_TEST_MODE=true python -m aici"

class TestAiciE2EMocked:
    """End-to-end tests for the aici CLI tool with mocked API responses."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        if not os.getenv('DEEPSEEK_API_KEY'):
            os.environ['DEEPSEEK_API_KEY'] = 'sk-dummy-api-key-for-testing'
        
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
        """Test a basic query with mocked API response."""
        prompt = "Hello, please respond with a test message"
        result = subprocess.run(
            f"{AICI_CMD} '{prompt}' --complete", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0
        assert "Mocked DeepSeek Response" in result.stdout
    
    def test_output_to_file(self):
        """Test writing output to a file."""
        prompt = "Hello, please respond with a test message"
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
        assert "Mocked DeepSeek Response" in content
    
    def test_stdin_input(self):
        """Test reading input from stdin."""
        prompt = "Hello, please respond with a test message"
        result = subprocess.run(
            f"echo '{prompt}' | {AICI_CMD} -", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0
        assert "Mocked DeepSeek Response" in result.stdout
    
    def test_model_selection(self):
        """Test specifying a different model."""
        prompt = "Hello, please respond with a test message"
        result = subprocess.run(
            f"{AICI_CMD} '{prompt}' --model=deepseek-reasoner --complete", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0
        assert "Mocked DeepSeek Response" in result.stdout
    
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
        assert "Mocked DeepSeek Response" in result.stdout

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-xvs", __file__]))
