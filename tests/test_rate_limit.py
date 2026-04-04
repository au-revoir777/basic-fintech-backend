# tests/test_rate_limit.py
import pytest
from collections import deque
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request

from app.core.config import get_settings
from app.core.rate_limit import _request_buckets, enforce_rate_limit

class DummyClient:
    def __init__(self, host: str):
        self.host = host

class DummyRequest:
    def __init__(self, host: str | None):
        self.client = DummyClient(host) if host else None

@pytest.fixture(autouse=True)
def clear_buckets():
    """Clear the request buckets before each test to avoid cross-test contamination."""
    _request_buckets.clear()
    yield
    _request_buckets.clear()

def test_rate_limit_allows_under_limit():
    settings = get_settings()
    request = DummyRequest("127.0.0.1")

    # Make requests less than the limit
    for _ in range(settings.rate_limit_per_minute):
        enforce_rate_limit(request)

    # The bucket should have exactly rate_limit_per_minute entries
    key = request.client.host
    assert len(_request_buckets[key]) == settings.rate_limit_per_minute

def test_rate_limit_blocks_over_limit():
    settings = get_settings()
    request = DummyRequest("127.0.0.1")

    # Fill up to the limit
    for _ in range(settings.rate_limit_per_minute):
        enforce_rate_limit(request)

    # Next request should raise HTTP 429
    with pytest.raises(HTTPException) as exc:
        enforce_rate_limit(request)
    assert exc.value.status_code == 429
    assert exc.value.detail == "Rate limit exceeded"

def test_rate_limit_clears_old_requests(monkeypatch):
    settings = get_settings()
    request = DummyRequest("127.0.0.1")

    now = datetime.now(timezone.utc)
    old_time = now - timedelta(minutes=2)

    # Pre-fill bucket with old timestamps
    key = request.client.host
    _request_buckets[key] = deque([old_time] * settings.rate_limit_per_minute)

    # Patch datetime to control "now"
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return now

    monkeypatch.setattr("app.core.rate_limit.datetime", FixedDatetime)

    # Should allow new request after old ones are cleared
    enforce_rate_limit(request)
    assert len(_request_buckets[key]) == 1
    assert _request_buckets[key][0] == now

def test_rate_limit_unknown_client_allows_request():
    request = DummyRequest(None)  # No client info

    # First request should work
    enforce_rate_limit(request)
    key = "unknown"
    assert len(_request_buckets[key]) == 1

def test_multiple_clients_isolated_buckets():
    settings = get_settings()
    request1 = DummyRequest("127.0.0.1")
    request2 = DummyRequest("192.168.0.1")

    # Fill each bucket partially
    for _ in range(settings.rate_limit_per_minute // 2):
        enforce_rate_limit(request1)
        enforce_rate_limit(request2)

    key1 = request1.client.host
    key2 = request2.client.host
    assert len(_request_buckets[key1]) == settings.rate_limit_per_minute // 2
    assert len(_request_buckets[key2]) == settings.rate_limit_per_minute // 2