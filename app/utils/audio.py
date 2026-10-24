import io

import av
from av.container import InputContainer


class AudioValidationError(ValueError):
    """Uploaded bytes are not a readable audio file."""


def get_audio_duration(audio_bytes: bytes) -> float:
    """Return the audio duration in seconds, without decoding the audio.

    Tries, in order: the container header, the audio stream header, then the
    sum of packet durations (some WebM files carry no duration in the header).

    Raises:
        AudioValidationError: unreadable file, no audio stream, or unknown duration.
    """
    try:
        with av.open(io.BytesIO(audio_bytes), mode="r") as container:
            # Narrows the type for the checker: reading always gives an InputContainer
            if not isinstance(container, InputContainer):
                raise AudioValidationError("Unreadable audio file")
            if not container.streams.audio:
                raise AudioValidationError("File has no audio stream")
            stream = container.streams.audio[0]

            # 1. Container header (WAV, FLAC, MP3, M4A...)
            if container.duration is not None:
                return container.duration / av.time_base

            # 2. Stream header
            if stream.duration is not None and stream.time_base is not None:
                return float(stream.duration * stream.time_base)

            # 3. Sum of packet durations (reads packets, does not decode audio)
            total = 0.0
            for packet in container.demux(stream):
                if packet.duration is not None and packet.time_base is not None:
                    total += float(packet.duration * packet.time_base)
            if total > 0:
                return total

    except av.error.FFmpegError as exc:
        raise AudioValidationError("Unreadable audio file") from exc

    raise AudioValidationError("Could not determine audio duration")
