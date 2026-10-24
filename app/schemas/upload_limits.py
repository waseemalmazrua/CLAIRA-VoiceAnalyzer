from pydantic import BaseModel


class UploadLimits(BaseModel):
    max_audio_seconds: float
    max_upload_mb: float
