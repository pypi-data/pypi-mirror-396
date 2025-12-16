"""Configuration for e2e tests.

This module provides pytest fixtures and configuration for e2e tests.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

os.environ.setdefault('DEEPSEEK_API_KEY', 'sk-dummy-api-key-for-testing')

@pytest.fixture(scope="session", autouse=True)
def setup_mock_environment():
    """Set up the mock environment for all tests."""
    mock_module_path = os.path.join(os.path.dirname(__file__), "mock_openai.py")
    with open(mock_module_path, "w") as f:
        f.write("""
import sys
from unittest.mock import MagicMock

if 'pytest' in sys.modules:
    import openai.resources.chat.completions.completions
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mocked DeepSeek Response"
    
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Mocked DeepSeek Response"
    
    original_create = openai.resources.chat.completions.completions.Completions.create
    
    def mock_create(self, **kwargs):
        if kwargs.get('stream', False):
            return [mock_chunk]
        else:
            return mock_response
    
    openai.resources.chat.completions.completions.Completions.create = mock_create
""")
    
    init_path = os.path.join(os.path.dirname(__file__), "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write("# e2e test package\n")
    
    yield
    
    if os.path.exists(mock_module_path):
        os.remove(mock_module_path)
