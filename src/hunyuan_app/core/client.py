from typing import Optional

# Import GradioClient and specific errors if needed elsewhere,
# but we will not use a specific one in connect_client's except block now.
from gradio_client import Client as GradioClient

# from gradio_client import errors as gradio_errors # Keep if needed for query_hunyuan_model

# --- Constants related to the service ---
DEFAULT_GRADIO_URL: str = "tencent/Hunyuan-T1"
GRADIO_API_ENDPOINT: str = "/chat"


# --- Custom Exceptions ---
class ConnectionSetupError(Exception):
    """Custom exception for errors during Gradio client initialization."""
    pass


class PredictionError(Exception):
    """Custom exception for errors during the prediction call."""
    pass


# --- Core Functions ---

# Optional: Setup logging if you want more detailed internal logs
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO) # Configure as needed

def connect_client(url: str) -> GradioClient:
    """
    Attempts to connect to the specified Gradio Space.

    Args:
        url: The URL or Hugging Face repo ID of the Gradio Space.

    Returns:
        An initialized GradioClient instance.

    Raises:
        ConnectionSetupError: If the connection or client initialization fails.
    """
    # logger.info(f"Attempting to connect to Gradio Space: {url}")
    try:
        client = GradioClient(url)
        # logger.info(f"Successfully connected to {url}")
        return client
    # CORRECTED except block: Removed gradio_utils.error.Error
    except (ValueError, Exception) as e:
        # Catch ValueError for bad URLs and general Exception for others
        # (like network issues, space not found errors during init).
        error_message = f"Could not initialize client for '{url}'. Reason: {e}"
        # logger.error(error_message, exc_info=True) # Log detailed error if needed
        raise ConnectionSetupError(error_message) from e


def query_hunyuan_model(
        message: str,
        client: GradioClient,
        api_endpoint: str = GRADIO_API_ENDPOINT
) -> str:
    """
    Sends a message to the connected Hunyuan model via the Gradio client.

    Args:
        message: The input message/prompt for the model.
        client: An initialized GradioClient instance.
        api_endpoint: The specific API endpoint name on the Gradio server.

    Returns:
        The model's response as a string. Returns an empty string if the
        response is None.

    Raises:
        ConnectionError: If the API call fails due to network/connection issues.
        PredictionError: For other unexpected errors during the prediction.
    """
    try:
        # logger.debug(f"Querying endpoint '{api_endpoint}' with message: '{message[:50]}...'")
        response: Optional[str] = client.predict(
            message,
            api_name=api_endpoint
        )
        # logger.debug(f"Received response: '{str(response)[:50]}...'")

        return str(response) if response is not None else ""

    except ConnectionError as e:
        # Handle network errors during the API call specifically
        # logger.error(f"Gradio API call failed due to network issue: {e}", exc_info=False)
        # Re-raise for the caller (CLI) to handle
        raise ConnectionError(f"Gradio API call failed due to network issue: {e}") from e
    except Exception as e:
        # Handle other errors (e.g., internal Gradio app errors, timeouts)
        # logger.error(f"An unexpected error occurred during prediction: {e}", exc_info=True)
        # Re-rise as a custom error for the caller (CLI) to handle
        raise PredictionError(f"An unexpected error occurred during prediction: {e}") from e
