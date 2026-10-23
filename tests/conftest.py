import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
import redis as sync_redis
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.schemas.agent_output import ClinicalReport, Recommendation, SOAPNote
from bento_services.ner_schema import Entity, NEROutput

TEST_REDIS_HOST = "localhost:6380"


# ── Safety: never run against non-test infrastructure ──────────────
@pytest.fixture(scope="session", autouse=True)
def ensure_test_environment():
    if TEST_REDIS_HOST not in str(settings.redis_url):
        pytest.exit(
            f"Refusing to run: REDIS_URL is not the test Redis ({TEST_REDIS_HOST}). "
            "Is pytest-env installed?",
            returncode=1,
        )


# ── Shared client for all integration tests ────────────────────────
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ── Clean test Redis before every test ─────────────────────────────
@pytest.fixture(autouse=True)
def clean_redis():
    r = sync_redis.Redis.from_url(os.environ["REDIS_URL"])
    r.flushdb()
    yield
    r.close()


# ── Fake data and mocks ────────────────────────────────────────────
@pytest.fixture
def fake_report() -> ClinicalReport:
    return ClinicalReport(
        chief_complaint="Fever and cough",
        clinical_summary="Patient reports fever and cough for 3 days.",
        key_findings=["Fever", "Cough"],
        possible_risks=["Lower respiratory tract infection"],
        soap_note=SOAPNote(
            subjective="Fever and cough for 3 days.",
            objective="Not documented.",
            assessment="Likely viral upper respiratory infection.",
            plan="Supportive care, reassess if worsening.",
        ),
        recommendations=[
            Recommendation(
                title="Hydration",
                rationale="Fever increases fluid loss.",
                urgency="low",
            ),
        ],
        disclaimer="For clinical decision support only.",
    )


@pytest.fixture
def mock_services(client, monkeypatch, fake_report):
    transcript = "Patient reports fever and cough for 3 days"
    entities = [Entity(text="fever", label="SYMPTOM", score=0.98)]

    whisper = AsyncMock(return_value={"transcript": transcript})
    ner = AsyncMock(return_value=NEROutput(entities=entities))
    report = AsyncMock(return_value=fake_report)

    services = app.state.services
    monkeypatch.setattr(services.whisper, "transcribe", whisper)
    monkeypatch.setattr(services.ner, "extract_entities", ner)
    monkeypatch.setattr("app.api.medical.generate_clinical_report", report)

    return SimpleNamespace(
        whisper=whisper,
        ner=ner,
        report=report,
        transcript=transcript,
        entities=entities,
    )
