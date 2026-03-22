# 環境変数を取得するための標準ライブラリ
import os
# MCP（Model Context Protocol）のstdioクライアントと接続パラメータをインポート
from mcp.client.stdio import stdio_client, StdioServerParameters
# Strandsフレームワークのエージェントクラスをインポート
from strands import Agent
# AWS Bedrockモデルクラスをインポート
from strands.models import BedrockModel
# MCPクライアントクラスをインポート
from strands.tools.mcp.mcp_client import MCPClient
# メッセージ型をインポート
from strands.types.content import Messages
# 型ヒント用のListとDictをインポート
from typing import List, Dict

from dotenv import load_dotenv
load_dotenv("/Users/ryoyamasuda/Documents/git-repo-RyoyaMasuda/mcp-aws-handbook/.env")

# RAGエージェントクラス
class RagAgent:
    # コンストラクタ：インスタンス生成時に呼ばれる初期化メソッド
    def __init__(self):
        """RAGエージェントを初期化"""
        # AWS MCP Serverへの接続設定を作成
        self.aws_mcp_client = self.create_stdio_mcp_client(
            # 実行コマンドとしてuvxを指定
            command="uvx",
            # AWS MCP Proxyサーバーのバージョンとエンドポイント、リージョンを指定
            args=[
                "mcp-proxy-for-aws@1.1.5",
                "https://aws-mcp.us-east-1.api.aws/mcp",
                "--metadata", "AWS_REGION=us-west-2"
            ],
            # AWS認証情報を環境変数から取得して渡す
            env={
                "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
                "AWS_SECRET_ACCESS_KEY":os.getenv("AWS_SECRET_ACCESS_KEY"),
            }
        )
        # AWS Bedrock Knowledge Base Retrieval MCP Serverへの接続設定を作成
        self.aws_kb_mcp_client = self.create_stdio_mcp_client(
            # uvxコマンドを使用してMCPサーバーを起動
            command="uvx",
            # Bedrock Knowledge Base Retrievalサーバーのバージョンを指定
            args=["awslabs.bedrock-kb-retrieval-mcp-server@1.0.13"],
            # AWS認証情報とリージョンを環境変数から取得して渡す
            env={
                "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
                "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
                # 使用するAWSリージョンを指定
                # "AWS_REGION": "us-west-2",
                # 間違ってus-east-2にしてしまったので、us-west-2に変更
                "AWS_REGION": "us-east-2",
                # 使用するKnowledge BaseのIDを指定
                "BEDROCK_KB_IDS": os.getenv("BEDROCK_KB_IDS"),
            }
        )

    # stdio経由でMCPクライアントを作成するメソッド
    def create_stdio_mcp_client(self, command: str, args: List[str], env: Dict) -> MCPClient:
        """stdio MCPクライアントを作成する関数"""
        # stdioクライアントをラップしたMCPClientを生成
        stdio_mcp_client = MCPClient(
            # ラムダ関数でstdioクライアントを遅延生成
            lambda: stdio_client(
                # サーバー起動コマンド、引数、環境変数を指定したパラメータを渡す
                StdioServerParameters(command=command, args=args, env=env)
            ),
            # サーバー起動タイムアウトを60秒に設定
            startup_timeout=60
        )
        # 生成したMCPクライアントを返す
        return stdio_mcp_client

    # エージェントを生成するメソッド
    def create_agent(self, tools: list):
        # エージェントを初期化して返す
        return Agent(
            # 使用するBedrockモデルのIDを指定
            model=BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0"),
            # エージェントの振る舞いを定義するシステムプロンプトを設定
            system_prompt="AWSに関する質問はAWS MCP Serverを用いて、システム設計情報についてはBedrock Knowledge Retrieval Base MCP Serverを用いて回答してください。その参考先も明記してください。",
            # 使用するツール一覧を渡す
            tools=tools,
            # コールバックハンドラを無効化
            callback_handler=None,
        )

    # メッセージを非同期ストリームで処理するメソッド
    async def stream(self, messages: Messages):
        # 両方のMCPクライアントをコンテキストマネージャとして起動
        with self.aws_mcp_client,  self.aws_kb_mcp_client:
            # AWS MCP Serverからツール一覧を同期的に取得
            tools = self.aws_mcp_client.list_tools_sync()
            # Knowledge Base MCP Serverのツールを追加
            tools.extend(self.aws_kb_mcp_client.list_tools_sync())

            # エージェントの生成
            agent = self.create_agent(
                # 取得したツール一覧をエージェントに渡す
                tools=tools
            )

            # メッセージの返答
            async for event in agent.stream_async(messages):
                # イベントにメッセージが含まれている場合のみ返す
                if "message" in event:
                    yield event["message"]