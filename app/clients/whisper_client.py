# app/clients/whisper_client.py

import logfire
from groq import AsyncGroq

from app.core.config import settings


class WhisperClient:
    def __init__(self) -> None:
        if (
            settings.groq_api_key is None
            or not settings.groq_api_key.get_secret_value()
        ):
            raise ValueError("GROQ_API_KEY is not configured")

        self.client = AsyncGroq(api_key=settings.groq_api_key.get_secret_value())

    async def aclose(self) -> None:
        await self.client.close()

    async def transcribe(
        self,
        filename: str,
        audio_bytes: bytes,
        content_type: str,
    ) -> dict:
        # PHI policy: never log transcript content or filenames — metadata only.
        with logfire.span(
            "Whisper transcription",
            audio_size_bytes=len(audio_bytes),
            content_type=content_type,
        ):
            transcription = await self.client.audio.transcriptions.create(
                file=(filename, audio_bytes, content_type),
                model="whisper-large-v3-turbo",
                temperature=0,
                language="en",
            )

            transcript = transcription.text

            logfire.info(
                "Transcription completed",
                transcript_chars=len(transcript),
                transcript_words=len(transcript.split()),
            )

            return {"transcript": transcript}
