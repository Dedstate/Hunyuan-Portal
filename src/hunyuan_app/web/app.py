import logging
import os
import uuid

from dotenv import load_dotenv
from flask import (Flask, Response, flash, redirect, render_template, request,
                   session, url_for)
from markdown import markdown  # Keep for converting core response to HTML

# --- Import Core Logic ---
# Import functions, constants, and exceptions from the core client module
from hunyuan_app.core.client import (
    connect_client,  # Use this instead of local get_gradio_client
    query_hunyuan_model,  # Use this instead of local query_hunyuan_web
    DEFAULT_GRADIO_URL as CORE_DEFAULT_GRADIO_URL,  # Alias to avoid potential name clashes
    GRADIO_API_ENDPOINT as CORE_GRADIO_API_ENDPOINT,  # Alias
    ConnectionSetupError,  # Catch this during connection
    PredictionError  # Catch this during prediction
    # ConnectionError is built-in, but the core module raises it specifically
)

# --- Web App Constants ---
load_dotenv()  # Load environment variables (.env file)

# Use default from core module if env var is not set
DEFAULT_GRADIO_URL_WEB: str = os.environ.get("DEFAULT_GRADIO_URL", CORE_DEFAULT_GRADIO_URL)

# Flask specific secrets and config
DEFAULT_SECRET_KEY: str = "a_very_insecure_default_dev_secret_key_change_me"
FLASK_SECRET_KEY: str = os.environ.get("FLASK_SECRET_KEY", DEFAULT_SECRET_KEY)
FLASK_DEBUG_MODE: bool = os.environ.get("FLASK_DEBUG", "0").lower() in ['true', '1', 't']
SERVER_PORT: int = int(os.environ.get("PORT", 5000))

# Session keys remain the same
SESSION_CHAT_URL_KEY: str = 'chat_url'
SESSION_CHAT_HISTORY_KEY: str = 'chat_history'
SESSION_ASK_RESPONSE_KEY: str = 'ask_response'
SESSION_UNIQUE_ID_KEY: str = 'user_unique_id'

# --- Flask Application Setup ---
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Configure logging for Flask app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.INFO)  # Ensure Flask logger uses the configured level

if app.secret_key == DEFAULT_SECRET_KEY and not FLASK_DEBUG_MODE:
    app.logger.warning(
        "SECURITY WARNING: Using default FLASK_SECRET_KEY in a non-debug environment!"
    )


# --- Flask Routes ---

@app.route('/')
def index() -> str:
    """Renders the main index page, displaying any previous 'ask' response."""
    app.logger.debug("Rendering index page.")
    # Retrieve and remove the 'ask' response from session to display it once
    ask_response_html = session.pop(SESSION_ASK_RESPONSE_KEY, None)
    # Get current chat history for display
    chat_history = session.get(SESSION_CHAT_HISTORY_KEY, [])
    current_chat_url = session.get(SESSION_CHAT_URL_KEY, DEFAULT_GRADIO_URL_WEB)

    return render_template(
        'index.html',
        default_url=DEFAULT_GRADIO_URL_WEB,  # Pass default URL to template
        current_chat_url=current_chat_url,  # Pass current chat URL
        ask_response=ask_response_html,  # Pass single 'ask' response if available
        chat_history=chat_history  # Pass chat history
    )


@app.route('/ask', methods=['POST'])
def handle_ask() -> Response:
    """Handles form submission for the single 'ask' query."""
    app.logger.info("Received POST request for /ask.")
    url: str = request.form.get('url', DEFAULT_GRADIO_URL_WEB).strip()
    message: str = request.form.get('message', '').strip()

    # --- Input Validation ---
    if not url:
        flash("Gradio URL cannot be empty.", "warning")
        return redirect(url_for('index'))
    if not message:
        flash("Message cannot be empty.", "warning")
        return redirect(url_for('index'))

    # --- Ensure Session ID ---
    if SESSION_UNIQUE_ID_KEY not in session:
        session[SESSION_UNIQUE_ID_KEY] = str(uuid.uuid4())
        session.modified = True
        app.logger.info(f"Generated new unique ID for session: {session[SESSION_UNIQUE_ID_KEY][:8]}...")
    session_id_snippet = session.get(SESSION_UNIQUE_ID_KEY, "N/A")[:8]

    app.logger.info(f"[Session {session_id_snippet}] Processing /ask request for URL: {url}")

    try:
        # 1. Connect using the core function
        client = connect_client(url)  # Can raise ConnectionSetupError

        # 2. Query using the core function (returns raw text)
        raw_response = query_hunyuan_model(
            message=message,
            client=client,
            api_endpoint=CORE_GRADIO_API_ENDPOINT  # Use core constant
        )  # Can raise ConnectionError, PredictionError

        # 3. Convert raw response to HTML using Markdown (Web layer responsibility)
        ask_response_html: str = markdown(
            raw_response,
            extensions=['fenced_code', 'codehilite', 'extra', 'smarty']
        )

        # Store HTML response in session for display on redirect
        session[SESSION_ASK_RESPONSE_KEY] = ask_response_html
        session.modified = True
        app.logger.info(f"[Session {session_id_snippet}] Successfully processed /ask request.")

    # Catch specific exceptions from core module + general ConnectionError
    except (ConnectionSetupError, ConnectionError, PredictionError) as e:
        flash(f"Error: {str(e)}", "danger")
        app.logger.error(f"[Session {session_id_snippet}] Error during /ask processing: {e}")
    # Catch any other unexpected errors
    except Exception as e:
        app.logger.error(f"[Session {session_id_snippet}] Unexpected error in /ask route: {e}", exc_info=True)
        flash("An unexpected server error occurred. Please try again later.", "danger")

    # Redirect back to the index page to display results or errors
    return redirect(url_for('index'))


