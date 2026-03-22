# asyncio: Pythonで非同期処理（複数の処理を並行して動かす仕組み）を行うための標準ライブラリ
import asyncio
# nest_asyncio: Streamlit環境ではすでにイベントループが動いているため、
# その中でさらに asyncio.run() を呼べるようにするためのライブラリ
import nest_asyncio
# streamlit: Webアプリを簡単に作れるライブラリ。Python コードだけでUIを構築できる
import streamlit as st
# agent.py で定義した RAGAgent クラスをインポートする
from agent import RagAgent

# Streamlit 実行環境での非同期処理の競合を解消する設定
nest_asyncio.apply()

# ブラウザのタブに表示されるタイトルとアイコンを設定する
st.set_page_config(page_title="RAGチャットアプリ", page_icon="🤖")

# 画面上部にアプリのタイトルを表示する
st.title("RAGチャットアプリ")

# st.session_state はブラウザをリロードしても値が保持される Streamlit の仕組み
# まだ "messages" キーがなければ空リストで初期化する（会話履歴の保存先）
if "messages" not in st.session_state:
    st.session_state.messages = []

# まだ "agent" キーがなければ RagAgent を生成して保存する
# セッションに保持することで、毎回再生成せず同じエージェントを使い回せる
if "agent" not in st.session_state:
    st.session_state.agent = RagAgent()

# 1件のメッセージを画面に表示する関数
# message は {"role": "user" or "assistant", "content": [...]} の形式
def print_message(message):
    # role に応じたアイコン付きのチャットバブルを表示する
    with st.chat_message(message["role"]):
        for content in message["content"]:
            # テキストコンテンツがあれば表示する
            if "text" in content:
                st.write(content["text"])
            # AIがツールを呼び出した情報があれば折りたたみ表示する
            if "toolUse" in content:
                with st.expander("toolUse", expanded=False):
                    st.write(content["toolUse"])
            # ツールの実行結果があれば折りたたみ表示する
            if "toolResult" in content:
                with st.expander("toolResult", expanded=False):
                    st.write(content["toolResult"])

# アプリのメイン処理。async def にすることで非同期処理として定義する
async def main():
    # セッションに保存されている過去のメッセージを順番に画面へ表示する
    for message in st.session_state.messages:
        print_message(message)

    # 画面下部のチャット入力欄を表示し、ユーザーが送信したテキストを prompt に格納する
    # ":=" はセイウチ演算子。代入と条件判定を同時に行う Python 3.8+ の構文
    if prompt := st.chat_input("質問を入力してください..."):
        # ユーザーの発言をセッションの会話履歴に追加する
        st.session_state.messages.append({"role": "user", "content": [{"text": prompt}]})
        # ユーザーのメッセージを画面に即時表示する
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # スピナー（くるくるアニメーション）を表示しながら AI の回答を待つ
            with st.spinner("回答を生成中..."):
                # agent.stream() はメッセージを非同期で少しずつ返す（ストリーミング）
                # async for を使うことで、返ってくるたびに逐次処理できる
                async for message in st.session_state.agent.stream(st.session_state.messages):
                    # 受信したメッセージを画面に表示する
                    print_message(message)
                    # 会話履歴にも追加して次回の入力コンテキストに含める
                    st.session_state.messages.append(message)

        except Exception as e:
            # 何らかのエラーが発生した場合はエラー内容を画面に表示する
            st.write(f"エラーが発生しました: {e}")

# このファイルが直接実行された場合のみ main() を呼び出す
# （別ファイルから import されたときは実行されない）
if __name__ == "__main__":
    asyncio.run(main())
