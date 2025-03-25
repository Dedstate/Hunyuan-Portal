"""
Hunyuan Portal CLI: Interact with Tencent's Hunyuan model via Gradio.

This script provides a command-line interface (CLI) using Typer and Rich
to interact with Hunyuan models hosted on Hugging Face Gradio Spaces.
It allows for interactive chat sessions or sending single queries.
"""

from pathlib import Path
from typing import Optional

import typer
from gradio_client import Client as GradioClient
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule

# --- Constants ---
APP_NAME: str = "Hunyuan Portal (CLI)"
APP_VERSION: str = "3.1.1"
DEFAULT_GRADIO_URL: str = "tencent/Hunyuan-T1"
GRADIO_API_ENDPOINT: str = "/chat"  # Define the specific API endpoint name

# --- Application Setup ---

# Initialize Rich Console for pretty printing
console = Console()

# Initialize Typer application
# Use Markdown for rich formatting in help messages
app = typer.Typer(
    rich_markup_mode="markdown",
    help=f"{APP_NAME} - Interact with Hunyuan models on Gradio.",
    add_completion=False,  # Disable shell completion for simplicity
)


# --- Core Logic Functions ---

def _connect_client(url: str) -> GradioClient:
    """
    Attempts to connect to the specified Gradio Space.

    Handles initialization errors and provides user feedback.
    Exits application
    gracefully with an error code if connection fails.

    Args:
        url: The URL or Hugging Face repo ID of the Gradio Space.

    Returns:
        An initialized and connected GradioClient instance.

    Raises:
        typer.Exit: If the connection or client initialization fails.
    """
    console.print(f"Attempting to connect to Gradio Space: [cyan]{url}[/cyan]...")
    try:
        # Initialize the Gradio client.
        # This might raise errors for various reasons
        # (invalid URL format, network issues during initial checks, etc.).
        client = GradioClient(url)
        console.print(f"[green]Successfully connected to [bold]{url}[/bold][/green]")
        return client
    except Exception as e:
        # Catch a broad range of exceptions during initialization
        console.print(f"\n[bold red]Fatal Connection Error:[/bold red] Could not initialize client for '{url}'.")
        console.print(f"[red]Details:[/red] {e}")
        console.print(
            "\n[yellow]Possible reasons:[/yellow]\n"
            "- Incorrect URL or Hugging Face repo ID.\n"
            "- Gradio Space is not running or is private.\n"
            "- Network connectivity issues."
        )
        console.print("[yellow]Please check the URL/ID and ensure the Space is accessible.[/yellow]")
        # Exit the application with a non-zero status code indicating failure
        raise typer.Exit(code=1)


def query_hunyuan(message: str, client: GradioClient, show_progress: bool = True) -> str:
    """
    Sends a message to the connected Hunyuan model via the Gradio client.

    Handles API call errors and displays optional progress indication.

    Args:
        message: The input message/prompt for the model.
        client: An initialized GradioClient instance.
        show_progress: Whether to display a progress spinner during the API call.

    Returns:
        The model's response as a string.
        Returns an empty string if the response is None.

    Raises:
        ConnectionError: If the API call fails due to network/connection issues.
        RuntimeError: For other unexpected errors during the prediction process.
    """
    task_description: str = "Querying Hunyuan..."

    try:
        response: Optional[str]  # Declare a type hint for clarity

        if show_progress:
            # Use Rich Progress to show a spinner during the potentially long API call
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,  # Remove progress display upon completion
                    console=console,
            ) as progress:
                progress.add_task(task_description, total=None)  # Indeterminate progress
                # IMPORTANT: Pass arguments positionally to client.predict,
                # matching the order expected by the Gradio API function.
                response = client.predict(
                    message,  # First positional argument
                    api_name=GRADIO_API_ENDPOINT  # Specify the target API function
                )
        else:
            # Make the prediction call without the progress display
            response = client.predict(
                message,
                api_name=GRADIO_API_ENDPOINT
            )

        # Ensure a string is returned even if the API gives None
        return str(response) if response is not None else ""

    except ConnectionError as e:
        # Handle network errors during the API call specifically
        console.print_exception(show_locals=False)  # Show traceback for debugging
        # Re-rise as ConnectionError for specific handling upstream
        raise ConnectionError(f"Gradio API call failed due to network issue: {e}") from e
    except Exception as e:
        # Handle other errors that might occur during the prediction process
        # (e.g., errors within the Gradio app logic, protocol errors, timeouts)
        console.print_exception(show_locals=False)
        # Re-raise as RuntimeError for general prediction failures
        raise RuntimeError(f"An unexpected error occurred during prediction: {e}") from e


# --- Typer Command Definitions ---

