# 非同期処理を行うための標準ライブラリ
import asyncio
# Jupyter/Streamlit環境でネストされた非同期ループを許可するライブラリ
import nest_asyncio
# WebアプリUIを構築するStreamlitライブラリ
import streamlit as st
# Knowledge Base対応のRAGエージェントクラスをインポート
from agent_with_kb import RagAgent # ここを変更

# ネストされた非同期ループを有効化
nest_asyncio.apply()

# Streamlitのページ設定
st.set_page_config(page_title="RAGチャットアプリ", page_icon="🤖")

# タイトルを描画
st.title("RAGチャットアプリ")

# 会話履歴の初期化
# セッションにmessagesキーが存在しない場合のみ空リストで初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# RAGAgentの初期化
# セッションにagentキーが存在しない場合のみRagAgentのインスタンスを生成
if "agent" not in st.session_state:
    st.session_state.agent = RagAgent()

# メッセージを画面に表示する関数
def print_message(message):
    # メッセージのrole（user/assistant）に応じたチャットUIで表示
    with st.chat_message(message["role"]):
        # メッセージのコンテンツを1つずつ処理
        for content in message["content"]:
            # テキストコンテンツがある場合は通常表示
            if "text" in content:
                st.write(content["text"])
            # ツール使用情報がある場合は折りたたみ表示
            if "toolUse" in content:
                with st.expander("toolUse", expanded=False):
                    st.write(content["toolUse"])
            # ツール実行結果がある場合は折りたたみ表示
            if "toolResult" in content:
                with st.expander("toolResult", expanded=False):
                    st.write(content["toolResult"])

# メインの非同期処理関数
async def main():
    # 会話履歴の表示
    for message in st.session_state.messages:
        print_message(message)

    # チャット入力
    # ユーザーが入力した場合のみ処理を実行
    if prompt := st.chat_input("質問を入力してください..."):
        # ユーザーメッセージを追加
        st.session_state.messages.append({"role": "user", "content": [{"text": prompt}]})
        # ユーザーのメッセージをチャットUIに表示
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # ローディングスピナーを表示しながらエージェントに問い合わせ
            with st.spinner("回答を生成中..."):
                # エージェントからストリームでメッセージを受け取り逐次表示
                async for message in st.session_state.agent.stream(st.session_state.messages):
                    print_message(message)
                    # 受け取ったメッセージを会話履歴に追加
                    st.session_state.messages.append(message)

        # 例外が発生した場合はエラーメッセージを表示
        except Exception as e:
            st.write(f"エラーが発生しました: {e}")

# スクリプトが直接実行された場合にmain関数を起動
if __name__ == "__main__":
    asyncio.run(main())
