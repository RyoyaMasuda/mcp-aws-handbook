from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from strands.types.content import Messages

# RAGエージェントクラス
class RagAgent:
    def __init__(self):
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
            model=BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0"),
            system_prompt="AWSに関する質問はAWS Knowledge MCPサーバーを用いて回答してください。その参考先も定義してください。",
            tools=tools,
            callback_handler=None,
        )

    async def stream(self, messages: Messages):
        with self.aws_knowledge_mcp_client:
            tools = self.aws_knowledge_mcp_client.list_tools_sync()

            # エージェントの生成
            agent = self.create_agent(
                tools=tools
            )

            # メッセージの返答
            async for event in agent.stream_async(messages):
                if "message" in event:
                    yield event["message"]