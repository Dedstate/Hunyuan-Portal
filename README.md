# Hunyuan Portal CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Add other badges if applicable, e.g., PyPI version, build status, code style -->
<!-- [![PyPI version](https://badge.fury.io/py/hunyuan-portal.svg)](https://badge.fury.io/py/hunyuan-portal) -->
<!-- [![Build Status](https://travis-ci.org/Dedstate/Hunyuan-Portal.svg?branch=main)](https://travis-ci.org/Dedstate/Hunyuan-Portal) -->

**A user-friendly command-line interface (CLI) to interact with Tencent's Hunyuan models hosted on Gradio Spaces.**

This tool allows you to easily chat with or send single queries to Hunyuan models directly from your terminal, providing
a streamlined alternative to web interfaces.

## ✨ Features

* **Interactive Chat:** Engage in back-and-forth conversations (`chat` command).
* **Single Queries:** Send a one-off prompt and get a response (`ask` command).
* **Flexible Connection:** Connect to the official Hunyuan space or any other compatible Gradio endpoint via URL or
  Hugging Face repo ID.
* **Formatted Output:** Responses rendered beautifully in Markdown (default) or plain text using Rich.
* **File Saving:** Option to save model responses directly to a file.
* **User-Friendly:** Progress indicators for API calls and clear error messages.

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Dedstate/Hunyuan-Portal.git
   cd Hunyuan-Portal
   ```

2. **Install dependencies:** (Requires Python 3.8+)
    * **Using Poetry (Recommended):**
      ```bash
      # Install poetry if you haven't already: https://python-poetry.org/docs/#installation
      poetry install
      ```
    * **Using pip:**
      ```bash
      # First, generate requirements.txt if needed (using Poetry):
      # poetry export -f requirements.txt --output requirements.txt --without-hashes
      python -m pip install -r requirements.txt
      # Or install directly from pyproject.toml (might need recent pip):
      # python -m pip install .
      ```
      *(Note: For pip users without Poetry, ensure a `requirements.txt` is available or instruct them to
      use `pip install .`)*

3. **Run:**
    * **Interactive Chat:**
      ```bash
      # If using Poetry
      poetry run python hunyuan.py chat

      # If installed globally or in a virtualenv with pip
      python hunyuan.py chat
      ```
    * **Single Question:**
      ```bash
      # If using Poetry
      poetry run python hunyuan.py ask "Explain the basics of quantum computing."

      # If installed globally or in a virtualenv with pip
      python hunyuan.py ask "Explain the basics of quantum computing."
      ```

## 📦 Installation

Requires **Python 3.8+** and **Git**.

Choose one of the following methods:

1. **Using Poetry (Recommended for development & isolated environment):**
   ```bash
   git clone https://github.com/Dedstate/Hunyuan-Portal.git
   cd Hunyuan-Portal
   poetry install
   # Run commands with `poetry run python hunyuan.py ...`
   ```

2. **Using pip directly from GitHub:**
   ```bash
   python -m pip install git+https://github.com/Dedstate/Hunyuan-Portal.git
   # Now you *might* be able to run commands directly (if PATH is configured and entry point exists)
   # Example: hunyuan --version
   # Otherwise, run via: python -m hunyuan <command> or python <path_to_script>/hunyuan.py <command>
   ```
   *(Note: A direct command like `hunyuan` requires an entry point configured in `pyproject.toml`)*

3. **Editable install (for development with pip):**
   ```bash
   git clone https://github.com/Dedstate/Hunyuan-Portal.git
   cd Hunyuan-Portal
   python -m pip install -e .
   # Run commands with `python hunyuan.py ...`
   ```

## 🖥️ Usage

The CLI provides two main commands: `chat` and `ask`.

```bash
python hunyuan.py [COMMAND] [ARGUMENTS] [OPTIONS]
```

### `chat` - Interactive Chat Session

Starts a loop where you can send messages to the model and receive replies. Type `exit` or `quit` to end the session.

```bash
python hunyuan.py chat [OPTIONS]
```

**Options:**

* `--url TEXT`, `-u TEXT`: URL or Hugging Face repo ID for the Gradio Space.
  (Default: `tencent/Hunyuan-T1`)

**Example:**

```bash
$ python hunyuan.py chat -u tencent/Hunyuan-Pro
Attempting to connect to Gradio Space: [cyan]tencent/Hunyuan-Pro[/cyan]...
[green]Successfully connected to [bold]tencent/Hunyuan-Pro[/bold][/green]

[bold blue]Interactive Chat Mode[/]
Type your message and press Enter. Use 'exit' or 'quit' to end.
───────────────────────────────────────────────────────────────────────────────
You: Hello! How are you?
Querying Hunyuan...

[green]Hunyuan:[/green]
Hello! I'm an AI language model, doing great and ready to assist you. How can I help you today?
───────────────────────────────────────────────────────────────────────────────
You: exit
[yellow]Exiting chat session.[/yellow]
```

### `ask` - Single Query

Sends one message to the model, prints the response, and exits.

```bash
python hunyuan.py ask <MESSAGE> [OPTIONS]
```

**Arguments:**

* `MESSAGE`: The prompt/question to send to the model (required). Enclose in quotes if it contains spaces.

**Options:**

* `--url TEXT`, `-u TEXT`: URL or Hugging Face repo ID for the Gradio Space.
  (Default: `tencent/Hunyuan-T1`)
* `--markdown` / `--no-markdown`: Output response as Markdown (default) or raw text.
* `--output PATH`, `-o PATH`: Save the response to the specified file instead of printing to the console.

**Examples:**

1. **Simple query (Markdown output):**
   ```bash
   python hunyuan.py ask "Write a short poem about stars."
   ```

2. **Query with plain text output:**
   ```bash
   python hunyuan.py ask "List three benefits of Python." --no-markdown
   ```

3. **Saving response to a file:**
   ```bash
   python hunyuan.py ask "Generate Python code for a simple calculator." -o calculator.py
   ```

4. **Using a different model endpoint:**
   ```bash
   python hunyuan.py ask "What is the capital of France?" -u some-other/hunyuan-variant
   ```

## ⚙️ Configuration

Currently, configuration is handled directly via command-line options (`--url`, `--markdown`/`--no-markdown`,
`--output`). There is no separate configuration file (`.env`) support in this version.

## 🛠️ Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Dedstate/Hunyuan-Portal.git
   cd Hunyuan-Portal
   ```

2. **Install dependencies (including development tools):**
   ```bash
   # Ensure dev dependencies are listed under [tool.poetry.group.dev.dependencies] in pyproject.toml
   poetry install --with dev
   # Or if all dependencies are needed:
   # poetry install
   ```
   *(Make sure linters like `ruff` or `black`, and test runners like `pytest` are included as development dependencies
   in `pyproject.toml`)*

3. **Running Tests (Example - if tests exist):**
   ```bash
   # Ensure you have tests in a 'tests/' directory and pytest installed
   poetry run pytest
   ```

4. **Code Style:**
    * Consider using tools like Black and Ruff for consistent code formatting and linting.
    * Example commands (if configured):
      ```bash
      poetry run black .
      poetry run ruff check . --fix
      ```

## 🤝 Contributing

Contributions are welcome! If you have suggestions, bug reports, or want to contribute code:

1. **Check for existing issues:** Please search the [Issues](https://github.com/Dedstate/Hunyuan-Portal/issues) page to
   see if your question or bug has already been reported.
2. **Open an issue:** If not, please open a new issue to describe the bug, suggest an enhancement, or ask a question.
3. **Submit a Pull Request:** For code contributions, please fork the repository, create a new branch for your feature
   or fix, and submit a Pull Request. Ensure your code follows the project's style and includes tests if applicable.

## 🔄 Updating

* **If you installed via `git clone`:**
  ```bash
  cd Hunyuan-Portal
  git pull origin main  # Or the branch you are tracking
  # Update dependencies
  poetry install        # If using Poetry
  # Or: python -m pip install -e . --upgrade # If using editable pip install
  ```

* **If you installed via `pip install git+...`:**
  ```bash
  python -m pip install --upgrade git+https://github.com/Dedstate/Hunyuan-Portal.git
  ```

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details. *(Note: Ensure a `LICENSE` file
containing the MIT license text exists in the repository).*

## 📧 Contact

For issues or questions regarding the tool, please use
the [GitHub Issues](https://github.com/Dedstate/Hunyuan-Portal/issues) page.
