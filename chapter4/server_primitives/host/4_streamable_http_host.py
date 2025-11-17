import asyncio

import streamlit as st
from mcp import (
    ClientSession,
    GetPromptResult,
    ListPromptsResult,
)
from mcp.client.streamable_http import streamablehttp_client
from strands.agent import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPAgentTool, MCPClient
from strands.types.content import ContentBlock, Message


def with_mcp_client(func) -> ClientSession:
    async def wrapper(*args, **kwargs):
        mcp_client = MCPClient(
            lambda: streamablehttp_client(url="http://localhost:8000/mcp")
        )  # streamablehttp_clientからMCPClientを生成するよう変更

        with mcp_client:
            return await func(mcp_client, *args, **kwargs)

    return wrapper


@with_mcp_client
async def main(mcp_client: MCPClient):
    st.title("Chat with MCP")

    # Prompts
    with st.sidebar:
        st.subheader("Prompts")
        list_prompts: ListPromptsResult = (
            mcp_client.list_prompts_sync()
        )  # MCP SDKを使用するときと異なる方法で指定
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
            )  # MCP SDKを使用するときと異なる方法で指定
            st.session_state.chat_input = result.messages[0].content.text

    with st.sidebar:
        st.divider()
        st.subheader("Tools")
        list_tools = mcp_client.list_tools_sync()

        select_tool: list[MCPAgentTool] = []
        for tool in list_tools:
            if st.checkbox(tool.tool_name, value=True):
                select_tool.append(tool)

    if input := st.chat_input(key="chat_input"):
        user_content: list[ContentBlock] = []

        user_content.append({"text": input})
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
            callback_handler=None,
        )

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
