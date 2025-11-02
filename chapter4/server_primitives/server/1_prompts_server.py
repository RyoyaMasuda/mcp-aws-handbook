from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="MCP Server Example")


@mcp.prompt(title="Translation")
def translation(lang: str) -> str:
    print("translation")
    return f"以下の文章を{lang}に訳してください。"


if __name__ == "__main__":
    mcp.run()