@app.command()
def chat(
        url: str = typer.Option(
            DEFAULT_GRADIO_URL,
            "--url",
            "-u",  # Short alias for the option
            help="URL or Hugging Face repo ID for the Gradio Space.",
            rich_help_panel="Connection Settings",  # Group option in help message
        ),
) -> None:
    """
    Start an interactive CLI chat session with the Hunyuan model.

    Continuously prompts the user for input and displays the model's responses
    until 'exit' or 'quit' is entered.
    """
    # Establish connection first
    client = _connect_client(url)

    # Print instructions for the chat mode
    console.print("\n[bold blue]Interactive Chat Mode[/]")
    console.print("Type your message and press Enter. Use 'exit' or 'quit' to end.")
    console.print(Rule(style="blue"))  # Visual separator

    # Main interaction loop
    while True:
        try:
            # Prompt user for input
            message = console.input("[bold]You:[/bold] ")
        except (EOFError, KeyboardInterrupt):
            # Handle Ctrl+D (EOF) or Ctrl+C (Interrupt) gracefully
            console.print("\n[yellow]Exiting chat session.[/yellow]")
            break  # Exit the loop

        # Strip whitespace and check for exit commands
        cleaned_message = message.strip()
        if cleaned_message.lower() in ("exit", "quit"):
            console.print("[yellow]Exiting chat session.[/yellow]")
            break  # Exit the loop
        if not cleaned_message:
            # If user just pressed Enter, prompt again
            continue

        # Query the model and handle potential errors
        try:
            response = query_hunyuan(cleaned_message, client, show_progress=True)

            # Display the model's response using Markdown formatting
            console.print(f"\n[green]Hunyuan:[/green]")
            console.print(Markdown(response))
            console.print(Rule(style="green"))  # Visual separator

        except ConnectionError as e:
            # Handle API connection errors specifically during the chat loop
            console.print(f"\n[bold red]API Call Error:[/bold red] {str(e)}")
            console.print("[yellow]Please check connection or endpoint status. You can try again.[/yellow]")
            console.print(Rule(style="red"))
        except RuntimeError as e:
            # Handle general prediction errors during the chat loop
            console.print(f"\n[bold red]Prediction Error:[/bold red] {str(e)}")
            console.print(Rule(style="red"))
        except Exception as e:
            # Catch any other unexpected errors within the loop to prevent crashing
            console.print(f"\n[bold red]An unexpected error occurred in the chat loop:[/bold red] {str(e)}")
            console.print_exception(show_locals=False)
            console.print(Rule(style="red"))
            # Consider whether breaking or continue after an unexpected error


@app.command()
def ask(
        # Use typer.Argument for required positional command-line arguments
        message: str = typer.Argument(..., help="The message/prompt to send to the model."),
        url: str = typer.Option(
            DEFAULT_GRADIO_URL,
            "--url", "-u",
            help="URL or Hugging Face repo ID for the Gradio Space.",
            rich_help_panel="Connection Settings",
        ),
        markdown_output: bool = typer.Option(
            True,  # Default value is True (output as Markdown)
            "--markdown/--no-markdown",  # Defines both --Markdown and --no-markdown flags
            help="Output response as Markdown (default) or raw text.",
            rich_help_panel="Display Options",
        ),
        output_file: Optional[Path] = typer.Option(
            None,  # Default is None (print to console)
            "--output", "-o",
            help="Save response to a file instead of printing to console.",
            rich_help_panel="Output Options",
            writable=True,  # Ensure the path is writable
            resolve_path=True,  # Resolve to an absolute path
            dir_okay=False,  # Ensure it is a file path, not a directory
        ),
) -> None:
    """
    Send a single message (prompt) to the Hunyuan model and display or save the response.
    """
    # Establish connection
    client = _connect_client(url)
    console.print(" ")  # Add a blank line for spacing

    try:
        # Query the model
        response = query_hunyuan(message, client, show_progress=True)

        # Handle output: either save to file or print to console
        if output_file:
            try:
                # Ensure parent directory exists
                output_file.parent.mkdir(parents=True, exist_ok=True)
                # Write the response to the specified file
                output_file.write_text(response, encoding="utf-8")
                console.print(f"[green]Response successfully saved to: [cyan]{output_file}[/cyan][/green]")
            except IOError as e:
                # Handle potential file writing errors
                console.print(f"[bold red]Error writing to file {output_file}:[/bold red] {e}")
                raise typer.Exit(code=1)  # Exit with error code if file writing fails
        elif markdown_output:
            # Print response formatted as Markdown
            console.print(f"[green]Hunyuan Response:[/green]")
            console.print(Markdown(response))
        else:
            # Print response as raw text
            console.print(f"[dim]Hunyuan Response (Raw):[/dim]")
            console.print(response)

    except ConnectionError as e:
        # Handle API connection errors specifically for the 'ask' command
        console.print(f"\n[bold red]API Call Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)  # Exit with error code
    except RuntimeError as e:
        # Handle general prediction errors for the 'ask' command
        console.print(f"\n[bold red]Prediction Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)  # Exit with error code
    except Exception as e:
        # Catch any other unexpected errors during the 'ask' process
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red] {str(e)}")
        console.print_exception(show_locals=False)
        raise typer.Exit(code=1)  # Exit with error code


# --- Utility Callbacks (e.g., for --version) ---

def version_callback(value: bool) -> None:
    """
    Callback function for the --version option. Prints version and exits.
    """
    if value:  # If the --version flag was passed
        console.print(f"[bold]{APP_NAME}[/bold] version {APP_VERSION}")
        # Exit a cleanly after printing version
        raise typer.Exit(code=0)


# --- Main Application Callback and Entry Point ---

@app.callback()
def main(
) -> None:
    """
    {APP_NAME}

    A command-line tool to interact with Tencent's Hunyuan model
    hosted on Gradio Spaces.

    Use '--help' after a command (e.g., `chat --help`) for command-specific options.
    """
    # This main callback runs before any command.
    # We primarily use it here for the --version option setup.
    # If `version_callback` is triggered, it exits before reaching here.
    pass


# --- Main Execution Guard ---
if __name__ == "__main__":
    # Run the Typer application
    # Typer handles command-line argument parsing and calling the appropriate command function.
    app()