@app.route('/chat', methods=['POST'])
def handle_chat() -> Response:
    """Handles form submission for the interactive chat functionality."""
    app.logger.info("Received POST request for /chat.")
    url: str = request.form.get('url', DEFAULT_GRADIO_URL_WEB).strip()
    message: str = request.form.get('message', '').strip()
    clear_chat: bool = request.form.get('clear_chat') is not None

    # --- Session Management & Unique ID ---
    if SESSION_CHAT_URL_KEY not in session:
        session[SESSION_CHAT_URL_KEY] = url
    if SESSION_CHAT_HISTORY_KEY not in session:
        session[SESSION_CHAT_HISTORY_KEY] = []

    if SESSION_UNIQUE_ID_KEY not in session:
        session[SESSION_UNIQUE_ID_KEY] = str(uuid.uuid4())
        session.modified = True
        app.logger.info(f"Generated new unique ID for session: {session[SESSION_UNIQUE_ID_KEY][:8]}...")
    session_id_snippet = session.get(SESSION_UNIQUE_ID_KEY, "N/A")[:8]

    # --- Handle URL Change or Clear Request ---
    current_session_url = session.get(SESSION_CHAT_URL_KEY)
    if current_session_url != url or clear_chat:
        reason = 'URL changed' if current_session_url != url else 'Clear requested'
        app.logger.info(f"[Session {session_id_snippet}] Resetting chat history. Reason: {reason}")
        session[SESSION_CHAT_HISTORY_KEY] = []
        session[SESSION_CHAT_URL_KEY] = url
        session.modified = True
        if clear_chat:
            flash("Chat history cleared.", "info")
            # Redirect immediately after clearing
            return redirect(url_for('index'))
        # If only URL changed, continue processing the new message below

    # --- Input Validation ---
    if not url:  # Should use session URL after potential reset
        flash("Gradio URL cannot be empty.", "warning")
        return redirect(url_for('index'))
    if not message:
        flash("Please enter a message.", "warning")
        # Do not clear history if a message is empty, just show warning
        return redirect(url_for('index'))

    # --- Process New Message ---
    try:
        # Add a user message to history (convert to HTML)
        user_message_html: str = markdown(message, extensions=['extra', 'smarty'])
        session[SESSION_CHAT_HISTORY_KEY].append({'role': 'user', 'content': user_message_html})
        session.modified = True
        app.logger.info(f"[Session {session_id_snippet}] Added user message to chat history.")

        # 1. Connect using the core function (using URL from session)
        client = connect_client(session[SESSION_CHAT_URL_KEY])

        # 2. Query using the core function (returns raw text)
        raw_response = query_hunyuan_model(
            message=message,
            client=client,
            api_endpoint=CORE_GRADIO_API_ENDPOINT
        )

        # 3. Convert raw response to HTML using Markdown
        bot_response_html: str = markdown(
            raw_response,
            extensions=['fenced_code', 'codehilite', 'extra', 'smarty']
        )

        # Add bot response to history
        session[SESSION_CHAT_HISTORY_KEY].append({'role': 'bot', 'content': bot_response_html})
        session.modified = True
        app.logger.info(f"[Session {session_id_snippet}] Added bot response to chat history.")

    # Catch specific exceptions from core module + general ConnectionError
    except (ConnectionSetupError, ConnectionError, PredictionError) as e:
        flash(f"Error: {str(e)}", "danger")
        app.logger.error(f"[Session {session_id_snippet}] Error during /chat processing: {e}")
        # Do not add a potentially failed bot response to history
    # Catch any other unexpected errors
    except Exception as e:
        app.logger.error(f"[Session {session_id_snippet}] Unexpected error in /chat route: {e}", exc_info=True)
        flash("An unexpected server error occurred. Please try again later.", "danger")

    # Redirect back to the index page to display updated chat/errors
    return redirect(url_for('index'))


# --- Main Execution Guard (for development using `flask run` or direct execution) ---
if __name__ == '__main__':
    app.logger.info(f"Starting Flask development server. Debug mode: {FLASK_DEBUG_MODE}, Port: {SERVER_PORT}")
    # Use Flask's built-in server for development
    app.run(debug=FLASK_DEBUG_MODE, host='0.0.0.0', port=SERVER_PORT)

# --- WSGI Entry Point (for Gunicorn/production) ---
# Gunicorn will target this 'app' object directly, e.g., gunicorn "hunyuan_app.web.app:app"
# No extra code needed here for that.
