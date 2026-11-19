from faster_whisper import WhisperModel

_model = None


def load():
    """Load Whisper once. The first run downloads about 150 MB."""
    global _model
    if _model is None:
        _model = WhisperModel("base.en", device="cpu", compute_type="int8")
    return _model


def transcribe(audio):
    """Turn recorded audio (numbers) into written words."""
    model = load()
    segments, _ = model.transcribe(audio, language="en", beam_size=1, vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip()