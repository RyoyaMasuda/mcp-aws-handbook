import boto3
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
import requests

# AWS Cognito 認証情報
CLIENT_ID = "<CognitoのクライアントID>"
CLIENT_SECRET =  "<Cognitoのクライアントシークレット>
USER_POOL_ID = "<CognitoのユーザプールID>"
# AgentCore Gateway エンドポイント
GATEWAY_ENDPOINT = "<AgentCore Gatewayのエンドポイント>"

def get_token(client_id, client_secret, user_pool_id):
    client = boto3.client('cognito-idp')
    userpool_info = client.describe_user_pool(UserPoolId=user_pool_id)
   
    """AWS Cognitoからアクセストークンを取得"""    
    response = requests.post(
        f"https://{userpool_info["UserPool"]["Domain"]}.auth.us-west-2.amazoncognito.com/oauth2/token",
        data=f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}",
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    jwtToken = response.json()["access_token"]
    return jwtToken

def create_streamable_http_mcp_client(url: str, headers: str) -> MCPClient:
    """Streamable HTTP MCPクライアントを作成する関数"""
    streamable_http_mcp_client = MCPClient(
        lambda: streamablehttp_client(url, headers=headers),
    )
    return streamable_http_mcp_client

def get_tools_list(client: MCPClient):
    """AgentCore Gatewayのツール一覧を取得する"""
    more_tools = True
    tools = []
    pagination_token = None
    # ページネーションを使用してすべてのツールを取得
    while more_tools:
        tmp_tools = client.list_tools_sync(pagination_token=pagination_token)
        tools.extend(tmp_tools)
        if tmp_tools.pagination_token is None:
            more_tools = False
        else:
            more_tools = True
            pagination_token = tmp_tools.pagination_token
    return tools

PROMPT="""こんにちは。以下のjsonをcsvに変換して結果だけ出力してください
[{"a": "1", "b": "2", "c": "3"}]"""
PROMPT="""以下のJSONをYAMLに変換して結果だけ出力してください
[{"a": {"aa": "1", "ab": "5"}, "b": "2", "c": "3"}]"""
def invoke_agent():
    """メイン処理：エージェントを起動してデータ変換を実行"""
    # アクセストークンを取得
    access_token = get_token(CLIENT_ID, CLIENT_SECRET, USER_POOL_ID)


    # MCPクライアントを作成し、ゲートウェイに接続
    mcp_client = create_streamable_http_mcp_client(
        GATEWAY_ENDPOINT,
        {"Authorization": f"Bearer {access_token}"}
    )
    with mcp_client:
        # 利用可能なツール一覧を取得
        mcp_tools = get_tools_list(mcp_client)
        # Bedrockのモデルを定義
        model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0")
        # エージェントを初期化
        agent = Agent(
            model=model,
            tools=[mcp_tools]
        )
        response = agent(PROMPT)

if __name__ == "__main__":
    invoke_agent()
