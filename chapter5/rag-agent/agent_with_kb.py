import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamable_http_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from strands.types.content import Messages

# RAGエージェントクラス
class RagAgent:
    def __init__(self):
        """RAGエージェントを初期化"""
        # AWS Knowledge MCP Serverへの接続
        self.aws_knowledge_mcp_client = self.create_streamable_http_mcp_client("https://knowledge-mcp.global.api.aws")
        
        # AWS Bedrock Knowledge Base Retrieval MCP Serverへの接続設定
        self.aws_kb_mcp_client = self.create_stdio_mcp_client(
            command="uvx",  # uvxコマンドを使用してMCPサーバーを起動
            args=["awslabs.bedrock-kb-retrieval-mcp-server@1.0.13"],
            env={
                "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
                "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "AWS_REGION": "us-west-2",  # AWSリージョン
            }
        )

    def create_streamable_http_mcp_client(self, url: str) -> MCPClient:
        """Streamable HTTP MCPクライアントを作成する関数"""
        streamable_http_mcp_client = MCPClient(
            lambda: streamable_http_client(url),
            startup_timeout=60
        )
        return streamable_http_mcp_client

    def create_stdio_mcp_client(self, command: str, args: list[str], env: dict) -> MCPClient:
        """stdio MCPクライアントを作成する関数"""
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
            model=BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0"),
            system_prompt="AWSに関する質問はAWS Knowledge MCP Serverを用いて、システム設計情報についてはBedrock Knowledge Retrieval Base MCP Serverを用いて回答してください。その参考先も定義してください。",
            tools=tools,
            callback_handler=None,
        )

    async def stream(self, messages: Messages):
        with self.aws_knowledge_mcp_client,  self.aws_kb_mcp_client:
            tools = self.aws_knowledge_mcp_client.list_tools_sync()
            tools.extend(self.aws_kb_mcp_client.list_tools_sync())

            # エージェントの生成
            agent = self.create_agent(
                tools=tools
            )

            # メッセージの返答
            async for event in agent.stream_async(messages):
                if "message" in event:
                    yield event["message"]