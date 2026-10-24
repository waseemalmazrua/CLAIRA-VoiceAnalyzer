from app.core.config import settings


def test_limits_are_public_and_match_settings(anon_client):
    response = anon_client.get("/limits")

    assert response.status_code == 200
    assert response.json() == {
        "max_audio_seconds": settings.max_audio_seconds,
        "max_upload_mb": settings.max_upload_mb,
    }
    assert "max-age=300" in response.headers["cache-control"]
