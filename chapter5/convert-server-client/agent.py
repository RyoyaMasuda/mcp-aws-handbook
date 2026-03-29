import os
from pathlib import Path
from dotenv import load_dotenv
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client
from mcp_proxy_for_aws.utils import determine_service_name
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from typing import List, Dict

load_dotenv(Path(__file__).parent.parent.parent / ".env")
# AgentCore Runtime ARN
# AgentCore RuntimeのコンソールでAgent ARNを確認し、ここに設定する
AGENTCORE_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-west-2:035261964577:runtime/convert_server-kjZTNh6BGz"


def create_stdio_mcp_client(command: str, args: List[str], env: Dict) -> MCPClient:
    """Stdio MCPクライアントを作成する関数"""
    # コマンドライン経由でMCPサーバーと通信するクライアントを生成する
    # startup_timeout: サーバー起動を最大60秒待機する
    stdio_mcp_client = MCPClient(
        lambda: stdio_client(StdioServerParameters(command=command, args=args, env=env)),
        startup_timeout=60
    )
    return stdio_mcp_client


def create_aws_iam_streamable_http_mcp_client(
    url: str,
    aws_service: str = "bedrock-agentcore"
) -> MCPClient:
    """MCP Proxy for AWSを利用したMCPクライアントを作成する関数"""
    # AWS IAM認証付きのHTTPストリーミングでMCPサーバーと通信するクライアントを生成する
    # terminate_on_close=False: セッション終了時にサーバープロセスを終了しない
    streamable_http_mcp_client = MCPClient(
        lambda: aws_iam_streamablehttp_client(
            endpoint=url,
            aws_service=aws_service,
            aws_region="us-west-2",
            terminate_on_close=False,
        )
    )
    return streamable_http_mcp_client


def get_mcp_endpoint() -> str:
    # ARN内の特殊文字をURLエンコードしてエンドポイントURLを生成する
    # ":"→"%3A"、"/"→"%2F" に変換してURLに埋め込む
    encoded_arn = AGENTCORE_RUNTIME_ARN.replace(":", "%3A").replace("/", "%2F")
    return f"https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"


# エージェントに与えるプロンプト
# DynamoDBからデータを取得し、PPT変換後にダウンロードURLを返すよう指示する
prompt = """
DynamoDBのtech-reportテーブルから最新の技術レポートを取得して、それをPPT形式に変換してください。
完了後は変換したファイルを取得するURLをユーザーへ明示してください。
"""


def main():
    # AgentCoreのMCPエンドポイントURLを取得する
    mcp_endpoint = get_mcp_endpoint()

    # AgentCore RuntimeへのHTTPストリーミングMCPクライアントを作成する
    gateway_server_client = create_aws_iam_streamable_http_mcp_client(mcp_endpoint)

    # AWS公式MCPサーバー（DynamoDB等のAWSサービス操作用）のクライアントを作成する
    # uvxでmcp-proxy-for-awsを起動し、AWS_ACCESS_KEY_IDとAWS_SECRET_ACCESS_KEYを渡して認証する
    aws_mcp_client = create_stdio_mcp_client(
        command="uvx",
        args=[
            "mcp-proxy-for-aws@1.1.5",
            "https://aws-mcp.us-east-1.api.aws/mcp",
            "--metadata", "AWS_REGION=us-west-2"
        ],
        env={
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
        }
    )

    # 両方のMCPクライアントをコンテキストマネージャーで起動・終了を管理する
    with gateway_server_client, aws_mcp_client:
        # 各MCPサーバーが提供するツール一覧を取得してマージする
        tools = gateway_server_client.list_tools_sync()
        tools.extend(aws_mcp_client.list_tools_sync())

        # Bedrockのモデルを定義
        model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0")

        # エージェントを初期化（モデルとツール一覧を渡す）
        agent = Agent(
            model=model,
            tools=tools
        )

        # プロンプトをエージェントに渡して実行する
        agent(prompt)


if __name__ == "__main__":
    main()
