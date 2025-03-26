# Hunyuan Portal ✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Add other badges like PyPI version once published -->
<!-- [![PyPI version](https://badge.fury.io/py/hunyuan-app.svg)](https://badge.fury.io/py/hunyuan-app) -->

**Interact with Tencent's Hunyuan models hosted on Gradio Spaces through a user-friendly Web Interface or directly from
your Command-Line (CLI).**

This portal provides two convenient ways to chat with or send single queries to Hunyuan models, powered by Flask, Typer,
Rich, and Gradio-Client.

**(Optional: Add a Screenshot/GIF here showing both the Web UI and the CLI in action)**
<!--
![Screenshot Collage](link/to/your/screenshot_collage.png)
-->

## Key Features

* **Dual Interfaces:** Choose between a feature-rich Web UI or a fast CLI.
* **Flexible Connection:** Connect to the official Hunyuan space or any compatible Gradio endpoint (via URL or Hugging
  Face repo ID).
* **Interactive Chat:**
    * **Web:** Real-time chat interface with scrollable history.
    * **CLI:** Simple, terminal-based back-and-forth conversation (`hunyuan-cli chat`).
* **Single Queries:**
    * **Web:** Get quick answers displayed directly on the page.
    * **CLI:** Send a one-off prompt and get a response (`hunyuan-cli ask`).
* **Formatted Output (CLI):** Responses rendered beautifully in Markdown (default) or plain text using Rich.
* **File Saving (CLI):** Option to save CLI responses directly to a file.
* **Configuration:** Use a `.env` file for easy configuration of secrets and defaults.
* **User-Friendly:** Progress indicators (CLI), helpful startup messages (Web), and clear error handling.

## 🚀 Installation

Requires **Python 3.10+** and **Git**.

**Using Poetry (Strongly Recommended):**

Poetry handles dependency management and virtual environments gracefully.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Dedstate/Hunyuan-Portal.git
   cd Hunyuan-Portal
   ```

2. **Install Poetry:**
   If you don't have Poetry, follow the instructions on
   the [official Poetry website](https://python-poetry.org/docs/#installation).

3. **Install dependencies:**
   This command installs the core application, plus the dependencies needed for both the web and CLI interfaces. It also
   includes development tools if you plan to contribute.
   ```bash
   poetry install --with web,cli,dev
   ```
    * *Just want the CLI?* `poetry install --with cli`
    * *Just want the Web UI?* `poetry install --with web`

## ⚙️ Configuration (`.env` File)

This project uses a `.env` file in the project's root directory (`Hunyuan-Portal/`) for configuration.

1. **Create the file:** Copy the example or create a new `.env` file:
   ```bash
   cp .env.example .env # If you create an example file
   # Or just create an empty .env file and add variables
   ```

2. **Edit `.env`:** Add the following variables (at minimum `FLASK_SECRET_KEY` is required for the web interface):

   ```dotenv
   # REQUIRED for Flask sessions (Web UI) - Make this long and random!
   FLASK_SECRET_KEY='your_super_secret_random_string_here_3498tguib#$@'

   # Optional: Override default Gradio space URL/ID
   # DEFAULT_GRADIO_URL='tencent/Hunyuan-Pro'

   # Optional: Set port for the web server (Default is 5000)
   PORT=5000

   # Optional: Enable Flask debug mode (1 = True, 0 = False). Enables auto-reload for Waitress.
   FLASK_DEBUG=1

   # Optional: Set host for the web server (Default is 0.0.0.0)
   # FLASK_RUN_HOST=0.0.0.0

   # Optional: Set number of threads for Waitress (Default is 4)
   # WAITRESS_THREADS=8
   ```

3. **IMPORTANT:** Add `.env` to your `.gitignore` file to prevent accidentally committing secrets!
   ```gitignore
   # .gitignore
   .env
   # other ignored files...
   ```

## 🖥️ Usage

Make sure you are in the project's root directory (`Hunyuan-Portal/`) in your terminal.

### Using the Web Interface

The web interface provides a graphical way to ask single questions or chat interactively.

1. **Start the Web Server:**
   This command uses the `runner.py` script to launch the Waitress WSGI server (which works on Windows, Linux, macOS).
   ```bash
   poetry run hunyuan-web
   ```

2. **Access in Browser:**
   Waitress will start and the script will print the URL. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```
   *(Use the port number specified in your `.env` file or the default 5000)*.

3. **Interact:**
    * Use the **"Ask a Single Question"** form for one-off queries. The response will appear below the form.
    * Use the **"Chat"** form for conversations. The history will update below the form.
    * Use the **"Clear Chat"** button within the chat form to reset the conversation history.
    * Changing the **Gradio URL** in either form will use that URL for the request (and clear chat history if changed in
      the chat form).

4. **Stop the Server:** Go back to the terminal where you ran `poetry run hunyuan-web` and press `Ctrl+C`.

### Using the Command-Line Interface (CLI)

The CLI is ideal for quick queries or scripting.

1. **Get Help:**
   ```bash
   poetry run hunyuan-cli --help
   ```

2. **`ask` Command (Single Query):**
   ```bash
   # Basic query
   poetry run hunyuan-cli ask "Explain the theory of relativity simply."

   # Save response to file
   poetry run hunyuan-cli ask "Generate Python code for FizzBuzz." -o fizzbuzz.py

   # Use a different Gradio Space and raw output
   poetry run hunyuan-cli ask "Test query" -u user/other-model --no-markdown
   ```

3. **`chat` Command (Interactive Session):**
   ```bash
   poetry run hunyuan-cli chat
   ```
   *(Type `exit` or `quit` or press `Ctrl+C` to end)*

   ```bash
   # Start chat with a specific Gradio Space
   poetry run hunyuan-cli chat -u tencent/Hunyuan-Pro
   ```

## 🛠️ Development

1. **Clone & Install:** Follow the Poetry installation steps, ensuring you install with `--with dev` (included in the
   default install command above).
2. **Activate Environment:** Use `poetry shell` to activate the virtual environment for easier command execution.
3. **Running Tests (Example):**
   ```bash
   # Assuming tests are in a 'tests/' directory and pytest is a dev dependency
   pytest
   ```
4. **Code Style/Linting (Example):**
   ```bash
   # Assuming Black and Ruff are dev dependencies
   black .
   ruff check . --fix
   ruff format .
   ```

## 🤝 Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

1. Check existing [Issues](https://github.com/Dedstate/Hunyuan-Portal/issues).
2. Open a new issue for bugs, features, or questions.
3. For code changes, fork the repo, create a branch, and submit a PR.

## 🔄 Updating

If you cloned the repository:

```bash
cd Hunyuan-Portal
git pull origin main # Or your primary branch
poetry install --with web,cli,dev # Update dependencies
```

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details. *(Make sure a `LICENSE` file with
the MIT license text exists).*

## Contact

For issues or questions, please use the [GitHub Issues](https://github.com/Dedstate/Hunyuan-Portal/issues) page.
