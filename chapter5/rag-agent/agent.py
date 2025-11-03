import os
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

    def create_streamable_http_mcp_client(self, url: str) -> MCPClient:
        """Streamable HTTP MCPクライアントを作成する関数"""
        streamable_http_mcp_client = MCPClient(
            lambda: streamablehttp_client(url),
            startup_timeout=60
        )
        return streamable_http_mcp_client

    def create_agent(self, tools: list):
        # エージェントを初期化
        return Agent(
            name="質問回答エージェント",
            model=BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0"),
            system_prompt="AWSに関する質問はAWS Knowledge MCPサーバーを用いて回答してください。その参考先も定義してください。",
            tools=tools,
            callback_handler=None,
        )

    async def stream(self, query: str):
        with self.aws_knowledge_mcp_client:
            tools = self.aws_knowledge_mcp_client.list_tools_sync()

            # Create orchestrator agent (clients are now accessible via session manager)
            agent = self.create_agent(
                tools=tools
            )

            # Stream the orchestrator response
            async for event in agent.stream_async(query):
                if "data" in event:
                    yield event["data"]