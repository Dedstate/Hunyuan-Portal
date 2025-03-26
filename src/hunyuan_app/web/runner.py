import os
import subprocess
import sys

from dotenv import load_dotenv

# Load .env from the project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)


def main():
    """Starts the web server using Waitress and prints the access URL."""
    # --- Configuration ---
    # Use 0.0.0.0 for binding, but localhost for the clickable link
    bind_host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    port = os.environ.get("PORT", "5000")
    threads = os.environ.get("WAITRESS_THREADS", "4")
    app_module = "hunyuan_app.web.app:app"  # Your Flask app location

    # --- Construct Waitress command ---
    waitress_cmd = [
        sys.executable,  # Use the Python executable from the virtual environment
        "-m", "waitress",  # Run waitress as a module
        f"--host={bind_host}",  # Tell waitress which IP to bind to
        f"--port={port}",  # Tell the waitress that ports to bind to
        f"--threads={threads}",  # Set the number of worker threads
        app_module,  # The module:variable containing the Flask app
    ]

    print(f"Starting Waitress with command: {' '.join(waitress_cmd)}")

    # --- Initialize process variable ---
    process = None
    try:
        # --- Start Waitress Subprocess ---
        # Use Popen to start waitress in the background relative to this script
        process = subprocess.Popen(waitress_cmd)

        # --- Print a Helpful User Message with Clickable Link ---
        # Construct the URL the user should actually use in their browser
        access_url = f"http://localhost:{port}"  # Use localhost for the clickable link
        print("-" * 40)
        print(f"Server should be accessible at: {access_url}")
        print("Press Ctrl+C to stop the server.")
        print("-" * 40)
        # ---

        # --- Wait for the Waitress to Exit ---
        # The runner script will now wait here until the waitress stops
        # (e.g., due to Ctrl+C or an internal error)
        exit_code = process.wait()

        # Check exit code after wait returns normally
        if exit_code != 0:
            print(f"Waitress exited with error code: {exit_code}", file=sys.stderr)
            sys.exit(exit_code)

    except FileNotFoundError:
        print(f"\nError: Command not found '{waitress_cmd[0]}' or 'waitress'.", file=sys.stderr)
        print("Please ensure Waitress is installed in your environment (`poetry install --with web`).", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nCtrl+C received. Shutting down waitress...")
        if process and process.poll() is None:  # Check if a process exists and is running
            process.terminate()  # Send SIGTERM (or equivalent signal on Windows)
            try:
                process.wait(timeout=5)  # Wait up to 5 seconds for a graceful shutdown
            except subprocess.TimeoutExpired:
                print("Waitress did not exit gracefully after 5s, forcing kill.")
                process.kill()  # Force kill if it does not stop
        print("Server stopped.")
        sys.exit(0)  # Exit cleanly after user interruption
    except Exception as e:
        # Catch any other unexpected errors during startup or waiting
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        if process and process.poll() is None:
            print("Attempting to kill waitress process after error.")
            process.kill()
        sys.exit(1)  # Exit with a non-zero code indicating an error


if __name__ == "__main__":
    main()
