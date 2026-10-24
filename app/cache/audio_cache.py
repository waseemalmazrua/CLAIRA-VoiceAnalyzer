import hashlib
import json
from typing import Any

from pydantic import ValidationError
from redis.asyncio import Redis

from app.schemas.audio_analyzer_response import AudioAnalyzerResponse


class AudioAnalysisCache:
    """Per-user cache of analysis results, keyed by user id + audio fingerprint.

    Results are never shared across users, even for identical audio.
    """

    def __init__(
        self,
        redis_client: Redis,
        *,
        ttl_seconds: int = 900,
    ) -> None:
        self._redis = redis_client
        self._ttl_seconds = ttl_seconds

    @staticmethod
    def build_key(user_id: str, audio_bytes: bytes) -> str:
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()
        return f"medical:audio-analysis:{user_id}:{audio_hash}"

    async def get(
        self,
        *,
        user_id: str,
        audio_bytes: bytes,
    ) -> AudioAnalyzerResponse | None:
        key = self.build_key(user_id, audio_bytes)

        cached_value = await self._redis.get(key)

        if cached_value is None:
            return None

        try:
            raw_data: Any = json.loads(cached_value)
            return AudioAnalyzerResponse.model_validate(raw_data)

        except (json.JSONDecodeError, ValidationError):
            # Corrupted entry or an old schema: drop it and recompute
            await self._redis.delete(key)
            return None

    async def set(
        self,
        *,
        user_id: str,
        audio_bytes: bytes,
        response: AudioAnalyzerResponse,
    ) -> None:
        key = self.build_key(user_id, audio_bytes)

        await self._redis.set(
            key,
            response.model_dump_json(),
            ex=self._ttl_seconds,
        )

    async def delete(self, *, user_id: str, audio_bytes: bytes) -> None:
        key = self.build_key(user_id, audio_bytes)
        await self._redis.delete(key)
