# Hunyuan Portal ✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Interact with Tencent's Hunyuan models—your way.**  
Use an intuitive Web App or a powerful Command-Line Interface (CLI) to chat and query models hosted on Gradio Spaces.

---

> **Hunyuan Portal** offers a seamless experience for users who want either a modern web UI or a scriptable CLI to communicate with Hunyuan models. Built with Flask, Typer, Rich, and Gradio-Client.

<!--
OPTIONAL: Add a side-by-side screenshot or GIF here showing both the Web UI and CLI in use!
Example:
![Web and CLI Screenshot Collage](link/to/your/screenshot_collage.png)
-->

---

## 🌟 Features

- **Choose Your Interface:**  
  - **Web:** Fast, responsive chat and Q&A in your browser.
  - **CLI:** Scriptable, efficient CLI for single queries or interactive chat.

- **Flexible Connection:**  
  Connect to the official Hunyuan Space or any compatible Gradio endpoint (URL or Hugging Face repo ID).

- **Chat or Ask:**  
  - **Web:** Real-time chat with scrollable history, or quick single-question forms.
  - **CLI:** `chat` for ongoing conversation, `ask` for one-off questions.

- **Beautiful Output:**  
  - **Web:** Clean, copy-friendly responses.
  - **CLI:** Markdown-formatted output using Rich, or switch to plain text.

- **Save Responses (CLI):**  
  Save model replies directly to files.

- **Easy Setup:**  
  Configure secrets and defaults with a `.env` file.

- **User-Friendly:**  
  Progress spinners, helpful startup messages, and clear error handling in both interfaces.

---

## 🚀 Quickstart

> **Requirements:**  
> - Python 3.10+  
> - Git

#### 1. Clone the Repository

```bash
git clone https://github.com/Dedstate/Hunyuan-Portal.git
cd Hunyuan-Portal
```

#### 2. Install Poetry (Recommended)

If you don’t have it yet: [Poetry Install Guide](https://python-poetry.org/docs/#installation)

#### 3. Install Dependencies

Install everything (web UI, CLI, and dev tools):

```bash
poetry install --with web,cli,dev
```

- _Just the CLI?_ `poetry install --with cli`
- _Just the Web UI?_ `poetry install --with web`

---

## ⚙️ Configuration

All configuration is handled via a `.env` file in your project root.

1. **Create a `.env` file:**  
   Copy the example or create your own:

   ```bash
   cp .env.example .env
   # Or touch .env and add variables manually
   ```

2. **Edit your `.env`:**

   At minimum, set a secure `FLASK_SECRET_KEY` for the web UI:

   ```dotenv
   # Required for Flask sessions (Web UI)
   FLASK_SECRET_KEY='your_super_secret_random_string_here_3498tguib#$@'

   # Optional: Override Gradio space URL/ID (default points to tencent/Hunyuan-Pro)
   # DEFAULT_GRADIO_URL='tencent/Hunyuan-Pro'

   # Optional: Web server port (default 5000)
   PORT=5000

   # Optional: Flask debug mode (1 = True, 0 = False)
   FLASK_DEBUG=1

   # Optional: Host for the web server (default 0.0.0.0)
   # FLASK_RUN_HOST=0.0.0.0

   # Optional: Number of threads for Waitress (default 4)
   # WAITRESS_THREADS=8
   ```

3. **Security:**  
   Add `.env` to your `.gitignore` to avoid leaking secrets:

   ```gitignore
   .env
   ```

---

## 🖥️ Using the Web App

1. **Start the server:**

   ```bash
   poetry run hunyuan-web
   ```

2. **Open your browser:**  
   Visit [http://localhost:5000](http://localhost:5000) (or use your configured port).

3. **Interact:**  
   - **Ask a Single Question:** Get immediate answers.
   - **Chat:** Enjoy a full-featured conversation interface with history.
   - **Clear Chat:** Reset your session easily.
   - **Change Gradio URL:** Point to any compatible backend on demand.

4. **Stop the server:** Press `Ctrl+C` in your terminal.

---

## 💻 Using the CLI

1. **Get help:**

   ```bash
   poetry run hunyuan-cli --help
   ```

2. **Ask a single question:**

   ```bash
   poetry run hunyuan-cli ask "Explain quantum entanglement."
   ```

   - Save output to a file:
     ```bash
     poetry run hunyuan-cli ask "Generate a Python fizzbuzz." -o fizzbuzz.py
     ```
   - Use a different Gradio Space and plain text output:
     ```bash
     poetry run hunyuan-cli ask "Custom prompt" -u user/other-model --no-markdown
     ```

3. **Start an interactive chat:**

   ```bash
   poetry run hunyuan-cli chat
   ```

   - To specify a different Gradio Space:
     ```bash
     poetry run hunyuan-cli chat -u tencent/Hunyuan-Pro
     ```
   - Exit: Type `exit`, `quit`, or press `Ctrl+C`.

---

## 🛠️ Development

1. **Install:**  
   See [Quickstart](#-quickstart) above (be sure to include `--with dev`).

2. **Activate the environment:**

   ```bash
   poetry shell
   ```

3. **Run tests:**

   ```bash
   pytest
   ```

4. **Format and lint your code:**

   ```bash
   black .
   ruff check . --fix
   ruff format .
   ```

---

## 🤝 Contributing

Contributions and feedback are always welcome!

- [Open an issue](https://github.com/Dedstate/Hunyuan-Portal/issues) for bugs, features, or questions.
- Fork the repo and submit a pull request for changes.

---

## 🔄 Updating

Update your local repository and dependencies:

```bash
cd Hunyuan-Portal
git pull origin main
poetry install --with web,cli,dev
```

---

## 📄 License

MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📫 Contact

For support or questions, please use [GitHub Issues](https://github.com/Dedstate/Hunyuan-Portal/issues).
