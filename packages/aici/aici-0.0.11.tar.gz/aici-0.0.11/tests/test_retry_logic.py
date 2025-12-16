"""
APIのリトライロジックをテストするためのモジュール
"""
import pytest
import unittest.mock as mock
import sys
import io

# OpenAIのエラークラスをモック
class MockRateLimitError(Exception):
    def __init__(self, message="Rate limit exceeded", response=None):
        self.message = message
        self.response = response
        super().__init__(message)

class MockAPIConnectionError(Exception):
    def __init__(self, message="Connection error"):
        self.message = message
        super().__init__(message)

class MockAPIStatusError(Exception):
    def __init__(self, message="API error", response=None, body=None):
        self.message = message
        self.response = response
        self.body = body
        self.status_code = response.status_code if response else 500
        super().__init__(message)

# モジュールを直接インポート
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # aiciパッケージをインポートできるようにする

# aici.mainモジュールをインポート
import aici.main as aici_main
from aici.main import retry_with_exponential_backoff

# OpenAIのエラークラスをモックに置き換え
# モジュールのエラークラスをモックで置き換え
import openai
openai.RateLimitError = MockRateLimitError
openai.APIConnectionError = MockAPIConnectionError
openai.APIStatusError = MockAPIStatusError


def test_retry_logic_success():
    """正常に動作する関数のテスト"""
    mock_func = mock.Mock(return_value="success")
    decorated_func = retry_with_exponential_backoff(mock_func)
    
    result = decorated_func()
    
    assert result == "success"
    assert mock_func.call_count == 1


def test_retry_logic_rate_limit_then_success():
    """レート制限エラーが発生した後に成功するケース"""
    mock_func = mock.Mock(side_effect=[
        MockRateLimitError("Rate limit exceeded", response=mock.Mock(status_code=429)),
        "success"
    ])
    decorated_func = retry_with_exponential_backoff(mock_func)
    
    result = decorated_func()
    
    assert result == "success"
    assert mock_func.call_count == 2


def test_retry_logic_max_retries_exceeded(monkeypatch):
    """最大リトライ回数を超えるケース"""
    # グローバル変数を直接上書きして、テスト中のリトライ回数を減らす
    original_max_retries = aici_main.MAX_RETRIES
    aici_main.MAX_RETRIES = 2
    
    # テスト完了後に元の値に戻すように設定
    def restore_max_retries():
        aici_main.MAX_RETRIES = original_max_retries
    monkeypatch.addfinalizer(restore_max_retries)
    
    # 常にRateLimitErrorを発生させるモック関数
    mock_func = mock.Mock(side_effect=MockRateLimitError("Rate limit exceeded", response=mock.Mock(status_code=429)))
    decorated_func = retry_with_exponential_backoff(mock_func)
    
    # SystemExitが発生することを確認
    with pytest.raises(SystemExit) as excinfo:
        decorated_func()
    
    # 終了コードが1であることを確認
    assert excinfo.value.code == 1
    # 関数が指定回数呼び出されたことを確認
    assert mock_func.call_count == 3  # 初回 + リトライ2回


def test_retry_logic_other_exception():
    """RateLimitError以外の例外が発生するケース"""
    mock_func = mock.Mock(side_effect=ValueError("Some other error"))
    decorated_func = retry_with_exponential_backoff(mock_func)
    
    with pytest.raises(ValueError) as excinfo:
        decorated_func()
    
    assert str(excinfo.value) == "Some other error"
    assert mock_func.call_count == 1  # リトライなし


def test_retry_logic_api_connection_error():
    """APIConnectionErrorが発生するケース"""
    mock_func = mock.Mock(side_effect=MockAPIConnectionError("Connection error"))
    decorated_func = retry_with_exponential_backoff(mock_func)
    
    with pytest.raises(MockAPIConnectionError) as excinfo:
        decorated_func()
    
    assert "Connection error" in str(excinfo.value)
    assert mock_func.call_count == 1  # リトライなし


def test_retry_logic_api_status_error():
    """APIStatusErrorが発生するケース"""
    mock_func = mock.Mock(side_effect=MockAPIStatusError("API error", response=mock.Mock(status_code=500), body={}))
    decorated_func = retry_with_exponential_backoff(mock_func)
    
    with pytest.raises(MockAPIStatusError) as excinfo:
        decorated_func()
    
    assert "API error" in str(excinfo.value)
    assert mock_func.call_count == 1  # リトライなし
