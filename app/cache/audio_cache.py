import hashlib
import json
from typing import Any

from pydantic import ValidationError
from redis.asyncio import Redis

from app.schemas.audio_analyzer_response import AudioAnalyzerResponse


class AudioAnalysisCache:
    def __init__(
        self,
        redis_client: Redis,
        *,
        ttl_seconds: int = 900,
    ) -> None:
        self._redis = redis_client
        self._ttl_seconds = ttl_seconds

    @staticmethod
    def build_key(audio_bytes: bytes) -> str:
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()
        return f"medical:audio-analysis:{audio_hash}"

    async def get(
        self,
        audio_bytes: bytes,
    ) -> AudioAnalyzerResponse | None:
        key = self.build_key(audio_bytes)

        cached_value = await self._redis.get(key)

        if cached_value is None:
            return None

        try:
            raw_data: Any = json.loads(cached_value)
            return AudioAnalyzerResponse.model_validate(raw_data)

        except (json.JSONDecodeError, ValidationError):
            # الكاش تالف أو لا يطابق الـ schema الحالي
            await self._redis.delete(key)
            return None

    async def set(
        self,
        audio_bytes: bytes,
        response: AudioAnalyzerResponse,
    ) -> None:
        key = self.build_key(audio_bytes)

        serialized_response = response.model_dump_json()

        await self._redis.set(
            key,
            serialized_response,
            ex=self._ttl_seconds,
        )

    async def delete(self, audio_bytes: bytes) -> None:
        key = self.build_key(audio_bytes)
        await self._redis.delete(key)
