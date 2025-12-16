"""
i18n module for aici

This module provides internationalization support for the aici CLI.
"""

import os
import locale
from typing import Dict, Any

# Currently supported languages
SUPPORTED_LANGUAGES = ['en', 'ja']

# Default language
DEFAULT_LANGUAGE = 'en'

# Get language setting
def get_language() -> str:
    """
    Get the current language setting.

    Returns:
        str: Language code ('en', 'ja', etc.)
    """
    # Get language setting from environment variable
    lang = os.environ.get('AICI_LANG')

    # Use system locale if environment variable is not set
    if not lang:
        try:
            system_locale, _ = locale.getlocale()
            if system_locale:
                lang = system_locale.split('_')[0]
        except (ValueError, AttributeError):
            pass

    # Check if the language is supported
    if lang and lang in SUPPORTED_LANGUAGES:
        return lang

    return DEFAULT_LANGUAGE

# Message dictionary
MESSAGES: Dict[str, Dict[str, str]] = {
    'en': {
        # Error messages
        'error_api_quota': "Error: API quota limit reached",
        'error_api_connection': "Error: Could not connect to OpenAI server",
        'error_api_status': "Error: An error occurred with the OpenAI API (status code: {status_code})",
        'error_unexpected': "Error: An unexpected problem occurred",

        # Rate limit messages
        'rate_limit_retry': "Temporary API rate limit reached. Retrying in {sleep_time:.1f} seconds ({retry_count}/{max_retries})...",

        # Solution messages
        'solutions_header': "Try the following solutions:",
        'solution_check_dashboard': "1. Check your usage on the OpenAI dashboard (https://platform.openai.com/)",
        'solution_check_billing': "2. Ensure your billing information is up to date",
        'solution_upgrade_plan': "3. Consider upgrading your plan if you need higher quotas",
        'solution_contact_support': "4. Contact OpenAI support if the problem persists",

        # Internet connection messages
        'check_internet': "Check your internet connection and try again later.",

        # API related messages
        'api_retry_later': "Try again later. If the problem persists, check your API key.",

        # Verbose info messages
        'verbose_info': "For detailed error information, use the -V or --verbose option.",

        # Config file related messages
        'config_not_found': "Configuration file not found. Please create a configuration file in one of the following locations:",
        'config_template_header': "\nConfiguration file template:",
        'config_template_comment': "# OpenAI API Settings",
        'api_key_info': "\nYou can get your OpenAI API key from https://platform.openai.com/api-keys",
        'api_key_env_info': "Alternatively, you can set your API key directly in the OPENAI_API_KEY environment variable.",
        'config_not_found_error': "Configuration file not found. Please refer to the instructions above to set it up.",
        'api_key_not_set': "API key is not set. Please set your API key using one of the following methods:",
        'api_key_config_option': "1. Add OPENAI_API_KEY=your_api_key_here to your configuration file",
        'api_key_env_option': "2. Set the OPENAI_API_KEY environment variable",
        'api_key_not_found': "API key information not found.",
    },
    'ja': {
        # Error messages
        'error_api_quota': "エラー: APIクォータ制限に達しました",
        'error_api_connection': "エラー: OpenAIサーバーに接続できませんでした",
        'error_api_status': "エラー: OpenAI APIでエラーが発生しました（ステータスコード: {status_code}）",
        'error_unexpected': "エラー: 予期しない問題が発生しました",

        # Rate limit messages
        'rate_limit_retry': "一時的なAPIレート制限に達しました。{sleep_time:.1f}秒後に再試行します（{retry_count}/{max_retries}）...",

        # Solution messages
        'solutions_header': "以下の対処方法を試してください:",
        'solution_check_dashboard': "1. OpenAIダッシュボード（https://platform.openai.com/）で使用状況を確認",
        'solution_check_billing': "2. 請求情報が最新であることを確認",
        'solution_upgrade_plan': "3. より高いクォータが必要な場合は、プランのアップグレードを検討",
        'solution_contact_support': "4. 問題が解決しない場合は、OpenAIサポートに連絡",

        # Internet connection messages
        'check_internet': "インターネット接続を確認し、しばらくしてから再度お試しください。",

        # API related messages
        'api_retry_later': "しばらくしてから再度お試しください。問題が続く場合は、APIキーを確認してください。",

        # Verbose info messages
        'verbose_info': "詳細なエラー情報を確認するには、-V または --verbose オプションを使用してください。",

        # Config file related messages
        'config_not_found': "コンフィグファイルが見つかりません。以下のいずれかの場所にコンフィグファイルを作成してください：",
        'config_template_header': "\nコンフィグファイルのテンプレート:",
        'config_template_comment': "# OpenAI API設定",
        'api_key_info': "\nOpenAI APIキーは https://platform.openai.com/api-keys から取得できます。",
        'api_key_env_info': "または、環境変数 OPENAI_API_KEY に直接APIキーを設定することもできます。",
        'config_not_found_error': "コンフィグファイルが見つかりません。上記の説明を参考に設定してください。",
        'api_key_not_set': "APIキーが設定されていません。以下のいずれかの方法でAPIキーを設定してください：",
        'api_key_config_option': "1. コンフィグファイルに OPENAI_API_KEY=your_api_key_here を追加",
        'api_key_env_option': "2. 環境変数 OPENAI_API_KEY にAPIキーを設定",
        'api_key_not_found': "APIキー情報が見つかりません。",
    }
}

def get_message(key: str, **kwargs: Any) -> str:
    """
    Get a localized message.
    
    Args:
        key (str): Message key
        **kwargs: Format parameters for the message
        
    Returns:
        str: Localized message
    """
    lang = get_language()

    # Get messages for the specified language
    messages = MESSAGES.get(lang, MESSAGES[DEFAULT_LANGUAGE])

    # Get from default language if key doesn't exist
    message = messages.get(key)
    if message is None and lang != DEFAULT_LANGUAGE:
        message = MESSAGES[DEFAULT_LANGUAGE].get(key, f"Missing message: {key}")
    elif message is None:
        message = f"Missing message: {key}"

    # Apply format parameters if any
    if kwargs:
        try:
            message = message.format(**kwargs)
        except KeyError:
            pass
    
    return message
