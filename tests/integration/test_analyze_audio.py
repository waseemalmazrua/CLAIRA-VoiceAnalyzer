import httpx

from app.core.config import settings
from tests.helpers import make_wav

ENDPOINT = "/analyze-audio"


def test_rejects_non_audio_file(client):
    files = {"file": ("notes.txt", b"hello", "text/plain")}

    response = client.post(ENDPOINT, files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid audio file"


def test_rejects_empty_audio_file(client):
    files = {"file": ("empty.wav", b"", "audio/wav")}

    response = client.post(ENDPOINT, files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid audio file"


AUDIO = {"file": ("visit.wav", make_wav(2), "audio/wav")}


def test_happy_path_returns_report(client, mock_services, fake_report):
    response = client.post(ENDPOINT, files=AUDIO)

    assert response.status_code == 200
    assert response.json()["report"] == fake_report.model_dump(mode="json")

    # the pipeline is wired correctly: transcript → NER → agent
    mock_services.whisper.assert_awaited_once()
    mock_services.ner.assert_awaited_once()
    mock_services.report.assert_awaited_once_with(
        transcript=mock_services.transcript,
        entities=mock_services.entities,
    )


def test_identical_audio_is_served_from_cache(client, mock_services):
    first = client.post(ENDPOINT, files=AUDIO)
    second = client.post(ENDPOINT, files=AUDIO)

    assert first.status_code == second.status_code == 200
    assert second.json() == first.json()
    mock_services.whisper.assert_awaited_once()  # second call never reached Whisper


def test_returns_502_when_whisper_fails(client, mock_services):
    mock_services.whisper.side_effect = httpx.ConnectError("whisper down")

    response = client.post(ENDPOINT, files=AUDIO)

    assert response.status_code == 502
    assert response.json()["detail"] == "Upstream service request failed."
    mock_services.report.assert_not_awaited()  # OpenAI never called


def test_rejects_audio_longer_than_limit(client, mock_services):
    files = {"file": ("long.wav", make_wav(25), "audio/wav")}

    response = client.post(ENDPOINT, files=files)

    assert response.status_code == 400
    assert f"limit is {settings.max_audio_seconds:g} s" in response.json()["detail"]
    mock_services.whisper.assert_not_awaited()  # rejected before any paid call


def test_accepts_audio_exactly_at_limit(client, mock_services):
    seconds = settings.max_audio_seconds
    files = {"file": ("edge.wav", make_wav(seconds), "audio/wav")}

    response = client.post(ENDPOINT, files=files)

    assert response.status_code == 200


def test_rejects_unreadable_audio(client, mock_services):
    files = {"file": ("fake.wav", b"not really audio", "audio/wav")}

    response = client.post(ENDPOINT, files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid audio file"
    mock_services.whisper.assert_not_awaited()


def test_rejects_file_over_size_limit(client, mock_services, monkeypatch):
    monkeypatch.setattr(settings, "max_upload_mb", 0.01)  # ~10 KB for this test only
    files = {"file": ("big.wav", make_wav(2), "audio/wav")}  # ~64 KB

    response = client.post(ENDPOINT, files=files)

    assert response.status_code == 413
    mock_services.whisper.assert_not_awaited()
