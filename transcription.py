import pyaudio
import numpy as np
import time
from faster_whisper import WhisperModel
import torch
from server import send_new_text

# Configuration
RATE = 16000
CHUNK_DURATION = 6
CHUNK = int(RATE * CHUNK_DURATION)

device = "cuda" if torch.cuda.is_available() else "cpu"
model_size = "large-v3"
print(device)
model = WhisperModel(model_size, device=device, compute_type="float16" if device == "cuda" else "int8")

audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)


def transcribe(queue):
    """Continuously record audio chunks and transcribe them."""
    segments_list = []
    print("Recording and transcribing...")
    try:
        start_time = time.time()
        segment_start_time = start_time

        while True:
            audio_data = stream.read(CHUNK)
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            segments, _ = model.transcribe(audio_np, beam_size=5, language="pl")

            for segment in segments:
                relative_segment_start = segment_start_time - start_time
                relative_segment_end = relative_segment_start + (segment.end - segment.start)

                segment_info = {
                    "start": f"{relative_segment_start:.2f}s",
                    "end": f"{relative_segment_end:.2f}s",
                    "text": segment.text
                }
                segments_list.append(segment_info)

                queue.put(segment_info)

                print(f"[{relative_segment_start:.2f}s -> {relative_segment_end:.2f}s] {segment.text}")
                segment_start_time += segment.end - segment.start
                send_new_text(segment.text)
    except KeyboardInterrupt:
        print("\nTranscription stopped.")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    return segments_list
