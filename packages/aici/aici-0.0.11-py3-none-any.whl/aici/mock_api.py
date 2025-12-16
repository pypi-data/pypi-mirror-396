"""Mock API module for testing.

This module provides mock implementations of the DeepSeek API for testing.
"""

import os
from unittest.mock import MagicMock

TEST_MODE = os.environ.get('AICI_TEST_MODE', 'false').lower() == 'true'

mock_response = MagicMock()
mock_response.choices = [MagicMock()]
mock_response.choices[0].message.content = "Mocked DeepSeek Response"

mock_chunk = MagicMock()
mock_chunk.choices = [MagicMock()]
mock_chunk.choices[0].delta.content = "Mocked DeepSeek Response"

def mock_create(**kwargs):
    """Mock implementation of the OpenAI create method."""
    if kwargs.get('stream', False):
        return [mock_chunk]
    else:
        return mock_response
