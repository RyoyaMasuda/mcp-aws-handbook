### 5-2
cd /workspaces/mcp-aws-handbook
mkdir -p chapter5
cd chapter5
uv init rag-agent --python 3.13

cd rag-agent
uv add mcp==1.21.0 strands-agents==1.15.0 nest-asyncio==1.6.0 streamlit==1.51.0

uv run streamlit run app.py

uv run streamlit run app_with_kb.py


mkdir -p .claude
touch settings.json

claude mcp add --scope user --transport stdio "playwright" -- npx "@playwright/mcp@latest"
npm install chrome

claude mcp list
app_with_kb.pyをGUIベースでテストしてください。テスト時の入力は「AWS Bedrock API Keyについて教えて」です。出力結果のテキストを保存してください。python実行はuvを用いてください。

# 削除
aws s3vectors delete-index --vector-bucket-name "<ベクトルバケット名>" --index-name "<ベクトルインデックス名>"
aws s3vectors delete-vector-bucket --vector-bucket-name "<ベクトルバケット名>"

aws s3vectors delete-index --vector-bucket-name "bedrock-knowledge-base-nf6rrm" --index-name "bedrock-knowledge-base-default-index"
aws s3vectors delete-vector-bucket --vector-bucket-name "bedrock-knowledge-base-nf6rrm"


### 5-3
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

uv init research-agent --python 3.13

cd research-agent
uv add  mcp==1.21.0 strands-agents==1.15.0 nest-asyncio==1.6.0
uv run research_agent.py

uv add boto3==1.40.69
uv run create_lambda_role.py

cd /workspaces/mcp-aws-handbook/chapter5
uv init convert-server --python 3.13

cd convert-server
uv add bedrock-agentcore-starter-toolkit==0.1.32

cd /workspaces/mcp-aws-handbook/chapter5
uv init convert-server-client --python 3.13

cd /workspaces/mcp-aws-handbook/chapter5/convert-server
uv run agentcore configure -e convert_server.py --protocol MCP --disable-memory

uv run agentcore launch

cd convert-server-client
uv add mcp==1.21.0 strands-agents==1.15.0 requests==2.32.5

#削除
cd /workspaces/mcp-aws-handbook/chapter5/convert-server
uv run agentcore destroy

####IAM版###
cd /workspaces/mcp-aws-handbook/chapter5/convert-server-client
uv add mcp==1.21.0 strands-agents==1.15.0 mcp-proxy-for-aws==1.1.0

uv run agent.py

#### 6-1
cd /workspaces/mcp-aws-handbook
mkdir -p chapter6
cd chapter6
uv init llm-as-a-judge --python 3.13
cd llm-as-a-judge
uv add deepeval==3.7.0  aiobotocore==2.25.1
uv run eval.py

cd /workspaces/mcp-aws-handbook
mkdir -p chapter6
cd chapter6
uv init eval-agent --python 3.13
cd eval-agent
uv add mcp==1.21.0 strands-agents==1.15.0 deepeval==3.7.0 aiobotocore==2.25.1
uv run calc_agent.py

#### 6-2
cd /workspaces/mcp-aws-handbook
mkdir -p chapter6
cd chapter6
uv init target-mcp-server --python 3.13

cd /workspaces/mcp-aws-handbook/chapter6/target-mcp-server
uv add bedrock-agentcore-starter-toolkit

uv run agentcore configure -e json_yaml.py --protocol MCP --disable-memory
uv run agentcore launch

cd /workspaces/mcp-aws-handbook/chapter6
uv init gateway-client --python 3.13

cd gateway-client/
uv add strands-agents==1.15.0 mcp-proxy-for-aws==1.1.0

uv run agent.py

#削除
cd /workspaces/mcp-aws-handbook/chapter6/target-mcp-server/
uv run agentcore destroy

curl -LsSf https://astral.sh/uv/install.sh | sh

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

aws --version