import sys

import typer
from gradio_client import Client
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Header, Input, Static

app = typer.Typer(rich_markup_mode="markdown")
console = Console()


class HunyuanChatApp(App):
    """Textual-based interactive chat application."""

    CSS_PATH = "styles.css"
    BINDINGS = [("ctrl+q", "quit", "Quit")]

    def __init__(self, client: Client):
        super().__init__()
        self.client = client
        self.chat_history = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            Static(id="chat-history", classes="chat-history"),
            Input(placeholder="Type your message...", id="message-input"),
            classes="chat-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Event when app is mounted."""
        self.title = "Hunyuan T1 Chat"
        self.sub_title = "Interactive Chat Interface"

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle message submission."""
        if not message.value.strip():
            return

        # Add user message to history
        self.add_message_to_history(f"You: {message.value}", "user-message")

        # Show processing indicator
        processing = self.query_one("#chat-history")
        processing.update(f"{processing.renderable}\n\n[italic]Thinking...[/]")

        # Get and display response
        try:
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
            ) as progress:
                progress.add_task("Processing...", total=None)
                response = self.client.predict(message=message.value, api_name="/chat")

            self.add_message_to_history(f"AI: {response}", "ai-message")
        except Exception as e:
            self.add_message_to_history(f"Error: {str(e)}", "error-message")

        # Clear input
        message.input.value = ""

    def add_message_to_history(self, message: str, css_class: str) -> None:
        """Add a message to the chat history."""
        history = self.query_one("#chat-history")
        new_content = Markdown(message)
        if history.renderable:
            history.update(f"{history.renderable}\n\n{new_content}")
        else:
            history.update(new_content)
        history.add_class(css_class)


def query_hunyuan(message: str, client: Client) -> str:
    """Query the Hunyuan T1 model and return the response."""
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        progress.add_task("Processing query...", total=None)
        return client.predict(message=message, api_name="/chat")


@app.command()
def chat(
        url: str = typer.Option(
            "tencent/Hunyuan-T1",
            help="URL or model name for Hunyuan T1",
            rich_help_panel="Connection Settings",
        ),
        gui: bool = typer.Option(
            False,
            "--gui",
            help="Launch interactive GUI interface (requires textual)",
            rich_help_panel="Interface Options",
        ),
):
    """Start interactive chat session."""
    try:
        client = Client(url)
        console.print(
            Panel.fit(
                f"[green]Connected to Hunyuan T1 at [bold]{url}[/bold][/green]",
                title="Connection Status",
            )
        )

        if gui:
            try:
                chat_app = HunyuanChatApp(client)
                chat_app.run()
            except ImportError:
                console.print(
                    "[red]GUI mode requires 'textual'. Install with: pip install textual[/red]"
                )
                sys.exit(1)
        else:
            console.print(
                Panel.fit(
                    "[bold]Interactive Chat Mode[/]\nType your messages. Enter 'exit' to quit.",
                    style="blue",
                )
            )
            while True:
                message = typer.prompt("You")
                if message.lower() in ("exit", "quit"):
                    break
                try:
                    response = query_hunyuan(message, client)
                    console.print(
                        Panel.fit(
                            Markdown(response),
                            title="Hunyuan T1",
                            border_style="green",
                        )
                    )
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")

    except Exception as e:
        console.print(f"[red]Connection error: {str(e)}[/red]")
        sys.exit(1)


@app.command()
def ask(
        message: str = typer.Argument(..., help="Message to send to Hunyuan T1"),
        url: str = typer.Option(
            "tencent/Hunyuan-T1",
            help="URL or model name for Hunyuan T1",
            rich_help_panel="Connection Settings",
        ),
        markdown: bool = typer.Option(
            True, help="Format output as Markdown", rich_help_panel="Display Options"
        ),
):
    """Send a single message to Hunyuan T1."""
    try:
        client = Client(url)
        response = query_hunyuan(message, client)

        if markdown:
            console.print(
                Panel.fit(
                    Markdown(response),
                    title="Hunyuan T1 Response",
                    border_style="green",
                )
            )
        else:
            console.print(Panel.fit(response, title="Hunyuan T1 Response"))

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


def version_callback(value: bool):
    """Show version information."""
    if value:
        console.print("[bold]Hunyuan CLI[/bold] version 1.0.0")
        raise typer.Exit()


@app.callback()
def main(
):
    """Command line interface for Tencent's Hunyuan T1 model."""
    pass


if __name__ == "__main__":
    app()
