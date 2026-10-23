# app/api/routes.py

from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from redis_fastapi import rate_limit

from app.agents.analyzer_agent import generate_clinical_report
from app.schemas.audio_analyzer_response import AudioAnalyzerResponse
from bento_services.ner_schema import NerRequest

router = APIRouter(tags=["Medical Analysis"])

# whisper_client = WhisperClient()
# ner_client = NERClient()


@router.post(
    "/analyze-audio",
    dependencies=[
        Depends(
            rate_limit(
                "2/second",
                scope="analyze-audio:burst",
            )
        ),
        Depends(
            rate_limit(
                "10/minute",
                scope="analyze-audio:sustained",
            )
        ),
    ],
)
async def analyze_audio(
    request: Request,
    file: Annotated[UploadFile, File()],
) -> AudioAnalyzerResponse:
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio file")

    try:
        services = request.app.state.services
        # اقرأ ملف الصوت
        audio_bytes = await file.read()

        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Invalid audio file")

        cached_response = await services.audio_cache.get(audio_bytes)

        if cached_response is not None:
            return cached_response

        # 1) Whisper ASR
        whisper_result = await services.whisper.transcribe(
            filename=file.filename,
            audio_bytes=audio_bytes,
            content_type=file.content_type,
        )

        transcript = whisper_result["transcript"]

        # 2) Medical NER
        ner_result = await services.ner.extract_entities(NerRequest(text=transcript))

        entities = ner_result.entities

        # 3) AI Agent
        report = await generate_clinical_report(
            transcript=transcript,
            entities=entities,
        )

        # 4) Final Response
        response = AudioAnalyzerResponse(
            report=report,
        )

        await services.audio_cache.set(
            audio_bytes=audio_bytes,
            response=response,
        )

        return response

    except HTTPException:
        raise

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Upstream service request failed.",
        ) from exc
