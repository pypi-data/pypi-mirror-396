from unittest.mock import MagicMock, patch

import pytest

from agent_memory_hub.client.memory_client import MemoryClient
from agent_memory_hub.config.regions import REGION_US_CENTRAL1


@pytest.fixture
def mock_storage():
    with patch("google.cloud.storage.Client") as mock_client:
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        yield mock_blob

def test_memory_client_init():
    client = MemoryClient("agent1", "sess1", REGION_US_CENTRAL1)
    assert client.agent_id == "agent1"
    assert client.region == REGION_US_CENTRAL1

def test_memory_write_flow(mock_storage):
    client = MemoryClient("agent1", "sess1", REGION_US_CENTRAL1)
    client.write("test_value", "key1")
    
    # Verify the mock interactions
    mock_storage.upload_from_string.assert_called_once()
    args, kwargs = mock_storage.upload_from_string.call_args
    assert '"value": "test_value"' in args[0]

def test_memory_recall_flow(mock_storage):
    mock_storage.exists.return_value = True
    mock_storage.download_as_text.return_value = '{"value": "returned_value"}'
    
    client = MemoryClient("agent1", "sess1", REGION_US_CENTRAL1)
    val = client.recall("key1")
    
    assert val == "returned_value"

def test_invalid_region():
    with pytest.raises(ValueError, match="Region 'invalid-region' is not supported"):
        MemoryClient("agent1", "sess1", "invalid-region")
