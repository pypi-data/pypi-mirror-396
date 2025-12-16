
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
