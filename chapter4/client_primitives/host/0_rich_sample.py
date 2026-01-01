from rich import print
from rich.panel import Panel
from rich.prompt import Prompt

print("こんにちは")  # Richライブラリのprint関数が呼び出される

print("[cyan]青色のテキスト[/cyan]")
print("[yellow]黄色のテキスト[/yellow]")
print("[dim]薄い色のテキスト[/dim]")

print("[bold]太字[/bold]")
print("[underline]下線[/underline]")
print("[bold blue]太字の青色[/bold blue]")

print(Panel("こんにちは", title="タイトル"))

print(Panel("[cyan]装飾も可能[/cyan]", title="[yellow]タイトル[/yellow]"))

value = Prompt.ask("[yellow]text[/yellow]")

print(f"入力した値は[bold blue]{value}[/bold blue]です。")
