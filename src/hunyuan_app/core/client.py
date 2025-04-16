import logging
from typing import Optional

from gradio_client import Client as GradioClient

DEFAULT_GRADIO_URL: str = "tencent/Hunyuan-T1"
GRADIO_API_ENDPOINT: str = "/chat"

# Optionally, allow users of this module to enable debug-level logging
logger = logging.getLogger("hunyuan_app.core.client")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class ConnectionSetupError(Exception):
    """Custom exception for errors during Gradio client initialization."""
    pass


class PredictionError(Exception):
    """Custom exception for errors during the prediction call."""
    pass


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
    logger.info(f"Attempting to connect to Gradio Space: {url}")
    try:
        client = GradioClient(url)
        logger.info(f"Successfully connected to {url}")
        return client
    except ValueError as e:
        # ValueError for bad URLs
        error_message = f"Invalid URL or repo ID '{url}': {e}"
        logger.error(error_message)
        raise ConnectionSetupError(error_message) from e
    except Exception as e:
        # Network issues, Space not found, or other errors
        error_message = f"Could not initialize client for '{url}'. Reason: {e}"
        logger.error(error_message, exc_info=logger.level <= logging.DEBUG)
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
        The model's response as a string.
        Returns an empty string if the response is None.

    Raises:
        ConnectionError: If the API call fails due to network/connection issues.
        PredictionError: For other unexpected errors during the prediction.
    """
    logger.info(f"Querying endpoint '{api_endpoint}' with message: {message[:60]}...")
    try:
        response: Optional[str] = client.predict(
            message,
            api_name=api_endpoint
        )
        logger.debug(f"Model response: {str(response)[:100]}...")
        return str(response) if response is not None else ""

    except ConnectionError as e:
        logger.error(f"Gradio API call failed due to network issue: {e}")
        raise ConnectionError(f"Gradio API call failed due to network issue: {e}") from e
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=logger.level <= logging.DEBUG)
        raise PredictionError(f"Prediction failed: {e}") from e


# Future: add utility to test connection or get model metadata
def ping_client(client: GradioClient) -> bool:
    """
    Attempt a trivial call to verify the client is alive.

    Returns:
        True if successful, False otherwise.
    """
    try:
        client.view_api()
        logger.debug("Gradio client is responsive.")
        return True
    except Exception as e:
        logger.warning(f"Gradio client ping failed: {e}")
        return False
