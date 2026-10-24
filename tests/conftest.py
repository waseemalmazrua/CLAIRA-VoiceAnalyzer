import os
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
import redis as sync_redis
from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.core.config import settings
from app.main import app
from app.schemas.agent_output import ClinicalReport, Recommendation, SOAPNote
from bento_services.ner_schema import Entity, NEROutput

# ── Constants ──────────────────────────────────────────────────────
TEST_REDIS_HOST = "localhost:6380"
FAKE_USER = CurrentUser(id="test-user-id", email="test@claira.dev")
COMPOSE_FILE = Path(__file__).resolve().parent.parent / "compose.test.yml"


def _redis_is_up() -> bool:
    client = sync_redis.Redis.from_url(
        os.environ["REDIS_URL"], socket_connect_timeout=1
    )
    try:
        return bool(client.ping())
    except sync_redis.exceptions.ConnectionError:
        return False
    finally:
        client.close()


# ── Safety + auto-start test Redis (once per pytest run) ───────────
@pytest.fixture(scope="session", autouse=True)
def ensure_test_environment():
    # 1. Never run against non-test infrastructure
    if TEST_REDIS_HOST not in str(settings.redis_url):
        pytest.exit(
            f"Refusing to run: REDIS_URL is not the test Redis ({TEST_REDIS_HOST}). "
            "Is pytest-env installed?",
            returncode=1,
        )

    # 2. Already running: nothing to do
    if _redis_is_up():
        return

    # 3. In CI, Redis comes from the workflow service; never start Docker there
    if os.environ.get("CI"):
        pytest.exit("Test Redis is not reachable in CI.", returncode=1)

    # 4. Locally: start only the isolated test project
    if shutil.which("docker") is None:
        pytest.exit("Docker not found. Start Redis on localhost:6380.", returncode=1)

    subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d", "--wait"],
        check=True,
    )

    if not _redis_is_up():
        pytest.exit("Test Redis did not become ready on localhost:6380.", returncode=1)


# ── Shared clients ─────────────────────────────────────────────────
@pytest.fixture
def client():
    """Authenticated client: real auth replaced by a fake user."""
    app.dependency_overrides[get_current_user] = lambda: FAKE_USER
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def anon_client():
    """No override: real auth runs, used to test 401s."""
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
