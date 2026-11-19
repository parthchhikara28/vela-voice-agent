import os
import tempfile
import pyttsx3
import soundfile as sf


def synthesize(text):
    """Turn written words into sound. Returns (samples, sample_rate)."""
    path = os.path.join(tempfile.gettempdir(), "vela_tts.wav")
    if os.path.exists(path):
        os.remove(path)
    engine = pyttsx3.init()          # a fresh engine each time avoids a known Windows freeze
    engine.setProperty("rate", 175)  # words per minute
    engine.save_to_file(text, path)
    engine.runAndWait()
    engine.stop()
    samples, sample_rate = sf.read(path, dtype="float32")
    return samples, sample_rate