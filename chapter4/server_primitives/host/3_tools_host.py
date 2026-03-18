import asyncio

from mcp import (
    ClientSession,
    GetPromptResult,
    ListPromptsResult,
    StdioServerParameters,
)

import streamlit as st
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Resource
from strands.agent import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient, MCPAgentTool
from strands.types.content import ContentBlock, Message


# デコレータ関数を定義
def with_mcp_client(func) -> ClientSession:
    async def wrapper(*args, **kwargs):
        server_params = StdioServerParameters(
            command="uv",
            args=[
                "run",
                "--directory",
                "../server",
                "3_tools_server.py",
            ],
            env={},
        )

        mcp_client = MCPClient(lambda: stdio_client(server_params))

        with mcp_client:
            return await func(mcp_client, *args, **kwargs)

    return wrapper

# ClientSessionはmcpからインポートしている。list_promptでpromptsプリミティブのメソッドである「prompts/list」をmcpサーバーに送っている。
@with_mcp_client
async def main(mcp_client: MCPClient):
    st.title("Chat with MCP")

    with st.sidebar:
        st.subheader("Prompts")
        # list_promptでpromptsプリミティブのメソッドである「prompts/list」をmcpサーバーに送っている。
        list_prompts: ListPromptsResult = (
            mcp_client.list_prompts_sync()
        )
        # st.write(f"{list_prompts}")
        # print(type(list_prompts))
        prompt_names = [prompt.name for prompt in list_prompts.prompts]
        select_prompt_name = st.selectbox("プロンプトを選択", prompt_names)

        select_prompt = list(
            filter(
                lambda x: x.name == select_prompt_name,
                list_prompts.prompts,
            )
        )[0]

        st.text("パラメーター")
        args = {}
        for argument in select_prompt.arguments:
            value = st.text_input(
                label=argument.name,
                placeholder=argument.description,
            )
            args[argument.name] = value

        if st.button("プロンプトをセット"):
            result: GetPromptResult = mcp_client.get_prompt_sync(
                select_prompt_name, args=args
            )  # MCPサーバーからPrompts情報を取得
            st.session_state.chat_input = result.messages[0].content.text

    with st.sidebar:
        st.divider()
        st.subheader("Tools")
        list_tools = mcp_client.list_tools_sync()

        select_tool: list[MCPAgentTool] = []
        for tool in list_tools:
            if st.checkbox(tool.tool_name, value=True):
                select_tool.append(tool)

    if input := st.chat_input(
        key="chat_input"
    ):  # keyの指定を追加。該当のkeyで保持された値がセットされる
        user_content: list[ContentBlock] = []

        user_content.append({"text": input})
        # user_contentが後で（このあとのfor文で）更新されるとuser_messageも更新される（参照渡し）
        user_message: Message = {"role": "user", "content": user_content}

        for content in user_content:
            with st.chat_message("user"):
                st.write(content["text"])

        model = BedrockModel(
            model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            region_name="us-west-2",
        )

        agent = Agent(
            model=model, 
            tools=select_tool,
            callback_handler=None)

        # st.write(user_message)

        agent_stream = agent.stream_async([user_message])

        async for event in agent_stream:
            if "message" in event:
                message: Message = event["message"]

                with st.chat_message(message["role"]):
                    for content in message["content"]:
                        if "text" in content:
                            st.write(content["text"])
                        else:
                            st.json(content, expanded=1)


if __name__ == "__main__":
    asyncio.run(main())
