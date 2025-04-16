import importlib.metadata
from pathlib import Path
from typing import Optional

import typer
from gradio_client import Client as GradioClient
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule

from hunyuan_app.core.client import (
    connect_client,
    query_hunyuan_model,
    DEFAULT_GRADIO_URL,
    GRADIO_API_ENDPOINT,
    ConnectionSetupError,
    PredictionError,
)

APP_NAME = "Hunyuan Portal (CLI)"
try:
    APP_VERSION = importlib.metadata.version("hunyuan_app")
except importlib.metadata.PackageNotFoundError:
    APP_VERSION = "0.0.0-dev"

console = Console()
app = typer.Typer(
    rich_markup_mode="markdown",
    help=f"{APP_NAME} - Interact with Hunyuan models on Gradio.",
    no_args_is_help=True,
)


def _exit_with_error(
        message: str, code: int = 1, show_traceback: bool = False, exception: Optional[Exception] = None
):
    console.print(f"\n[bold red]{message}[/bold red]")
    if exception and show_traceback:
        console.print_exception(show_locals=False)
    raise typer.Exit(code=code)


def _initialize_client(url: str) -> GradioClient:
    try:
        console.print(f"Connecting to Gradio Space: [cyan]{url}[/cyan]...")
        client = connect_client(url)
        # Optional show model/server information here
        console.print(f"[green]Connected to [bold]{url}[/bold][/green]")
        return client
    except ConnectionSetupError as e:
        _exit_with_error(
            f"Connection error: {e}\n[yellow]Check the URL and ensure the Space is accessible.[/yellow]",
            code=1,
        )
    except Exception as e:
        _exit_with_error("Unexpected error during connection.", code=1, show_traceback=True, exception=e)


def _query_with_progress(prompt: str, client: GradioClient, api_endpoint: str) -> str:
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
    ) as progress:
        progress.add_task("Querying Hunyuan...", total=None)
        response = query_hunyuan_model(
            message=prompt,
            client=client,
            api_endpoint=api_endpoint
        )
    return str(response) if response is not None else ""


@app.command()
def chat(
        url: str = typer.Option(
            DEFAULT_GRADIO_URL, "--url", "-u",
            help="URL or Hugging Face repo ID for the Gradio Space.",
            rich_help_panel="Connection Settings",
        ),
        api_endpoint: str = typer.Option(
            GRADIO_API_ENDPOINT, "--api",
            help="Specific API endpoint name in the Gradio Space (usually '/chat').",
            rich_help_panel="Connection Settings",
            hidden=True,
        ),
        history_file: Optional[Path] = typer.Option(
            None, "--history", "-h",
            help="Optional: save chat history to a file.",
            writable=True,
            resolve_path=True,
            dir_okay=False,
            rich_help_panel="Output Options",
        ),
):
    """
    Start an interactive CLI chat session with the Hunyuan model.

    Type messages and press Enter. Use 'exit' or 'quit' to end.
    """
    client = _initialize_client(url)
    chat_history = []

    console.print("\n[bold blue]Interactive Chat Mode[/]")
    console.print("Type your message and press Enter. Use 'exit' or 'quit' to end.")
    console.print(Rule(style="blue"))

    while True:
        try:
            message = console.input("[bold]You:[/bold] ")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Exiting chat session.[/yellow]")
            break

        cleaned = message.strip()
        if cleaned.lower() in {"exit", "quit"}:
            console.print("[yellow]Exiting chat session.[/yellow]")
            break
        if not cleaned:
            continue

        try:
            response = _query_with_progress(cleaned, client, api_endpoint)
            chat_history.append({"user": cleaned, "hunyuan": response})
            console.print(f"\n[green]Hunyuan:[/green]")
            console.print(Markdown(response))
            console.print(Rule(style="green"))
        except (ConnectionError, PredictionError) as e:
            console.print(f"\n[bold red]Query Error:[/bold red] {e}")
            console.print("[yellow]Try again or check your connection/endpoint.[/yellow]")
            console.print(Rule(style="red"))
        except Exception as e:
            _exit_with_error("Unexpected error in chat loop.", show_traceback=True, exception=e)

    if history_file and chat_history:
        import json
        history_file.write_text(json.dumps(chat_history, indent=2, ensure_ascii=False), encoding="utf-8")
        console.print(f"[green]Chat history saved to: [cyan]{history_file}[/cyan][/green]")


@app.command()
def ask(
        message: str = typer.Argument(..., help="The message/prompt to send to the model."),
        url: str = typer.Option(
            DEFAULT_GRADIO_URL, "--url", "-u",
            help="URL or Hugging Face repo ID for the Gradio Space.",
            rich_help_panel="Connection Settings",
        ),
        api_endpoint: str = typer.Option(
            GRADIO_API_ENDPOINT, "--api",
            help="Specific API endpoint name in the Gradio Space (usually '/chat').",
            rich_help_panel="Connection Settings",
            hidden=True,
        ),
        markdown_output: bool = typer.Option(
            True, "--markdown/--no-markdown",
            help="Output response as Markdown (default) or raw text.",
            rich_help_panel="Display Options",
        ),
        output_file: Optional[Path] = typer.Option(
            None, "--output", "-o",
            help="Save response to a file instead of printing to console.",
            rich_help_panel="Output Options",
            writable=True,
            resolve_path=True,
            dir_okay=False,
        ),
):
    """
    Send a single message (prompt) to the Hunyuan model and display or save the response.
    """
    client = _initialize_client(url)
    console.print()

    try:
        response = _query_with_progress(message, client, api_endpoint)
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(response, encoding="utf-8")
            console.print(f"[green]Response saved to: [cyan]{output_file}[/cyan][/green]")
        elif markdown_output:
            console.print(f"[green]Hunyuan Response:[/green]")
            console.print(Markdown(response))
        else:
            console.print(f"[dim]Hunyuan Response (Raw):[/dim]\n{response}")

    except (ConnectionError, PredictionError) as e:
        _exit_with_error(f"Error during query: {e}", code=1)
    except Exception as e:
        _exit_with_error("Unexpected error during 'ask' command.", show_traceback=True, exception=e)


def version_callback(value: bool):
    if value:
        console.print(f"[bold]{APP_NAME}[/bold] version {APP_VERSION}")
        raise typer.Exit(code=0)


@app.callback()
def main():
    """
    Hunyuan Portal (CLI)

    A command-line tool to interact with Tencent's Hunyuan model
    hosted on Gradio Spaces using the gradio_client library.

    Use '--help' after a command (e.g., `chat --help`) for command-specific options.
    """
    pass


app.command()(main)  # Optional, for clarity if using as a module
