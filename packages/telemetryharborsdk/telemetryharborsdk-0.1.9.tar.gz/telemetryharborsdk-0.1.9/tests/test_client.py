# test_client.py
import pytest
import requests
from telemetryharborsdk import HarborClient
from telemetryharborsdk.models import GeneralReading

API_ENDPOINT = "ENDPOINT"
API_KEY = "API-KEY"

@pytest.fixture
def client():
    """Provides a HarborClient instance for testing."""
    return HarborClient(endpoint=API_ENDPOINT, api_key=API_KEY, initial_backoff=0.1)

def test_send_single_success(client, requests_mock):
    """Test successful sending of a single reading."""
    reading = GeneralReading(ship_id="test-ship", cargo_id="test-cargo", value=100)
    requests_mock.post(API_ENDPOINT, text="OK", status_code=200)
    
    response = client.send(reading)
    
    assert response.status_code == 200
    assert requests_mock.called_once
    # Check that the sent JSON matches our model's data
    sent_json = requests_mock.last_request.json()
    assert sent_json["ship_id"] == "test-ship"
    assert "time" in sent_json

def test_send_batch_success(client, requests_mock):
    """Test successful sending of a batch."""
    readings = [GeneralReading(ship_id=f"s{i}", cargo_id="c1", value=i) for i in range(3)]
    batch_url = f"{API_ENDPOINT}/batch"
    requests_mock.post(batch_url, text="Batch OK", status_code=202)

    response = client.send_batch(readings)

    assert response.status_code == 202
    assert len(requests_mock.last_request.json()) == 3

def test_retry_on_server_error(client, requests_mock):
    """Test that the client retries on 5xx errors."""
    reading = GeneralReading(ship_id="retry-ship", cargo_id="c1", value=1)
    # Mock a server error followed by a success
    matcher = requests_mock.post(API_ENDPOINT, [
        {"status_code": 503, "text": "Service Unavailable"},
        {"status_code": 200, "text": "OK"}
    ])
    
    client.send(reading)

    # The request should have been made twice (1 failure + 1 success)
    assert matcher.call_count == 2

def test_no_retry_on_client_error(client, requests_mock):
    """Test that the client does NOT retry on 4xx errors."""
    reading = GeneralReading(ship_id="bad-ship", cargo_id="c1", value=1)
    requests_mock.post(API_ENDPOINT, status_code=400, text="Bad Request")

    with pytest.raises(ValueError, match="Client error: 400"):
        client.send(reading)
    
    assert requests_mock.call_count == 1
