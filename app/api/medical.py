from typing import Annotated

import httpx
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from redis_fastapi import rate_limit
from starlette.concurrency import run_in_threadpool

from app.agents.analyzer_agent import generate_clinical_report
from app.core.auth import CurrentUser, get_current_user
from app.core.config import settings
from app.core.rate_limit import user_identifier
from app.schemas.audio_analyzer_response import AudioAnalyzerResponse
from app.schemas.upload_limits import UploadLimits
from app.utils.audio import AudioValidationError, get_audio_duration
from bento_services.ner_schema import NerRequest

router = APIRouter(tags=["Medical Analysis"])


@router.get("/limits")
def get_upload_limits(response: Response) -> UploadLimits:
    """Public upload limits, so the frontend can validate files before uploading."""
    response.headers["Cache-Control"] = "public, max-age=300"
    return UploadLimits(
        max_audio_seconds=settings.max_audio_seconds,
        max_upload_mb=settings.max_upload_mb,
    )


INVALID_AUDIO = "Invalid audio file"


@router.post(
    "/analyze-audio",
    dependencies=[
        # 1) Per IP: stops anonymous spam before auth runs
        Depends(rate_limit("2/second", scope="analyze-audio:burst")),
        Depends(rate_limit("10/minute", scope="analyze-audio:sustained")),
        # 2) Auth: verifies the JWT and stores the user on request.state
        Depends(get_current_user),
        # 3) Per user: protects the OpenAI / RunPod budget
        Depends(
            rate_limit(
                "5/minute",
                scope="analyze-audio:user-minute",
                identifier=user_identifier,
            )
        ),
        Depends(
            rate_limit(
                "50/day",
                scope="analyze-audio:user-day",
                identifier=user_identifier,
            )
        ),
    ],
)
async def analyze_audio(
    request: Request,
    file: Annotated[UploadFile, File()],
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> AudioAnalyzerResponse:
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail=INVALID_AUDIO)

    try:
        services = request.app.state.services

        # Size limit: read at most max + 1 bytes, never the whole upload
        max_bytes = int(settings.max_upload_mb * 1024 * 1024)
        audio_bytes = await file.read(max_bytes + 1)

        if not audio_bytes:
            raise HTTPException(status_code=400, detail=INVALID_AUDIO)

        if len(audio_bytes) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Audio file is larger than {settings.max_upload_mb:g} MB.",
            )

        # Duration limit: read from the file header, off the event loop
        try:
            duration = await run_in_threadpool(get_audio_duration, audio_bytes)
        except AudioValidationError as exc:
            raise HTTPException(status_code=400, detail=INVALID_AUDIO) from exc

        if duration > settings.max_audio_seconds:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Audio is {duration:.1f} s long; "
                    f"the limit is {settings.max_audio_seconds:g} s."
                ),
            )

        cached_response = await services.audio_cache.get(
            user_id=user.id,
            audio_bytes=audio_bytes,
        )
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

        # 3) AI agent
        report = await generate_clinical_report(
            transcript=transcript,
            entities=entities,
        )

        # 4) Final response
        response = AudioAnalyzerResponse(report=report)

        await services.audio_cache.set(
            user_id=user.id,
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
