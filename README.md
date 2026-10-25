# CLAIRA — Clinical Language AI Reasoning Assistant

### Medical Voice Analyzer

CLAIRA turns recorded clinical speech into structured clinical documentation. A clinician uploads audio; the system transcribes it, extracts medical entities, and uses an AI reasoning agent to produce a structured clinical report.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Engineering Decisions](#engineering-decisions)
- [Privacy & Security](#privacy--security)
- [Model Serving & Performance](#model-serving--performance)
- [Quality Gates](#quality-gates)
- [API](#api)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Disclaimer](#disclaimer)

---

## How It Works

```text
  Clinician audio
        │
        ▼
┌──────────────────────┐
│ 1. Transcription      │  Whisper large-v3-turbo (Groq API)
│    speech → text      │  deterministic decoding (temperature 0)
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 2. Entity extraction  │  GLiNER Biomedical (self-hosted, GPU)
│    text → entities    │  diseases, symptoms, medications, lab tests,
└──────────┬───────────┘  dosages, frequencies, demographics
           ▼
┌──────────────────────┐
│ 3. Clinical reasoning │  Pydantic AI agent + OpenAI GPT
│    → structured report│  schema-validated output
└──────────┬───────────┘
           ▼
     Structured clinical report
```

Each stage is an independent service behind a typed client, so any stage can be replaced (for example, swapping the transcription provider) without touching the rest of the pipeline.

---

## Architecture

```text
             ┌──────────────────────────┐
             │  React Frontend          │
             │  (Firebase Hosting)      │
             └────────────┬─────────────┘
                          │ HTTPS + auth token
                          ▼
             ┌──────────────────────────┐
             │  FastAPI Backend         │
             │  (FastAPI Cloud)         │
             │  orchestration · auth ·  │
             │  validation · rate limit │
             └────────────┬─────────────┘
                          │
   ┌──────────────┬───────┴───────┬───────────────┬──────────────┐
   ▼              ▼               ▼               ▼              ▼
Redis Cloud   Supabase        Groq API        RunPod GPU      OpenAI API
cache +       Auth +          Whisper         BentoML         GPT via
rate limit    PostgreSQL      transcription   GLiNER NER      Pydantic AI
              (SQLModel)

                 Observability: Logfire distributed tracing across services
```

| Component | Runs on | Responsibility |
|-----------|---------|----------------|
| Frontend | Firebase Hosting | Audio upload, authentication, report display |
| API gateway | FastAPI Cloud | Request orchestration, validation, auth, rate limiting |
| Transcription | Groq API | Speech-to-text with Whisper large-v3-turbo |
| NER service | RunPod GPU (BentoML) | Biomedical entity extraction with GLiNER |
| Reasoning agent | OpenAI API (Pydantic AI) | Clinical reasoning and structured report generation |
| Cache & limits | Redis Cloud | Audio caching and rate limiting |
| Data & auth | Supabase | Authentication and PostgreSQL storage |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, Pydantic, httpx |
| AI orchestration | Pydantic AI, OpenAI GPT |
| Speech-to-text | Whisper large-v3-turbo via Groq |
| Medical NER | GLiNER Biomedical (`Ihor/gliner-biomed-large-v1.0`) |
| Model serving | BentoML on RunPod GPUs |
| Data | SQLModel, Supabase PostgreSQL |
| Auth | Supabase Auth |
| Caching & rate limiting | Redis Cloud |
| Observability | Logfire |
| Frontend | React, TypeScript, Vite |
| Tooling | uv, Ruff, ty, pre-commit, gitleaks, GitHub Actions |

---

## Engineering Decisions

**Priorities, in order:**

1. **Quality** — clinical output must be correct before it is fast or cheap
2. **Reliability** — failures are explicit and observable, never silent
3. **Security** — patient data is minimized at every boundary
4. **Cost** — GPU and API usage sized to the actual workload
5. **Latency** — optimized only after the above are satisfied

**Fully async I/O.** Every external call — transcription, NER, LLM, cache, database — uses an async client (`AsyncGroq`, `httpx.AsyncClient`, async Redis) and is awaited, so a slow upstream never blocks the event loop or other requests.

**Explicit resource lifecycle.** All clients are created once in the FastAPI lifespan and closed on shutdown through a uniform `aclose()` interface, avoiding leaked connections across restarts and test runs.

**Model on its own GPU service.** GLiNER runs as a separate BentoML service on RunPod rather than inside the API. The API stays lightweight and CPU-only; the GPU workload scales independently.

**Typed contracts between services.** Requests and responses are Pydantic models on both sides of every service boundary, so schema drift fails loudly instead of corrupting data downstream.

**Configuration as secrets.** API keys are typed as `SecretStr`, validated when services initialize, and never printed in logs or reprs.

---

## Privacy & Security

The system is designed around the assumption that every transcript contains Protected Health Information (PHI).

**No PHI in telemetry.** Logs and traces record metadata only — audio size, transcript length, entity counts per label, confidence statistics, latency. Transcripts, extracted entities, and filenames are never sent to the observability platform.

```python
# Logged: shape of the data, never its content
logfire.info(
    "GLiNER output completed",
    entity_count=len(entities),
    label_counts=dict(Counter(e["label"] for e in entities)),
)
```

**Secret scanning.** gitleaks runs on every commit via pre-commit; repository history is scanned clean.

**Access control.** Endpoints require authentication, and requests are rate-limited per user.

**Data minimization.** Data is sent only to services that must process it; nothing patient-related is stored where it is not required.

> Current deployment uses third-party processors (Groq, OpenAI, RunPod). It is intended for demonstration with synthetic data and is not configured for real patient data. Production use would require region-restricted infrastructure, processor agreements, and a formal compliance review (e.g. PDPL, HIPAA).

---

## Model Serving & Performance

GLiNER is served with BentoML on RunPod GPUs. Because RunPod may schedule the service on different GPU types, precision was benchmarked before choosing a default.

**Precision benchmark** — Tesla T4 (sm_75), 5 synthetic clinical notes, median of 5 trials:

| Precision | Latency / text | Model weights | Entity agreement vs FP32 |
|-----------|----------------|---------------|--------------------------|
| FP32 | 54.4 ms | 1.79 GB | baseline |
| **FP16** | **50.7 ms** | **0.90 GB** | **100% (53/53)** |
| BF16 | 69.7 ms | 0.90 GB | 100% (53/53) |

**Findings**

- **FP16 halves GPU memory with no change in extracted entities** on the test set.
- **BF16 is slower than FP32 on T4**: Turing GPUs have no BF16 tensor cores, so it runs emulated. BF16 only pays off on Ampere (sm_80) and newer.
- **Latency gains are small for short notes.** Profiling showed roughly half of per-request time is Python pre/post-processing (tokenization, span decoding), not GPU compute. Batching is the larger lever for throughput.

---

## Quality Gates

Every change passes the same checks locally and in CI.

| Check | Tool | Pre-commit | CI |
|-------|------|:----------:|:--:|
| Secret detection | gitleaks | ✓ | |
| Lint | Ruff | ✓ (auto-fix) | ✓ |
| Formatting | Ruff | ✓ (auto-fix) | ✓ (check) |
| Type checking | ty | ✓ | ✓ |
| Private keys, large files, merge markers, YAML/TOML validity | pre-commit-hooks | ✓ | |

Pre-commit fixes issues before they are committed; CI verifies and blocks anything that slipped through. Both use the same tool versions from the project lockfile.

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/medical/analyze-audio` | Analyze a clinical audio recording |
| `GET` | `/health` | Health check |

**Example response**

```json
{
  "report": {
    "clinical_summary": "...",
    "assessment": "...",
    "plan": "...",
    "medical_entities": {
      "diseases": [],
      "symptoms": [],
      "medications": [],
      "laboratory_tests": []
    }
  }
}
```

---

## Known Limitations

- **English only.** Transcription and entity extraction are configured for English.
- **NER errors on context-dependent entities.** Observed cases include lab values classified as dosages and diseases classified as symptoms. Most errors carry lower confidence scores, which makes them candidates for review flagging.
- **No formal evaluation set yet.** Entity quality has been assessed on a small set of synthetic notes, not with precision/recall on a labeled dataset.
- **Long transcripts.** GLiNER has a maximum input length; very long recordings require chunking, which is not yet implemented.
- **Not for real patient data** in the current deployment (see [Privacy & Security](#privacy--security)).

---

## Roadmap

**Completed**

- [x] FastAPI backend with async service clients
- [x] Speech-to-text via Whisper (Groq API)
- [x] Biomedical NER with GLiNER on GPU (BentoML + RunPod)
- [x] Pydantic AI agent with structured outputs
- [x] Authentication and PostgreSQL (Supabase)
- [x] Redis caching and rate limiting
- [x] React frontend
- [x] Distributed tracing with PHI-safe logging
- [x] Pre-commit and CI quality gates

**Next**

- [ ] Labeled evaluation set with per-label precision / recall
- [ ] Transcript chunking with batched NER inference
- [ ] Confidence-based review flags in the UI
- [ ] Medical terminology correction layer after transcription
- [ ] Self-hosted Faster-Whisper on GPU
- [ ] Real-time WebSocket transcription
- [ ] Streaming AI responses
- [ ] Multi-language support

---

## Disclaimer

CLAIRA is intended for clinical assistance, research, and educational purposes only. All AI-generated output must be reviewed and validated by a qualified healthcare professional before any clinical use.

---

## Author

**Waseem Almazrua**
