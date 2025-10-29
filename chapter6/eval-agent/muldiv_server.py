from mcp.server.fastmcp import FastMCP


# FastMCP サーバーを初期化
mcp = FastMCP("MulDivServer")


@mcp.tool()
def mul(a: int, b: int) -> int:
    """
    2つの整数を掛け算して結果を返す    
    Args:
        a: 第1の整数
        b: 第2の整数
    """
    return a * b


@mcp.tool()
def div(a: int, b: int) -> float:
    """
    第1の整数を第2の整数で割り算して結果を返す
    Args:
        a: 第1の整数
        b: 第2の整数
    """
    if b == 0:
        raise ZeroDivisionError("0で割ることはできません")
    return a / b


def main():
    """サーバーを実行"""
    mcp.run()


if __name__ == "__main__":
    main()
