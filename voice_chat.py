import uuid
import sounddevice as sd
from vela import audio_io
from vela.providers import stt, tts
from vela.telemetry import TurnTrace
from vela.agent.agent import respond

call_id = uuid.uuid4().hex[:8]
history = []

print("Loading the ears (first time downloads a model, please wait)...")
stt.load()
print("Ready. You talk, Vela answers out loud.")

while True:
    audio = audio_io.record()
    if audio is None:
        break
    if len(audio) < audio_io.SAMPLE_RATE * 0.4:
        print("That was too short. Try again.")
        continue

    trace = TurnTrace(call_id=call_id)
    trace.mark("audio_end")                      # stopwatch starts when you stop talking

    text = stt.transcribe(audio)
    trace.mark("stt_done")
    if not text:
        print("I couldn't hear any words. Try again, a bit closer to the mic.")
        continue
    print(f"\nYou said: {text}")

    reply = respond(history, text, trace)        # also marks "llm_done"
    print(f"Vela:     {reply}")

    samples, rate = tts.synthesize(reply)
    trace.mark("tts_done")

    trace.mark("audio_start")                    # the moment you can hear Vela
    audio_io.play(samples, rate)
    trace.emit()

    m = trace.marks
    print("\n  --- how long each part took ---")
    print(f"  ears (speech to words): {m['stt_done'] - m['audio_end']:.2f}s")
    print(f"  brain (thinking):       {m['llm_done'] - m['stt_done']:.2f}s")
    print(f"  mouth (make the voice): {m['tts_done'] - m['llm_done']:.2f}s")
    print(f"  TOTAL silence you felt: {m['audio_start'] - m['audio_end']:.2f}s")
    print(f"  tools used: {[t['name'] for t in trace.tool_calls]}")

    sd.wait()                                    # wait until Vela finishes talking