import redis.asyncio as redis
from redis.asyncio import Redis

from app.cache.audio_cache import AudioAnalysisCache
from app.clients.ner_client import NERClient
from app.clients.whisper_client import WhisperClient
from app.core.config import settings


class Services:
    def __init__(self) -> None:
        self.whisper = WhisperClient()
        self.ner = NERClient()

        self.redis: Redis = redis.from_url(
            str(settings.redis_url),
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        self.audio_cache = AudioAnalysisCache(self.redis)
