from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="MCP Server Example")


@mcp.prompt(title="Translation")
def translation(lang: str) -> str:
    print("translation")
    return f"以下の文章を{lang}に訳してください。"


@mcp.resource("file://bedrock.txt", name="Bedrock")
def get_bedrock() -> str:
    with open(
        "resources/bedrock.txt",
        mode="rt",
        encoding="utf-8",
    ) as f:
        text = f.read()
    return text


@mcp.resource("file://s3.txt", name="S3")
def get_s3() -> str:
    with open(
        "resources/s3.txt",
        mode="rt",
        encoding="utf-8",
    ) as f:
        text = f.read()
    return text


@mcp.resource("file://ec2.txt", name="EC2")
def get_ec2() -> str:
    with open(
        "resources/ec2.txt",
        mode="rt",
        encoding="utf-8",
    ) as f:
        text = f.read()
    return text


if __name__ == "__main__":
    mcp.run()
