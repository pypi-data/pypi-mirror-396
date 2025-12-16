"""Basic tests for html2pdfconverter client."""
import os
import tempfile
from unittest.mock import Mock, patch

import pytest
import requests

from html2pdfconverter import PdfClient


def test_client_initialization():
    """Test client initialization with required API key."""
    client = PdfClient(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.base_url == "https://api.html2pdfconverter.com"
    assert client.retry_attempts == 3
    assert client.retry_delay_ms == 1500


def test_client_initialization_without_api_key():
    """Test that missing API key raises an error."""
    with pytest.raises(ValueError, match="Missing api_key"):
        PdfClient(api_key="")


def test_client_custom_base_url():
    """Test client with custom base URL."""
    client = PdfClient(api_key="test-key", base_url="https://custom.example.com")
    assert client.base_url == "https://custom.example.com"


def test_convert_requires_input():
    """Test that convert requires html, url, or file_path."""
    client = PdfClient(api_key="test-key")
    with pytest.raises(ValueError, match="You must provide html, url, or file_path"):
        client.convert({})


@patch("html2pdfconverter.client.requests.Session")
def test_convert_with_url(mock_session_class):
    """Test convert with URL input."""
    mock_session = Mock()
    mock_session_class.return_value = mock_session
    mock_session.headers = {}

    # Mock job creation response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"jobId": "test-job-123", "status": "completed", "downloadUrl": "https://example.com/file.pdf"}
    mock_response.content = b"fake pdf content"

    # Mock download response
    mock_download = Mock()
    mock_download.status_code = 200
    mock_download.content = b"fake pdf content"

    mock_session.post.return_value = mock_response
    mock_session.get.side_effect = [mock_response, mock_download]

    client = PdfClient(api_key="test-key")
    result = client.convert({"url": "https://example.com"})

    assert result == b"fake pdf content"
    assert mock_session.post.called
    assert mock_session.get.called


def test_verify_webhook():
    """Test webhook verification."""
    client = PdfClient(api_key="test-key", webhook_secret="test-secret")
    
    import hmac
    import hashlib
    import json
    
    payload = {"jobId": "123", "status": "completed"}
    raw_body = json.dumps(payload).encode("utf-8")
    signature = "sha256=" + hmac.new(
        "test-secret".encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    
    result = client.verify_webhook(raw_body, signature)
    assert result == payload


def test_verify_webhook_invalid_signature():
    """Test webhook verification with invalid signature."""
    client = PdfClient(api_key="test-key", webhook_secret="test-secret")
    
    import json
    payload = {"jobId": "123", "status": "completed"}
    raw_body = json.dumps(payload).encode("utf-8")
    
    with pytest.raises(ValueError, match="Invalid webhook signature"):
        client.verify_webhook(raw_body, "invalid-signature")


def test_verify_webhook_missing_secret():
    """Test webhook verification without secret."""
    client = PdfClient(api_key="test-key")
    
    with pytest.raises(ValueError, match="Missing webhook_secret"):
        client.verify_webhook(b"{}", "signature")

