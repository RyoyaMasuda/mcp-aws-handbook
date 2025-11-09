import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from typing import List, Dict
import requests

# AgentCore Runtime ARN
AGENTCORE_RUNTIME_ARN = "<AgentCore RuntimeのAgent ARN>"

def create_stdio_mcp_client(command: str, args: List[str], env: Dict) -> MCPClient:
    """Stdio MCPクライアントを作成する関数"""
    stdio_mcp_client = MCPClient(
        lambda: stdio_client(StdioServerParameters(command=command, args=args, env=env)),
        startup_timeout=60
    )
    return stdio_mcp_client


def create_streamable_http_mcp_client(url: str, headers: str) -> MCPClient:
    """Streamable HTTP MCPクライアントを作成する関数"""
    streamable_http_mcp_client = MCPClient(
        lambda: streamablehttp_client( url, headers=headers),
        startup_timeout=60
    )
    return streamable_http_mcp_client

def get_mcp_endpoint() -> str:
    encoded_arn = AGENTCORE_RUNTIME_ARN.replace(":", "%3A").replace("/", "%2F")
    return f"https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"

def get_token():
    response = requests.post(
        "https://us-west-xxxxx.auth.us-west-2.amazoncognito.com/oauth2/token",
        data="grant_type=client_credentials&client_id=<クライアントID>&client_secret=<クライアントシークレット>&scope=default-m2m-resource-server-xxxx/read",
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    jwtToken = response.json()["access_token"]
    return jwtToken

prompt = """
DynamoDBのtech_topic_reportから最新の技術レポートを取得して、それをPPT形式に変換してください。
完了後は変換したファイルを取得するURLをユーザへ明示してください。
"""
def main():
    mcp_endpoint = get_mcp_endpoint()
    token = get_token()
    headers = {"authorization": f"Bearer {token}","Content-Type":"application/json"}

    gateway_server_cleint = create_streamable_http_mcp_client(mcp_endpoint, headers)
    dynamodb_client = create_stdio_mcp_client(
        command="uvx",  # npxコマンドを使用してMCPサーバーを起動
        args=["awslabs.aws-api-mcp-server@latest"],
        env={
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY":os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_REGION": "us-west-2",
        }
    )
    with gateway_server_cleint, dynamodb_client:
        tools = gateway_server_cleint.list_tools_sync()
        tools.extend(dynamodb_client.list_tools_sync())
        # Bedrockのモデルを定義
        model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0")
        # エージェントを初期化
        agent = Agent(
            model=model,
            tools=tools
        )
        agent(prompt)

if __name__ == "__main__":
    main()
