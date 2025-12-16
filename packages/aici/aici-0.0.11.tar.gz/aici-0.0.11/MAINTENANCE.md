#

- git の同期をとる
- ソースコードを修正し始める
- git にこまめに commit していく
- ok なら commit を適当な粒度にまとめて
- push する
- git URL で pip して動作確認
- 問題なければ、 pypi に上げる

# test の実行

`-s` をつけて標準出力を表示しながら確認する.

```bash
% cd test
% python -mpytest -s
```

python -mpip install --upgrade twine
twine upload --repository-url https://test.pypi.org/legacy/ dist/\*

# Prod release

rm -r sdist
rm -r dist

# pip install setuptools wheel

# ビルドする

python setup.py sdist bdist_wheel

# 自動的に upload する

# upload するファイルは新規ファイルのみなのでビルドするまえに

# dist をきれいにしておく.

python -mtwine upload dist/\*

# ビルド課題

copying aici/**main**.py -> build/lib/aici
/Users/taka/.pyenv/versions/3.12.1/lib/python3.12/site-packages/setuptools/\_distutils/cmd.py:66: SetuptoolsDeprecationWarning: setup.py install is deprecated.
!!

        ********************************************************************************
        Please avoid running ``setup.py`` directly.
        Instead, use pypa/build, pypa/installer or other
        standards-based tools.

        See https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html for details.
        ********************************************************************************

!!

# GitHub Actionsで秘密鍵をセキュアに使用する方法

GitHub Actionsでテストやデプロイを自動化する際に、APIキーや秘密鍵などの機密情報を安全に扱う方法を説明します。

## GitHub Secretsの使用

GitHubでは「Secrets」機能を使用して機密情報を安全に管理できます。

### 1. GitHub Secretsの設定方法

1. GitHubリポジトリの「Settings」タブをクリック
2. 左メニューから「Secrets and variables」を選択
3. 「Actions」タブを選択
4. 「New repository secret」ボタンをクリック
5. 名前（例: `OPENAI_API_KEY`）と値を入力
6. 「Add secret」をクリック

### 2. GitHub Actionsワークフローでの使用方法

ワークフローファイル（`.github/workflows/test.yml`など）で以下のように使用します：

```yaml
name: Run Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install tox tox-gh-actions
      - name: Test with tox
        run: tox
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

上記の例では、`${{ secrets.OPENAI_API_KEY }}`の部分でGitHub Secretsから値を安全に取得しています。

## 注意点

1. **ログ出力に注意**: `echo $OPENAI_API_KEY`などでログに出力しないようにします。GitHub Actionsは自動的にログからシークレットをマスクしますが、完全ではありません。

2. **サードパーティアクションに注意**: 信頼できないサードパーティのGitHub Actionsにシークレットを渡すと、情報漏洩のリスクがあります。

3. **シークレットのスコープ**: リポジトリレベル、組織レベル、環境レベルのシークレットがあります。用途に応じて適切なスコープを選択します。

## OpenAI APIキーの安全な使用

NOXやテストをGitHub Actionsで実行する場合、OpenAI APIキーを以下のように安全に使用できます：

1. APIキーをGitHub Secretsに設定
2. テスト用の別のAPIキーを作成し、使用量や権限を制限
3. テストではAPI呼び出しをモック化して実際のAPIを使用しないように実装
