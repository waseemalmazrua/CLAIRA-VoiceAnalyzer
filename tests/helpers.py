import io
import wave


def make_wav(seconds: float, sample_rate: int = 16000) -> bytes:
    """Silent mono 16-bit WAV of the given length, built in memory."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(b"\x00\x00" * int(sample_rate * seconds))
    return buf.getvalue()
