import httpx

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


AUDIO = {"file": ("visit.wav", b"fake-audio-bytes", "audio/wav")}


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
