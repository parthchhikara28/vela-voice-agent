import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # Whisper listens at 16,000 samples per second


def record():
    """Press Enter to start, press Enter to stop. Returns the audio, or None to quit."""
    cmd = input("\nPress Enter to START talking (or type q then Enter to quit): ")
    if cmd.strip().lower() == "q":
        return None

    chunks = []

    def on_audio(indata, frames, time_info, status):
        chunks.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=on_audio):
        input("Recording... press Enter to STOP.")

    if not chunks:
        return np.zeros(0, dtype="float32")
    return np.concatenate(chunks).flatten()


def play(samples, sample_rate):
    """Start playing and return straight away. Call sd.wait() to wait until it ends."""
    sd.play(samples, sample_rate)