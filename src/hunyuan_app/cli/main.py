from pathlib import Path
from typing import Optional

import typer
from gradio_client import Client as GradioClient
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule

# Import core logic and constants from the shared core module
from hunyuan_app.core.client import (
    connect_client,  # Core function to establish Gradio connection
    query_hunyuan_model,  # Core function to query the model
    DEFAULT_GRADIO_URL,  # Default connection URL
    GRADIO_API_ENDPOINT,  # Default API endpoint name
    ConnectionSetupError,  # Custom exception for connection setup issues
    PredictionError  # Custom exception for prediction errors
)

# --- CLI Constants ---
APP_NAME: str = "Hunyuan Portal (CLI)"
# Consider fetching version dynamically from pyproject.toml using importlib.metadata
# Example: try: APP_VERSION = importlib.metadata.version("hunyuan_app") except importlib.metadata.PackageNotFoundError: APP_VERSION = "0.0.0-dev"
APP_VERSION: str = "3.1.1"

# --- CLI Application Setup ---
console = Console()
app = typer.Typer(
    rich_markup_mode="markdown",
    help=f"{APP_NAME} - Interact with Hunyuan models on Gradio.",
    add_completion=False,  # Keep CLI setup simple
    no_args_is_help=True,  # Show help if no command/arguments are provided
)


# --- CLI Helper Functions ---

def _initialize_client(url: str) -> GradioClient:
    """
    Connects to the Gradio client, handling errors and printing status messages.

    Exits the application via typer.Exit if connection fails.

    Args:
        url: The URL or Hugging Face repo ID of the Gradio Space.

    Returns:
        An initialized GradioClient instance.

    Raises:
        typer.Exit: If connection setup fails.
    """
    try:
        console.print(f"Attempting to connect to Gradio Space: [cyan]{url}[/cyan]...")
        client = connect_client(url)  # Use core connection function
        console.print(f"[green]Successfully connected to [bold]{url}[/bold][/green]")
        return client
    except ConnectionSetupError as e:
        console.print(f"\n[bold red]Fatal Connection Error:[/bold red] {e}")
        console.print(
            "\n[yellow]Possible reasons:[/yellow]\n"
            "- Incorrect URL or Hugging Face repo ID.\n"
            "- Gradio Space is not running or is private.\n"
            "- Network connectivity issues."
        )
        console.print("[yellow]Please check the URL/ID and ensure the Space is accessible.[/yellow]")
        # Exit gracefully with an error code using Typer's mechanism
        raise typer.Exit(code=1)
    except Exception as e:  # Catch any other unexpected connection errors
        console.print(f"\n[bold red]Unexpected Error during connection:[/bold red] {e}")
        # Show traceback for unexpected errors to aid debugging
        console.print_exception(show_locals=False)
        raise typer.Exit(code=1)


def _query_with_progress(message: str, client: GradioClient, api_endpoint: str) -> str:
    """
    Wraps the core model query function with a Rich progress spinner.

    Args:
        message: The input message/prompt for the model.
        client: An initialized GradioClient instance.
        api_endpoint: The specific API endpoint name on the Gradio server.

    Returns:
        The model's response as a string.

    Raises:
        ConnectionError: If the API call fails due to network issues (propagated).
        PredictionError: For other prediction errors (propagated).
    """
    task_description: str = "Querying Hunyuan..."

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,  # Hide progress bar on completion
            console=console,
    ) as progress:
        progress.add_task(task_description, total=None)  # Indeterminate task
        # Call the core function that performs the actual API request
        response = query_hunyuan_model(
            message=message,
            client=client,
            api_endpoint=api_endpoint
        )
    # Ensure a string is returned even if the API gives None
    return str(response) if response is not None else ""


# --- Typer Command Definitions ---

@app.command()
def chat(
        url: str = typer.Option(
            DEFAULT_GRADIO_URL,  # Default from core module
            "--url", "-u",
            help="URL or Hugging Face repo ID for the Gradio Space.",
            rich_help_panel="Connection Settings",
        ),
        api_endpoint: str = typer.Option(
            GRADIO_API_ENDPOINT,  # Default from core module
            "--api",
            help="Specific API endpoint name in the Gradio Space (usually '/chat').",
            rich_help_panel="Connection Settings",
            hidden=True,  # Hide by default unless needed by advanced users
        ),
) -> None:
    """
    Start an interactive CLI chat session with the Hunyuan model.

    Type messages and press Enter. Use 'exit' or 'quit' to end.
    """
    # Initialize client using the helper function (handles errors/exit)
    client = _initialize_client(url)

    # Display chat instructions
    console.print("\n[bold blue]Interactive Chat Mode[/]")
    console.print("Type your message and press Enter. Use 'exit' or 'quit' to end.")
    console.print(Rule(style="blue"))

    # Main interaction loop
    while True:
        try:
            # Prompt user for input
            message = console.input("[bold]You:[/bold] ")
        except (EOFError, KeyboardInterrupt):
            # Handle Ctrl+D or Ctrl+C gracefully
            console.print("\n[yellow]Exiting chat session.[/yellow]")
            break

        # Process input
        cleaned_message = message.strip()
        if cleaned_message.lower() in ("exit", "quit"):
            console.print("[yellow]Exiting chat session.[/yellow]")
            break
        if not cleaned_message:
            # Ignore empty input, prompt again
            continue

        # Query the model and display response
        try:
            # Use the helper to show progress while calling core logic
            response = _query_with_progress(cleaned_message, client, api_endpoint)

            # Display the model's response using Markdown
            console.print(f"\n[green]Hunyuan:[/green]")
            console.print(Markdown(response))
            console.print(Rule(style="green"))  # Visual separator

        except (ConnectionError, PredictionError) as e:  # Catch specific errors from core
            console.print(f"\n[bold red]Error during query:[/bold red] {str(e)}")
            console.print("[yellow]You can try again, or check connection/endpoint status.[/yellow]")
            console.print(Rule(style="red"))
        except Exception as e:  # Catch other unexpected errors within the loop
            console.print(f"\n[bold red]An unexpected error occurred in the chat loop:[/bold red] {str(e)}")
            console.print_exception(show_locals=False)
            console.print(Rule(style="red"))
            # Consider whether breaking is safer here, depending on error type
            # break


