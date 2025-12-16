""" Some tests need appropriate API-KEY for the OpenAI API.

"""
import os
import sys
import io
import pytest
import aici
import pyperclip
from  aici import __version__

class Testaici:

    def test_keysetting(self):
        assert os.getenv('OPENAI_API_KEY') is not None, "OPENAI_API_KEY is not set"

    def test_version(self, monkeypatch, capsys):
        test_args = ['aici', '-v']
        monkeypatch.setattr(sys, 'argv', test_args)

        # Catch the SystemExit to prevent the test from failing
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            aici.main()

        # Ensure the SystemExit code is 0
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

        # Capture the output and check if the version was printed
        captured = capsys.readouterr()
        assert __version__ in captured.out

    def test_query(self, monkeypatch):
        # REAL CALL to API
        test_args = ['aici', 'Hello']
        monkeypatch.setattr(sys, 'argv', test_args)
        try:
            aici.main()
        except Exception as e:
            pytest.fail(f"command error: {e}")
            
    def test_query_with_model(self, monkeypatch):
        # REAL CALL to API
        test_args = ['aici', 'Hello', '--model=gpt-4o-mini-2024-07-18']
        monkeypatch.setattr(sys, 'argv', test_args)
        try:
            aici.main()
        except Exception as e:
            pytest.fail(f"command error: {e}")
            
    def test_query_with_system(self, monkeypatch):
        # REAL CALL to API
        test_args = ['aici', 'Hello', '--system="answer in Japnese Romaji only"']
        monkeypatch.setattr(sys, 'argv', test_args)
        try:
            aici.main()
        except Exception as e:
            pytest.fail(f"command error: {e}")
            
    def test_option_complete(self, monkeypatch):
        # REAL CALL to API
        test_args = ['aici', 'Hello', '--complete']
        monkeypatch.setattr(sys, 'argv', test_args)
        try:
            aici.main()
        except Exception as e:
            pytest.fail(f"command error: {e}")
            
    def test_option_clipboard(self, monkeypatch):
        # REAL CALL to API
        test_args = ['aici', 'Hello', '--output=clip']
        monkeypatch.setattr(sys, 'argv', test_args)
        try:
            aici.main()
        except Exception as e:
            pytest.fail(f"command error: {e}")
            
    def test_option_ai_out(self, monkeypatch):
        # REAL CALL to API
        # clipboard output
        test_args = ['aici', 'Hello', '--output=clip', '--system="すべてローマ字で答える"']
        monkeypatch.setattr(sys, 'argv', test_args)

        # to mock sys.stdout, using StringIO 
        mock_stdout = io.StringIO()
        monkeypatch.setattr(sys, 'stdout', mock_stdout)

        try:
            aici.main()
            clipboard_output = pyperclip.paste()

            assert all(ord(char) < 128 for char in clipboard_output), \
                f"Output contains non-ASCII characters: CONTENT:<<{clipboard_output}>>"

        except Exception as e:
            pytest.fail(f"command error: {e}")
            
