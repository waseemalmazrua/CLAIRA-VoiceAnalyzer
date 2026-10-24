import os
import time

import redis as sync_redis
from fastapi import Request

from app.core.auth import CurrentUser, get_current_user
from app.main import app
from tests.helpers import make_wav

ENDPOINT = "/analyze-audio"
AUDIO = {"file": ("visit.wav", make_wav(2), "audio/wav")}
IP_BURST_SAFE_DELAY = 0.6  # seconds; keeps us under the per-IP limit of 2/second


def _login_as(user_id: str) -> None:
    """Switch the fake authenticated user for the next requests."""
    user = CurrentUser(id=user_id)

    def _override(request: Request) -> CurrentUser:
        request.state.user = user
        return user

    app.dependency_overrides[get_current_user] = _override


def test_each_user_gets_own_counter(client, mock_services):
    _login_as("alice")
    assert client.post(ENDPOINT, files=AUDIO).status_code == 200

    _login_as("bob")
    assert client.post(ENDPOINT, files=AUDIO).status_code == 200

    r = sync_redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    keys = set(r.scan_iter("*user-minute*"))
    r.close()

    assert any(k.endswith("user:alice") for k in keys)
    assert any(k.endswith("user:bob") for k in keys)


def test_user_is_limited_to_5_per_minute(client, mock_services):
    _login_as("alice")
    codes = []
    for _ in range(6):
        codes.append(client.post(ENDPOINT, files=AUDIO).status_code)
        time.sleep(IP_BURST_SAFE_DELAY)

    assert codes == [200, 200, 200, 200, 200, 429]

    # Same IP, different user: still allowed, so the 429 came from the per-user limit
    _login_as("bob")
    assert client.post(ENDPOINT, files=AUDIO).status_code == 200
