# ==============================================================================
# 標準ライブラリのインポート
# import文: Pythonの組み込みモジュールや外部ライブラリを読み込む構文
# ==============================================================================

# asyncio: 非同期処理（async/await）を使うための標準ライブラリ
import asyncio

# boto3: AWSをPythonから操作するための公式SDKライブラリ
import boto3

# os: ファイルパスの操作やOSの機能を使うための標準ライブラリ
import os

# tempfile: OSが用意する一時ディレクトリのパスを取得するための標準ライブラリ
import tempfile

# datetime: 日付や時刻を扱うための標準ライブラリ
from datetime import datetime

# typing: 型ヒント（型アノテーション）を書くための標準ライブラリ
# Dict[str, Any] は「キーが文字列、値が何でもよい辞書型」を表す
from typing import Dict, Any

# FastMCP: MCPサーバーを簡単に構築するためのフレームワーク
from mcp.server.fastmcp import FastMCP

# Field: 関数の引数にメタ情報（説明文など）を付与するためのクラス
from pydantic import Field


# ==============================================================================
# MCPサーバーのインスタンス生成
# FastMCP(...) でサーバーオブジェクトを作成し、変数 mcp に代入する
# host="0.0.0.0" はすべてのIPアドレスからの接続を受け付ける設定
# stateless_http=True はHTTPリクエストをステートレス（状態を持たない）で処理する設定
# ==============================================================================
mcp = FastMCP("ConvertServer", host="0.0.0.0", stateless_http=True)


# ==============================================================================
# システムプロンプトの定義
# 三重クォート（"""..."""）: 複数行にわたる文字列（ヒアドキュメント）を定義する構文
# 大文字の変数名はPythonの慣習として「定数」を表す
# ==============================================================================
SYSTEM_PROMPT = """
あなたの責務は入力テキストをMarpフォーマットに変換することです。
入力テキストの構成を考慮して、プレゼンファイルを生成するためのMarpフォーマットに正確に変換してください。


Marpフォーマットでは以下ルールを厳守してください
- スライドの区切りは"---"で設定してください
- 入力テキストの構成を考慮して適切な見出しを設定してください
- 見出しは"#", "##", "###"で表現してください
- 1つのトピックを、1つのスライドにまとめてください
- <header></header>内のテキストをファイル先頭としてください。これ以前にはメタデータ含め一切のテキストを含めないでください。
<header>
---
marp: true
theme: default
paginate: true
---
</header>
"""


# ==============================================================================
# 関数定義: テキストをMarp形式に変換する
# def 関数名(引数: 型) -> 戻り値の型: という構文で関数を定義する
# アンダースコアで始まる関数名（_convert_...）はモジュール内部での使用を意図した慣習
# str = Field(...) は引数のデフォルト値にFieldオブジェクトを設定し、説明文を付与している
# ==============================================================================
def _convert_to_marp_format(text: str = Field(description="Marpフォーマットに変換するテキスト")) -> str:
    """入力テキストをMarpフォーマットに変換する"""

    # boto3.Session() でAWS認証情報（~/.aws/credentials）を読み込むセッションを作成する
    # session.client("bedrock-runtime") でBedrockを操作するクライアントオブジェクトを生成する
    session = boto3.Session()
    client = session.client("bedrock-runtime")

    # client.converse(...) でClaudeモデルにテキスト変換を依頼する
    # modelId: 使用するClaudeモデルのID
    # messages: ユーザーからの入力メッセージをリスト形式で渡す
    # system: モデルへの振る舞いを指定するシステムプロンプトをリスト形式で渡す
    # f"..." はf文字列（フォーマット文字列）で、{変数名}の部分に変数の値を埋め込む構文
    response = client.converse(
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        messages=[{
            "role": "user",
            "content": [{
                "text": f"<入力>{text}</入力>"
            }]
        }],
        system=[{"text": SYSTEM_PROMPT}]
    )

    # response はネストされた辞書型（dict）
    # ["キー名"] でその辞書から値を取り出す
    # response["output"]["message"]["content"][0]["text"] で最終的な変換結果テキストを取得する
    return response["output"]["message"]["content"][0]["text"]


# Marpコマンドの実行ファイルパス（環境にインストールされたmarpコマンドを指す）
MARP_PATH = "marp"


