import pytest
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from collections import defaultdict, deque
from app.core.config import get_settings

settings = get_settings()
_request_buckets: dict[str, deque[datetime]] = defaultdict(deque)

# Rate limiter dependency
def enforce_rate_limit(request: Request):
    key = request.client.host if request.client else "unknown"
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=1)
    bucket = _request_buckets[key]

    while bucket and bucket[0] < window_start:
        bucket.popleft()

    if len(bucket) >= settings.rate_limit_per_minute:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    bucket.append(now)


# Minimal test app
app = FastAPI()

@app.get("/test")
def test_endpoint(request: Request, _: None = Depends(enforce_rate_limit)):
    return {"message": "success"}


@pytest.mark.anyio
async def test_rate_limiter_blocks_excess_requests():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Send up to the limit
        for _ in range(settings.rate_limit_per_minute):
            response = await client.get("/test")
            assert response.status_code == 200
            assert response.json() == {"message": "success"}

        # The next request should be blocked
        response = await client.get("/test")
        assert response.status_code == 429
        assert response.json()["detail"] == "Rate limit exceeded"


@pytest.mark.anyio
async def test_rate_limiter_resets_after_window():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Clear bucket first
        _request_buckets.clear()

        # Exceed limit once
        for _ in range(settings.rate_limit_per_minute):
            await client.get("/test")

        response = await client.get("/test")
        assert response.status_code == 429

        # Manually adjust timestamps to simulate window passed
        now = datetime.now(timezone.utc)
        for key in _request_buckets:
            _request_buckets[key] = deque([now - timedelta(minutes=2)] * settings.rate_limit_per_minute)

        # Now requests should succeed again
        response = await client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "success"}