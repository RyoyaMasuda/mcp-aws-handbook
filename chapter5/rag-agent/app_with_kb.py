import asyncio
import nest_asyncio
import streamlit as st
from agent_with_kb import RagAgent

nest_asyncio.apply()

# Streamlitのページ設定
st.set_page_config(page_title="RAG エージェント チャット", page_icon="🤖")

# タイトルを描画
st.title("RAGエージェント チャット")

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

agent = RagAgent()

async def main():
    # 会話履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # チャット入力
    if prompt := st.chat_input("質問を入力してください..."):
        # ユーザーメッセージを追加
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # アシスタントの応答
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
               
            # ストリーミング応答を表示
            try:
                async for chunk in agent.stream(prompt):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                   
                # 最終的な応答を表示（カーソルを削除）
                message_placeholder.markdown(full_response)
                   
            except Exception as e:
                error_message = f"エラーが発生しました: {e}"
                message_placeholder.markdown(error_message)
                full_response = error_message
           
            # アシスタントメッセージを履歴に追加
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )

if __name__ == "__main__":
    asyncio.run(main())