# ==============================================================================
# 非同期関数定義: Marpコマンドを実行してMarkdownをpptxに変換する
# async def は非同期関数を定義する構文
# 非同期関数の中では await を使って他の処理が完了するまで待機できる
# Dict[str, Any] は型ヒントで「文字列キーと任意の値を持つ辞書」を返すことを示す
# ==============================================================================
async def _process_marp(input_file_path: str, output_file_path: str) -> Dict[str, Any]:
    """Marpコマンドを実行してMarkdownファイルをpptxに変換する。"""

    # asyncio.create_subprocess_exec(...) で外部コマンドを非同期サブプロセスとして起動する
    # await を付けることでプロセス起動が完了するまで待機する
    # stdout/stderr=asyncio.subprocess.PIPE はコマンドの出力をプログラム内で受け取る設定
    process = await asyncio.create_subprocess_exec(
        MARP_PATH,
        input_file_path,
        "--output", output_file_path,
        "--theme", "default",
        # --pptx-editable: PowerPoint上で編集可能なpptxを生成するオプション
        "--pptx-editable",
        "--allow-local-files",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # asyncio.wait_for(..., timeout=秒数) でタイムアウト付きで非同期処理を待機する
    # process.communicate() はプロセスの標準出力と標準エラー出力を取得する
    # タプルのアンパック（a, b = ...）で複数の戻り値を変数に代入する
    stdout, stderr = await asyncio.wait_for(
        process.communicate(),
        timeout=60
    )

    # 辞書リテラル {...} で結果をまとめて返す
    # bytes型の stdout/stderr を .decode() でstr型（文字列）に変換する
    # process.returncode は終了コードで、0なら成功、それ以外はエラーを意味する
    return {
        "returncode": process.returncode,
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
        "success": process.returncode == 0
    }


# ==============================================================================
# 関数定義: ファイルをS3にアップロードして署名付きURLを生成する
# 署名付きURL: 一定時間だけファイルをダウンロードできる一時的なURL
# ==============================================================================
def _upload_to_s3(file_name: str, bucket_name: str, key: str) -> str:
    """ファイルをS3にアップロードし、署名付きURLを生成する。"""

    # AWSセッションとS3クライアントを作成する
    # region_name を明示しないと us-east-1 で署名され、署名付きURLが無効になるため指定する
    session = boto3.Session()
    client = session.client("s3", region_name="us-west-2")

    # client.upload_file(ローカルファイルパス, バケット名, S3上のキー名) でアップロードする
    client.upload_file(file_name, bucket_name, key)

    # client.generate_presigned_url(...) で署名付きURLを生成する
    # ClientMethod="get_object": S3からファイルを取得する操作に対してURLを発行する
    # Params: バケット名とS3上のキー名を辞書で指定する
    # ExpiresIn=3600: URLの有効期限を秒単位で指定する（3600秒 = 1時間）
    # HttpMethod="GET": GETリクエスト用のURLを生成する
    response = client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket_name, "Key": key},
        ExpiresIn=3600,
        HttpMethod="GET"
    )

    return response


# アップロード先のS3バケット名（slide-data-<AWSアカウントID> の形式）
BUCKET = "slide-data-035261964577"

# tempfile.gettempdir() でOSの一時ファイル用ディレクトリパスを取得する（例: /tmp）
TEMP_DIR_PATH = tempfile.gettempdir()

# 変換処理で使う一時的なMarkdownファイルの名前
TEMP_FILE_PATH = "report_tmp.md"


# ==============================================================================
# MCPツール関数の定義
# @mcp.tool() はデコレータ構文で、この関数をMCPツールとして登録する
# デコレータ（@から始まる行）は直下の関数に追加の機能を付与する仕組み
# async def で非同期関数として定義し、内部で await を使って非同期処理を行う
# ==============================================================================
@mcp.tool()
async def convert_to_pptx(text: str = Field(description="pptxに変換するテキスト")) -> str:
    """
    入力テキストをPowerPointプレゼンテーション（pptx）に変換する。

    処理フロー:
    1. テキストをMarp形式に変換（Claude使用）
    2. Marp形式のテキストを一時ファイルに保存
    3. Marpコマンドでpptxファイルを生成
    4. 生成されたファイルをS3にアップロード
    5. ダウンロード可能な署名付きURLを返却

    Args:
        text: 変換対象のテキスト

    Returns:
        生成されたpptxファイルのダウンロードURL
    """

    # datetime.now() で現在の日時を取得し、strftime() で書式を指定して文字列に変換する
    # "%Y%m%d_%H%M%S" は「年月日_時分秒」の形式（例: 20260329_153045.pptx）
    # 毎回異なるファイル名にすることでS3上でのファイルの上書きを防ぐ
    output_file_path = datetime.now().strftime("%Y%m%d_%H%M%S") + ".pptx"

    # テキストをMarp形式のMarkdownに変換する（Claude APIを呼び出す）
    marp_text = _convert_to_marp_format(text)

    # with文（コンテキストマネージャ）: ブロックを抜けると自動的にファイルを閉じてくれる構文
    # open(パス, "w", encoding="utf-8") でUTF-8エンコーディングで書き込みモードとしてファイルを開く
    # os.path.join(...) でOSに依存しない形でパスを結合する（/や\を自動で補完する）
    # as f: 開いたファイルオブジェクトを変数 f に代入する
    with open(os.path.join(TEMP_DIR_PATH, TEMP_FILE_PATH), "w", encoding="utf-8") as f:
        # f.write(...) でファイルに文字列を書き込む
        f.write(marp_text)

    # await を付けて非同期関数を呼び出し、Marpコマンドでpptxを生成する
    # この処理が完了するまで待機してから次の行に進む
    await _process_marp(os.path.join(TEMP_DIR_PATH, TEMP_FILE_PATH), os.path.join(TEMP_DIR_PATH, output_file_path))

    # 生成されたpptxをS3にアップロードし、署名付きURLを取得する
    url = _upload_to_s3(os.path.join(TEMP_DIR_PATH, output_file_path), BUCKET, output_file_path)

    return url


# ==============================================================================
# エントリーポイントの定義
# if __name__ == "__main__": はこのファイルを直接実行したときだけ処理を行う構文
# 他のファイルからimportされたときはこのブロックは実行されない
# ==============================================================================
if __name__ == "__main__":
    # mcp.run(transport="streamable-http") でMCPサーバーをHTTPモードで起動する
    mcp.run(transport="streamable-http")
