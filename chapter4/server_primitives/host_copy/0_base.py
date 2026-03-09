import asyncio

import streamlit as st
from strands.agent import Agent
from strands.models import BedrockModel
from strands.types.content import ContentBlock, Message


async def main():
    st.title("Chat with MCP")

    if input := st.chat_input():
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

        agent = Agent(model=model, callback_handler=None)

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
