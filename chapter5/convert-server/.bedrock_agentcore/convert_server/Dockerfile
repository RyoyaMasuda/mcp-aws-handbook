FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

# All environment variables in one layer
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=us-west-2 \
    AWS_DEFAULT_REGION=us-west-2

## ここから追記内容 ##
# Install Node.js and npm
RUN apt-get update && apt-get install -y \
curl \
&& curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
&& apt-get install -y nodejs chromium chromium-driver fonts-noto-cjk libreoffice-impress\
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*
RUN npm install -g @marp-team/marp-cli
## ここまで ##


COPY requirements.txt requirements.txt
# Install from requirements file
RUN uv pip install -r requirements.txt




RUN uv pip install aws-opentelemetry-distro==0.12.2


# Signal that this is running in Docker for host binding logic
ENV DOCKER_CONTAINER=1

# Create non-root user
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

EXPOSE 9000
EXPOSE 8000
EXPOSE 8080

# Copy entire project (respecting .dockerignore)
COPY . .

# Use the full module path

CMD ["opentelemetry-instrument", "python", "-m", "convert_server"]
