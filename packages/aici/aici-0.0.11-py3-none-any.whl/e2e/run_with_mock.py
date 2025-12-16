#!/usr/bin/env python
"""Run the aici CLI with mocked API responses.

This script is used to run the aici CLI with mocked API responses for e2e testing.
"""

import os
import sys
import importlib.util

mock_module_path = os.path.join(os.path.dirname(__file__), "mock_openai.py")
if os.path.exists(mock_module_path):
    spec = importlib.util.spec_from_file_location("mock_openai", mock_module_path)
    mock_openai = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mock_openai)

from aici.main import main

if __name__ == "__main__":
    os.environ.setdefault('DEEPSEEK_API_KEY', 'sk-dummy-api-key-for-testing')
    
    sys.argv[0] = "aici"  # Set the program name
    main()
