# client.py
import requests
import time
import logging
from typing import List, Optional

from .models import HarborPayload # Import the Pydantic models

# Configure logging (same as before)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HarborClient:
    """
    Production-ready Python SDK for interacting with Telemetry Harbor.
    It is designed to be extensible with Pydantic models.
    """
    def __init__(self, endpoint: str, api_key: str, max_retries: int = 5, initial_backoff: float = 1.0):
        if not endpoint or not api_key:
            raise ValueError("Endpoint and API Key cannot be empty.")

        self._endpoint = endpoint.rstrip('/')
        self._api_key = api_key
        self._max_retries = max_retries
        self._initial_backoff = initial_backoff
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-Key": f"{self._api_key}",
            "Content-Type": "application/json"
        })
        logger.info(f"HarborClient initialized for endpoint: {self._endpoint}")

    def _send_request(self, url: str, json_data) -> requests.Response:
        """Sends an HTTP POST request with exponential backoff retry logic."""
        retries = 0
        while retries <= self._max_retries:
            try:
                logger.debug(f"Attempt {retries + 1}/{self._max_retries + 1} to send data to {url}")
                response = self._session.post(url, json=json_data, timeout=10)
                response.raise_for_status()
                logger.info(f"Data successfully sent to {url}. Status: {response.status_code}")
                return response
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error on attempt {retries + 1}: {e.response.status_code} - {e.response.text}")
                # Don't retry on 4xx client errors (except 429 Too Many Requests)
                if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    raise ValueError(f"Client error: {e.response.status_code} - {e.response.text}") from e
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                logger.error(f"Network error on attempt {retries + 1}: {e}")

            if retries < self._max_retries:
                sleep_time = self._initial_backoff * (2 ** retries)
                logger.warning(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            retries += 1
        
        raise requests.exceptions.RequestException(f"Failed to send data to {url} after {self._max_retries + 1} attempts.")

    def send(self, reading: HarborPayload) -> requests.Response:
        """
        Sends a single telemetry reading to the ingestion endpoint.

        Args:
            reading (HarborPayload): A Pydantic model instance (e.g., GeneralReading).

        Returns:
            requests.Response: The response object from the request.
        """
        logger.info(f"Sending single {type(reading).__name__} to {self._endpoint}")
        # Convert the Pydantic model to a JSON-serializable dictionary
        payload_dict = reading.model_dump(mode="json")
        return self._send_request(self._endpoint, payload_dict)

    def send_batch(self, readings: List[HarborPayload]) -> Optional[requests.Response]:
        """
        Sends multiple telemetry readings as a batch.

        Args:
            readings (List[HarborPayload]): A list of Pydantic model instances.

        Returns:
            Optional[requests.Response]: The response object, or None if the batch was empty.
        """
        if not readings:
            logger.warning("Attempted to send an empty batch. No request will be made.")
            return None

        batch_endpoint = f"{self._endpoint}/batch"
        # Convert all Pydantic models in the list to dictionaries
        processed_batch = [r.model_dump(mode="json") for r in readings]

        logger.info(f"Sending batch of {len(processed_batch)} readings to {batch_endpoint}")
        return self._send_request(batch_endpoint, processed_batch)
