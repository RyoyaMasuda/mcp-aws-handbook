import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from strands.types.content import Messages
from typing import List, Dict

# RAGエージェントクラス
class RagAgent:
    def __init__(self):
        """RAGエージェントを初期化"""
        # AWS MCP Serverへの接続
        self.aws_mcp_client = self.create_stdio_mcp_client(
            command="uvx",
            args=[
                "mcp-proxy-for-aws@1.1.5",
                "https://aws-mcp.us-east-1.api.aws/mcp",
                "--metadata", "AWS_REGION=us-west-2"
            ],
            env={
                "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
                "AWS_SECRET_ACCESS_KEY":os.getenv("AWS_SECRET_ACCESS_KEY"),
            }
        )

    def create_stdio_mcp_client(self, command: str, args: List[str], env: Dict) -> MCPClient:
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
            system_prompt="AWSに関する質問はAWS MCP Serverを用いて回答してください。その参考先も明記してください。",
            tools=tools,
            callback_handler=None,
        )

    async def stream(self, messages: Messages):
        with self.aws_mcp_client:
            tools = self.aws_mcp_client.list_tools_sync()

            # エージェントの生成
            agent = self.create_agent(
                tools=tools
            )

            # メッセージの返答
            async for event in agent.stream_async(messages):
                if "message" in event:
                    yield event["message"]