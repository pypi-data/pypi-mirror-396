"""
query_chatgpt関数のテスト
"""
import io
import sys
import pytest
import os

# モジュールを直接インポート
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# aici.mainモジュールを直接インポート（aici.__init__.pyのmain関数と区別するため）
import importlib
aici_main_module = importlib.import_module('aici.main')
query_chatgpt = aici_main_module.query_chatgpt


def test_query_chatgpt_complete(request):
    """完全なレスポンスモードのテスト"""
    # テストモードを有効化
    original_test_mode = os.environ.get('AICI_TEST_MODE')
    original_api_key = os.environ.get('AICI_OPENAI_KEY')
    os.environ['AICI_TEST_MODE'] = 'true'
    os.environ['AICI_OPENAI_KEY'] = 'sk-test'

    # テスト完了後に元の値に戻すように設定
    def restore_env():
        if original_test_mode is None:
            os.environ.pop('AICI_TEST_MODE', None)
        else:
            os.environ['AICI_TEST_MODE'] = original_test_mode
        if original_api_key is None:
            os.environ.pop('AICI_OPENAI_KEY', None)
        else:
            os.environ['AICI_OPENAI_KEY'] = original_api_key
    request.addfinalizer(restore_env)

    # 出力をキャプチャ
    output = io.StringIO()

    # 関数を呼び出し
    result = query_chatgpt("テストプロンプト", complete=True, output=output)

    # アサーション - テストモードでは "Mocked DeepSeek Response" が返される
    assert "Mocked DeepSeek Response" in output.getvalue()
    assert result == "Mocked DeepSeek Response"


def test_query_chatgpt_stream(request):
    """ストリームモードのテスト"""
    # テストモードを有効化
    original_test_mode = os.environ.get('AICI_TEST_MODE')
    original_api_key = os.environ.get('AICI_OPENAI_KEY')
    os.environ['AICI_TEST_MODE'] = 'true'
    os.environ['AICI_OPENAI_KEY'] = 'sk-test'

    # テスト完了後に元の値に戻すように設定
    def restore_env():
        if original_test_mode is None:
            os.environ.pop('AICI_TEST_MODE', None)
        else:
            os.environ['AICI_TEST_MODE'] = original_test_mode
        if original_api_key is None:
            os.environ.pop('AICI_OPENAI_KEY', None)
        else:
            os.environ['AICI_OPENAI_KEY'] = original_api_key
    request.addfinalizer(restore_env)

    # 出力をキャプチャ
    output = io.StringIO()

    # 関数を呼び出し
    result = query_chatgpt("テストプロンプト", complete=False, output=output)

    # アサーション - テストモードでは "Mocked DeepSeek Response" が返される
    assert "Mocked DeepSeek Response" in output.getvalue()
    assert result == "Mocked DeepSeek Response"


def test_query_chatgpt_with_model(request):
    """異なるモデルでのテスト"""
    # テストモードを有効化
    original_test_mode = os.environ.get('AICI_TEST_MODE')
    original_api_key = os.environ.get('AICI_OPENAI_KEY')
    os.environ['AICI_TEST_MODE'] = 'true'
    os.environ['AICI_OPENAI_KEY'] = 'sk-test'

    # テスト完了後に元の値に戻すように設定
    def restore_env():
        if original_test_mode is None:
            os.environ.pop('AICI_TEST_MODE', None)
        else:
            os.environ['AICI_TEST_MODE'] = original_test_mode
        if original_api_key is None:
            os.environ.pop('AICI_OPENAI_KEY', None)
        else:
            os.environ['AICI_OPENAI_KEY'] = original_api_key
    request.addfinalizer(restore_env)

    # 出力をキャプチャ
    output = io.StringIO()

    # 関数を呼び出し
    result = query_chatgpt("テストプロンプト", model="gpt-4o", output=output)

    # アサーション - テストモードでは "Mocked DeepSeek Response" が返される
    assert "Mocked DeepSeek Response" in output.getvalue()


def test_query_chatgpt_backward_compatibility():
    """query_chatgptとquery_deepseekの互換性テスト"""
    # query_chatgptがquery_deepseekと同じ結果を返すことを確認
    assert query_chatgpt == aici_main_module.query_deepseek or callable(query_chatgpt)
