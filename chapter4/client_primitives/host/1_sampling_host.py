import asyncio

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.shared.context import RequestContext
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from strands.agent import Agent
from strands.models import BedrockModel


def with_mcp_client(func) -> ClientSession:
    async def wrapper(*args, **kwargs):
        server_params = StdioServerParameters(
            command="uv",
            args=[
                "run",
                "--directory",
                "../server",
                "1_sampling_server.py",
            ],
            env={},
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(
                read,
                write,
                sampling_callback=handle_sampling_callback,
                # Samplingリクエストを処理する関数を指定
            ) as session:
                await session.initialize()

                return await func(session, *args, **kwargs)

    return wrapper


async def handle_sampling_callback(
    context: RequestContext,
    request_params: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    content = f"[cyan]System Prompt:[/cyan] {request_params.systemPrompt}\n"
    content += f"[cyan]Temperature:[/cyan] {request_params.temperature}\n"
    content += f"[cyan]Max Tokens:[/cyan] {request_params.maxTokens}\n"
    content += f"[cyan]Message:[/cyan] {request_params.messages[0].content.text}"

    print(Panel(content, title="Sampling parameters"))

    send_contents = [{"text": msg.content.text} for msg in request_params.messages]
    # list[ContentBlock]型に変換 [{"text: "LLMに送信する内容"}...] の形式

    model_id = "us.amazon.nova-lite-v1:0"

    model = BedrockModel(
        model_id=model_id,
        region_name="us-west-2",
        max_tokens=request_params.maxTokens,
        temperature=request_params.temperature,
    )

    agent = Agent(
        model=model,
        system_prompt=request_params.systemPrompt,
        callback_handler=None,
    )

    response = agent(send_contents)

    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text=response.message["content"][0]["text"],
        ),
        model=model_id,
        stopReason=response.stop_reason,
    )


@with_mcp_client
async def main(session: ClientSession):
    tool_name = "translate"

    tools = await session.list_tools()

    translate_tool = next(
        (t for t in tools.tools if t.name == tool_name),
        None,
    )

    content = f"[bold blue]{translate_tool.name}[/bold blue]\n"
    content += f"[dim]{translate_tool.description}[/dim]"

    print(Panel(content, title="Tool info"))

    params = {}
    for param_name, param_info in translate_tool.inputSchema["properties"].items():
        value = Prompt.ask(f"[yellow]{param_name}[/yellow]")
        params[param_name] = value

    result = await session.call_tool(translate_tool.name, params)
    print(Panel(result.content[0].text, title="Tool Result"))


if __name__ == "__main__":
    asyncio.run(main())
