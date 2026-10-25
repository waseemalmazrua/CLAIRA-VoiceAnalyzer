# CLAIRA — Clinical Language AI Reasoning Assistant

## Medical Voice Analyzer

AI-powered clinical voice analysis system that transforms clinician speech into structured clinical intelligence.

---

## Overview

CLAIRA Voice analyzes clinical audio and automatically generates structured medical documentation using a modular AI pipeline.

The current version supports audio upload via HTTP and performs:

- Speech-to-text transcription
- Medical entity extraction
- AI-powered clinical reasoning
- Structured clinical report generation

Designed with a strong focus on:

- Quality
- Reliability
- Security
- Healthcare AI best practices

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | API gateway and request orchestration |
| **Pydantic AI** | AI agent orchestration and structured outputs |
| **OpenAI GPT** | Clinical reasoning and report generation |
| **Faster-Whisper**(for Now is groq Whisper API)| Speech-to-text transcription |
| **GLiNER Biomedical** | Medical entity recognition (NER) |
| **SQLModel** | ORM and database models |
| **Supabase Auth** | Authentication |
| **Supabase PostgreSQL** | Relational database |
| **Redis Cloud** | Audio caching and rate limiting |
| **BentoML** | AI model serving |
| **RunPod** | GPU inference infrastructure |
| **FastAPI Cloud** | Backend deployment |
| **httpx** | Internal service communication |
| **Logfire** | Observability, monitoring, and tracing |

---

## System Architecture

```text
                  Doctor Audio
                        │
                        ▼
             Faster-Whisper Service
             (Speech → Transcript)
                        │
                        ▼
             Medical Correction Layer (later)
                        │
                        ▼
          GLiNER Biomedical NER Service
                        │
                        ▼
        Pydantic AI + OpenAI GPT-5.2
      (Clinical reasoning & report)
                        │
                        ▼
               FastAPI API Gateway
                        │
                        ▼
              React Frontend Dashboard
```

---

## Infrastructure

```text
                    React Frontend
                           │
                           ▼
                    FastAPI Cloud
                           │
                           ▼
                     FastAPI Backend
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   Redis Cloud      Supabase PostgreSQL   AI Services
(Cache & Rate Limit)     SQLModel         BentoML + RunPod
                                                │
                                                ▼
                                     Whisper + GLiNER + GPT
```

---

## AI Pipeline

```text
Doctor Voice
      │
      ▼
Speech-to-Text (Whisper)
      │
      ▼
Medical Entity Recognition
      │
      ▼
Clinical Reasoning Agent
      │
      ▼
Structured Clinical Report
```

---

## Current Features

- Audio upload
- Speech-to-text transcription
- Medical entity extraction
- Structured clinical report generation
- Clinical reasoning
- Audio caching
- Rate limiting
- Authentication
- API-first architecture
- Docker deployment
- Cloud GPU inference
- Distributed tracing & observability

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/medical/analyze-audio` | Analyze medical audio |
| `GET` | `/health` | Health check |

---

## Example Output

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

## Engineering Priorities

The architecture follows the following engineering priorities:

```
Quality
      ↓
Reliability
      ↓
Security
      ↓
Cost
      ↓
Latency
```

The system is designed with healthcare data in mind, following security best practices for handling **PHI (Protected Health Information)** and **PII (Personally Identifiable Information)** while keeping future HIPAA-oriented deployments in consideration.

---

## Roadmap

- [x] Faster-Whisper integration
- [x] Medical NER pipeline
- [x] Pydantic AI structured outputs
- [x] FastAPI backend
- [x] BentoML model serving
- [x] Redis caching
- [x] Rate limiting
- [x] Authentication
- [x] React frontend
- [x] Docker deployment
- [x] Cloud GPU deployment
- [ ] Real-time WebSocket transcription
- [ ] Streaming AI responses
- [ ] Multi-language support
- [ ] Multi-model inference
- [ ] Clinical decision support

---

## Future Vision

CLAIRA Voice is the first project under the **CLAIRA (Clinical Language AI Reasoning Assistant)** ecosystem.

Future releases will expand beyond voice analysis into additional AI-powered clinical workflows while maintaining a modular microservice architecture.

---

## Disclaimer

CLAIRA is intended for clinical assistance, research, and educational purposes only.

AI-generated outputs must always be reviewed and validated by qualified healthcare professionals before clinical use.

---

## Author

**Waseem Almazrua**
