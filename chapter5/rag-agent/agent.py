# オペレーティングシステムと対話するためのモジュールをインポートします（例：環境変数を読み込むため）
import os
# MCPクライアントの標準入出力（stdio）関連の機能とパラメータをインポートします
from mcp.client.stdio import stdio_client, StdioServerParameters
# AIエージェントを作成するための基本クラスをインポートします
from strands import Agent
# AWS Bedrockサービスで使用するAIモデルを定義するためのクラスをインポートします
from strands.models import BedrockModel
# MCP（Multi-Cloud Proxy）クライアントをインポートします
from strands.tools.mcp.mcp_client import MCPClient
# メッセージの型定義をインポートします
from strands.types.content import Messages
# 型ヒントのためにリストと辞書の型をインポートします
from typing import List, Dict
from pathlib import Path

from dotenv import load_dotenv
load_dotenv("/Users/ryoyamasuda/Documents/git-repo-RyoyaMasuda/mcp-aws-handbook/.env")
# RAGエージェントクラスの定義
class RagAgent:
    # RagAgentクラスのコンストラクタです。
    # エージェントが初期化されるときに一度だけ実行されます。
    def __init__(self):
        """RAGエージェントを初期化"""
        # AWS MCP Serverへの接続を設定します
        # self.aws_mcp_clientは、AWSのサービスと通信するためのクライアントになります
        self.aws_mcp_client = self.create_stdio_mcp_client(
            # 実行するコマンド（mcp-proxy-for-awsを起動するためのランナー）
            command="uvx",
            # コマンドに渡す引数のリスト
            args=[
                # 実行するMCPプロキシの特定のバージョン
                "mcp-proxy-for-aws@1.1.5",
                # AWS MCPサービスのAPIエンドポイント
                "https://aws-mcp.us-east-1.api.aws/mcp",
                # メタデータとしてAWSリージョンを設定（ここではus-west-2）
                "--metadata", "AWS_REGION=us-west-2"
            ],
            # コマンドが実行される環境変数の辞書
            env={
                # 環境変数からAWSアクセスキーIDを取得
                "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
                # 環境変数からAWSシークレットアクセスキーを取得
                "AWS_SECRET_ACCESS_KEY":os.getenv("AWS_SECRET_ACCESS_KEY"),
            }
        )

    # 標準入出力（stdio）ベースのMCPクライアントを作成するヘルパー関数です。
    # このクライアントは、AWSサービスへの接続を管理します。
    # Args:
    #     command (str): 実行するコマンド（例: "uvx"）。
    #     args (List[str]): コマンドに渡す引数のリスト。
    #     env (Dict): コマンド実行時に設定する環境変数の辞書。
    # Returns:
    #     MCPClient: 設定されたMCPクライアントのインスタンス。
    def create_stdio_mcp_client(self, command: str, args: List[str], env: Dict) -> MCPClient:
        """stdio MCPクライアントを作成する関数"""
        # MCPClientを作成します。
        # ここでは、stdio_clientを使って外部プロセス（mcp-proxy-for-aws）を起動し、それと通信します。
        stdio_mcp_client = MCPClient(
            # ラムダ関数を使ってstdio_clientを遅延実行します
            # 接続が必要なタイミングで実行される「起動用関数」を渡す。ラムダ式を使うことで即時実行しないで関数そのものを渡している。
            lambda: stdio_client(
                # stdioクライアントのパラメータを設定
                StdioServerParameters(command=command, args=args, env=env)
            ),
            # クライアントが起動するまでの最大待ち時間を60秒に設定
            startup_timeout=60
        )
        # 作成したクライアントを返します
        return stdio_mcp_client

    # AIエージェントを作成する関数です。
    # このエージェントは、与えられたツール（機能）を使ってユーザーの質問に答えます。
    # Args:
    #     tools (list): エージェントが使用できるツールのリスト。
    # Returns:
    #     Agent: 設定されたAIエージェントのインスタンス。
    def create_agent(self, tools: list):
        # エージェントを初期化
        # Agentクラスのインスタンスを作成して返します
        return Agent(
            # 使用するAIモデルを指定（ここではBedrockのClaude Haiku）
            model=BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0"),
            # エージェントの基本的な指示（システムプロンプト）
            system_prompt="AWSに関する質問はAWS MCP Serverを用いて回答してください。その参考先も明記してください。",
            # エージェントが利用できるツールを渡します
            tools=tools,
            # コールバックハンドラー（イベント処理）はここでは設定しません
            callback_handler=None,
        )

    # エージェントとの非同期ストリーミング対話を開始する関数です。
    # ユーザーからのメッセージを受け取り、エージェントが生成した応答をリアルタイムで返します。
    # Args:
    #     messages (Messages): ユーザーからの入力メッセージ。
    # Yields:
    #     dict: エージェントからの応答イベント（例: メッセージの一部）。
    async def stream(self, messages: Messages):
        # self.aws_mcp_clientとの接続を確立し、ブロックを抜けるときに自動的に閉じます
        with self.aws_mcp_client:
            # MCPクライアントを通じて利用可能なツール（機能）のリストを同期的に取得します
            tools = self.aws_mcp_client.list_tools_sync()

            # エージェントの生成
            # 取得したツールを使ってAIエージェントを生成します
            agent = self.create_agent(
                # エージェントにツールを渡します
                tools=tools
            )

            # メッセージの返答
            # エージェントとの非同期ストリーミング対話を開始し、応答イベントを順次処理します
            async for event in agent.stream_async(messages):
                # イベントに「message」キーが含まれている場合
                if "message" in event:
                    # そのメッセージ部分を呼び出し元に返します
                    yield event["message"]