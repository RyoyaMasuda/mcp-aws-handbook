from pathlib import Path

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import SamplingMessage, TextContent

mcp = FastMCP(name="Client features sample")


@mcp.tool()
async def translate(language: str, content: str, ctx: Context) -> dict:
    """翻訳します
    Args:
        language: 翻訳先の言語（日本語、英語など）
        content: 翻訳する内容
    """
    sampling_result = await ctx.session.create_message(
        system_prompt="あなたは優秀な翻訳家です。翻訳結果だけを回答してください。",
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"次の文章を{language}に翻訳してください。\n{content}",
                ),
            ),
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    list_roots = await ctx.session.list_roots()
    roots = list_roots.roots[0]

    filename = "output.txt"
    output_file = Path(roots.uri.path) / filename

    if output_file and not output_file.exists():
        with open(output_file, mode="wt", encoding="utf-8") as f:
            f.write(sampling_result.content.text)

        return {
            "message": f"翻訳結果を{output_file.name}に出力しました。",
            "content": sampling_result.content.text,
        }
    else:
        return {
            "message": "ファイルへの出力を中止しました。",
            "content": sampling_result.content.text,
        }


if __name__ == "__main__":
    mcp.run()
