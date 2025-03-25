"""
Hunyuan Portal CLI: Interact with Tencent's Hunyuan model via Gradio.

This script provides a command-line interface (CLI) to interact with
Hunyuan models hosted on Hugging Face Gradio Spaces. It offers two main modes:
1. `chat`: An interactive chat session.
2. `ask`: Send a single query and receive a response.
"""

from pathlib import Path
from typing import Optional

# Third-party dependencies
import typer
from gradio_client import Client as GradioClient
# Removed the incorrect import: from gradio_client.utils import ConnectError
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule

# --- Constants ---
APP_NAME = "Hunyuan Portal (CLI)"
APP_VERSION = "3.1.1"  # Incremented version for the fix
DEFAULT_GRADIO_URL = "tencent/Hunyuan-T1"

# --- Application Setup ---
app = typer.Typer(
    rich_markup_mode="markdown",
    help=f"{APP_NAME} - Interact with Hunyuan models on Gradio.",
    add_completion=False,
)
console = Console()


# --- Core Functions ---

def query_hunyuan(message: str, client: GradioClient, show_progress: bool = True) -> str:
    """
    Query the Hunyuan model via the Gradio client.

    Args:
        message: The input message/prompt for the model.
        client: An initialized GradioClient instance.
        show_progress: Whether to display a progress spinner during the API call.

    Returns:
        The model's response as a string.

    Raises:
        ConnectionError: If the API call fails due to network/connection issues.
        RuntimeError: For other unexpected errors during prediction.
    """
    task_description = "Querying Hunyuan..."
    api_name = "/chat"

    try:
        if show_progress:
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                    console=console,
            ) as progress:
                progress.add_task(task_description, total=None)
                response = client.predict(message=message, api_name=api_name)
        else:
            response = client.predict(message=message, api_name=api_name)

        return str(response) if response is not None else ""

    # Use the standard Python ConnectionError
    except ConnectionError as e:
        raise ConnectionError(f"Gradio API call failed: {e}") from e
    except Exception as e:
        # Catch broader exceptions during prediction
        console.print_exception(show_locals=False)
        raise RuntimeError(f"An unexpected error occurred during prediction: {e}") from e


def _connect_client(url: str) -> GradioClient:
    """Helper function to connect to the Gradio client with feedback."""
    console.print(f"Attempting to connect to Gradio Space: [cyan]{url}[/cyan]...")
    try:
        # Connection errors during initialization might raise various things,
        # including ValueError for bad URLs or potentially ConnectionError
        # if it tries an initial check. Catching broadly is safer here.
        client = GradioClient(url)
        console.print(
            f"[green]Successfully connected to [bold]{url}[/bold][/green]"
        )
        return client
    except Exception as e:
        # Catch potential errors during Client initialization (e.g., invalid URL format, initial connection fail)
        console.print(f"[bold red]Fatal Connection Error:[/bold red] Could not initialize client for {url}.")
        console.print(f"[red]Details: {e}[/red]")
        console.print("[yellow]Please check the URL/ID and ensure the Gradio Space is running and accessible.[/yellow]")
        raise typer.Exit(code=1)


# --- Typer Commands ---

@app.command()
def chat(
        url: str = typer.Option(
            DEFAULT_GRADIO_URL,
            "--url",
            "-u",
            help="URL or Hugging Face repo ID for the Gradio Space.",
            rich_help_panel="Connection Settings",
        ),
):
    """Start an interactive CLI chat session with the Hunyuan model."""
    client = _connect_client(url)

    console.print("\n[bold blue]Interactive Chat Mode[/]")
    console.print("Type your message and press Enter. Use 'exit' or 'quit' to end.")
    console.print(Rule(style="blue"))

    while True:
        try:
            message = typer.prompt("You")
        except EOFError:
            console.print("\n[yellow]Exiting chat session.[/yellow]")
            break

        if message.strip().lower() in ("exit", "quit"):
            console.print("[yellow]Exiting chat session.[/yellow]")
            break
        if not message.strip():
            continue

        try:
            response = query_hunyuan(message, client, show_progress=True)

            console.print(f"\n[green]Hunyuan:[/green]")
            console.print(Markdown(response))
            console.print(Rule(style="green"))

        # Catch standard ConnectionError for issues during the API call
        except ConnectionError as e:
            console.print(f"[red]API Call Error:[/red] {str(e)}")
            console.print("[yellow]Please check connection or endpoint status. Try again.[/yellow]")
            console.print(Rule(style="red"))
        except RuntimeError as e:  # Catch the re-raised prediction error
            console.print(f"[red]Prediction Error:[/red] {str(e)}")
            console.print(Rule(style="red"))
        except Exception as e:  # Catch any other unexpected errors in the loop
            console.print(f"[bold red]An unexpected error occurred:[/bold red] {str(e)}")
            console.print_exception(show_locals=False)
            console.print(Rule(style="red"))


@app.command()
def ask(
        message: str = typer.Argument(..., help="The message/prompt to send to the model."),
        url: str = typer.Option(
            DEFAULT_GRADIO_URL,
            "--url",
            "-u",
            help="URL or Hugging Face repo ID for the Gradio Space.",
            rich_help_panel="Connection Settings",
        ),
        markdown: bool = typer.Option(
            True,
            "--markdown/--no-markdown",
            help="Output response as Markdown (default) or raw text.",
            rich_help_panel="Display Options",
        ),
        output: Optional[Path] = typer.Option(
            None,
            "--output",
            "-o",
            help="Save response to a file instead of printing to console.",
            rich_help_panel="Output Options",
            writable=True,
            resolve_path=True,
            dir_okay=False,
        ),
):
    """Send a single message to Hunyuan and get the response."""
    client = _connect_client(url)
    console.print(" ")

    try:
        response = query_hunyuan(message, client, show_progress=True)

        if output:
            try:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(response, encoding="utf-8")
                console.print(f"[green]Response successfully saved to: [cyan]{output.resolve()}[/cyan][/green]")
            except IOError as e:
                console.print(f"[red]Error writing to file {output}: {e}[/red]")
                raise typer.Exit(code=1)
        elif markdown:
            console.print(f"[green]Hunyuan Response:[/green]")
            console.print(Markdown(response))
        else:
            console.print(f"[dim]Hunyuan Response (Raw):[/dim]")
            console.print(response)

    # Catch standard ConnectionError for issues during the API call
    except ConnectionError as e:
        console.print(f"[red]API Call Error:[/red] {str(e)}")
        raise typer.Exit(code=1)
    except RuntimeError as e:  # Catch the re-raised prediction error
        console.print(f"[red]Prediction Error:[/red] {str(e)}")
        raise typer.Exit(code=1)
    except Exception as e:  # Catch any other unexpected errors
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {str(e)}")
        console.print_exception(show_locals=False)
        raise typer.Exit(code=1)


def version_callback(value: bool):
    """Display the application version and exit."""
    if value:
        console.print(f"[bold]{APP_NAME}[/bold] version {APP_VERSION}")
        raise typer.Exit()


@app.callback()
def main(
):
    """
    {APP_NAME}

    A command-line tool to interact with Tencent's Hunyuan model
    hosted on Gradio Spaces. Provides both interactive chat and
    single-query modes.
    """
    pass


# --- Main Execution Guard ---
if __name__ == "__main__":
    app()
