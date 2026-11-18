import numpy, pydantic, yaml, httpx, rich
import fastapi, uvicorn, websockets, sounddevice, soundfile, jiwer
import sentence_transformers, chromadb
import faster_whisper, silero_vad

print("All bricks installed. Vela's workshop is ready!")
print("Microphones found:")
print(sounddevice.query_devices())