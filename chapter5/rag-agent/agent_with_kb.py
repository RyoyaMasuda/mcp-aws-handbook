import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from typing import  Dict, List

# RAGエージェントクラス
class RagAgent:
    def __init__(self, aws_profile: str = "dev", aws_region: str = "us-west-2"):
        """RAGエージェントを初期化"""
        # AWS公式Knowledge MCPサーバーへの接続
        self.aws_knowledge_mcp_client = self.create_streamable_http_mcp_client("https://knowledge-mcp.global.api.aws")
        # AWS Bedrock Knowledge Base MCPサーバーへの接続設定
        self.aws_kb_mcp_client = self.create_stdio_mcp_client(
            command="uvx",  # uvxコマンドを使用してMCPサーバーを起動
            args=["awslabs.bedrock-kb-retrieval-mcp-server@latest"],  # AWS Labs提供のKB検索MCPサーバー
            env={
                "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
                "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "AWS_REGION": "us-west-2",  # AWSリージョン
            }
        )

    def create_streamable_http_mcp_client(self, url: str) -> MCPClient:
        """Streamable HTTP MCPクライアントを作成する関数"""
        streamable_http_mcp_client = MCPClient(
            lambda: streamablehttp_client(url),
            startup_timeout=60
        )
        return streamable_http_mcp_client

    def create_stdio_mcp_client(self, command: str, args: List[str], env: Dict) -> MCPClient:
        """Stdio MCPクライアントを作成する関数"""
        stdio_mcp_client = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(command=command, args=args, env=env)
            ),
            startup_timeout=60
        )
        return stdio_mcp_client

    def create_agent(self, tools: list):
        # エージェントを初期化
        return Agent(
            name="質問回答エージェント",
            model=BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0"),
            system_prompt="AWSで構築したシステムの構成設定に関してはBedrock Knowledge Base MCPサーバーを用いて回答してください。AWSに関する質問はAWS Knowledge MCPサーバを用いて、その参考先も定義してください。",
            tools=tools,
            callback_handler=None,
        )

    async def stream(self, query: str):
        with self.aws_knowledge_mcp_client, self.aws_kb_mcp_client:
            tools = self.aws_knowledge_mcp_client.list_tools_sync()
            tools.extend(self.aws_kb_mcp_client.list_tools_sync())

            # Create orchestrator agent (clients are now accessible via session manager)
            agent = self.create_agent(
                tools=tools
            )

            # Stream the orchestrator response
            async for event in agent.stream_async(query):
                if "data" in event:
                    yield event["data"]