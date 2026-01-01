FROM public.ecr.aws/lambda/python:3.13


# システムパッケージの更新とNode.js最新安定版のインストール
RUN dnf update -y \
    && curl -fsSL https://rpm.nodesource.com/setup_lts.x | bash - \
    && dnf install -y nodejs


# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


ENV NPM_CONFIG_CACHE=/tmp/.npm
ENV NPM_CONFIG_PREFIX=/tmp/.npm-global
ENV HOME=/tmp


# アプリケーションファイルをコピー
COPY research_agent_lambda.py ${LAMBDA_TASK_ROOT}


# デフォルトコマンド
CMD ["research_agent_lambda.lambda_handler"]