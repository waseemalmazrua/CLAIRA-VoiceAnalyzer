import pytest

ENDPOINT = "/analyze-audio"
AUDIO = {"file": ("visit.wav", b"fake-audio-bytes", "audio/wav")}


def test_rejects_request_without_token(anon_client):
    response = anon_client.post(ENDPOINT, files=AUDIO)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "authorization",
    [
        "Bearer not-a-real-jwt",  # malformed token
        "Basic dXNlcjpwYXNz",  # wrong scheme
        "Bearer ",  # empty token
    ],
)
def test_rejects_invalid_credentials(anon_client, authorization):
    response = anon_client.post(
        ENDPOINT,
        files=AUDIO,
        headers={"Authorization": authorization},
    )

    assert response.status_code == 401


def test_health_check_stays_public(anon_client):
    response = anon_client.get("/")

    assert response.status_code == 200