@app.command()
def ask(
        message: str = typer.Argument(..., help="The message/prompt to send to the model."),
        url: str = typer.Option(
            DEFAULT_GRADIO_URL,  # Default from core module
            "--url", "-u",
            help="URL or Hugging Face repo ID for the Gradio Space.",
            rich_help_panel="Connection Settings",
        ),
        api_endpoint: str = typer.Option(
            GRADIO_API_ENDPOINT,  # Default from core module
            "--api",
            help="Specific API endpoint name in the Gradio Space (usually '/chat').",
            rich_help_panel="Connection Settings",
            hidden=True,  # Hide by default
        ),
        markdown_output: bool = typer.Option(
            True,
            "--markdown/--no-markdown",  # Creates --markdown and --no-markdown flags
            help="Output response as Markdown (default) or raw text.",
            rich_help_panel="Display Options",
        ),
        output_file: Optional[Path] = typer.Option(
            None,
            "--output", "-o",
            help="Save response to a file instead of printing to console.",
            rich_help_panel="Output Options",
            writable=True,  # Typer checks if the file path is writable
            resolve_path=True,  # Converts to an absolute path
            dir_okay=False,  # Ensures it is a file path, not a directory
        ),
) -> None:
    """
    Send a single message (prompt) to the Hunyuan model and display or save the response.
    """
    # Initialize client using the helper function (handles errors/exit)
    client = _initialize_client(url)
    console.print(" ")  # Add a blank line for visual spacing after connection messages

    # Query the model
    try:
        # Use the helper to show progress while calling core logic
        response = _query_with_progress(message, client, api_endpoint)

        # Handle output (file or console)
        if output_file:
            try:
                # Ensure parent directory exists before writing
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(response, encoding="utf-8")
                console.print(f"[green]Response successfully saved to: [cyan]{output_file}[/cyan][/green]")
            except IOError as e:
                # Handle potential file writing errors
                console.print(f"[bold red]Error writing to file {output_file}:[/bold red] {e}")
                raise typer.Exit(code=1)  # Exit with error code
        elif markdown_output:
            # Print response formatted as Markdown (default)
            console.print(f"[green]Hunyuan Response:[/green]")
            console.print(Markdown(response))
        else:
            # Print response as raw text (--no-markdown flag used)
            console.print(f"[dim]Hunyuan Response (Raw):[/dim]")
            console.print(response)

    except (ConnectionError, PredictionError) as e:  # Catch specific errors from core
        console.print(f"\n[bold red]Error during query:[/bold red] {str(e)}")
        raise typer.Exit(code=1)  # Exit with error code
    except Exception as e:  # Catch other unexpected errors during the 'ask' process
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red] {str(e)}")
        console.print_exception(show_locals=False)
        raise typer.Exit(code=1)  # Exit with error code


# --- Utility Callbacks ---

def version_callback(value: bool, app_name: str, app_version: str) -> None:
    """Callback function for the --version option. Prints version and exits."""
    if value:  # If the --version flag was passed
        console.print(f"[bold]{app_name}[/bold] version {app_version}")
        # Exit the cleanly after printing version using Typer's mechanism
        raise typer.Exit(code=0)


# Define the version option once and reuse it in the main callback
_version_option = typer.Option(
    None, "--version", "-V",  # Common flags for a version
    help="Show application version and exit.",
    # Use a lambda to pass current constants to the callback
    callback=lambda v: version_callback(v, APP_NAME, APP_VERSION),
    is_eager=True,  # Process this option before commands and other options
    rich_help_panel="About",  # Group it nicely in --help output
)


# --- Main Application Callback (Entry Point for Typer) ---

@app.callback()
def main(
        # Include the version option here
) -> None:
    f"""
    {APP_NAME}

    A command-line tool to interact with Tencent's Hunyuan model
    hosted on Gradio Spaces using the gradio_client library.

    Use '--help' after a command (e.g., `chat --help`) for command-specific options.
    """
    # This main callback runs before any command.
    # The `version_callback` (if triggered by --version) will exit before this point.
    # No other logic needed here for now.
    pass

# --- Execution Guard (Removed) ---
# NOTE: No `if __name__ == "__main__":` block is needed.
# Poetry's script entry point in pyproject.toml (`hunyuan-cli = "hunyuan_app.cli.main:app"`)
# will directly invoke the `app` object when the command is run.
