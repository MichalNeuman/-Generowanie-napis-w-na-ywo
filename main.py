import pyaudio
import wave
import numpy as np
import torch
from faster_whisper import WhisperModel
import time
print(torch.version.cuda)# Configuration
model_size = "medium"  # Choose model size like "base", "small", "medium", or "large-v2"

device = "cuda" if torch.cuda.is_available() else "cpu"  # Set to "cpu" or "cuda" for GPU
print(device)
chunk_duration = 3  # Duration (in seconds) of audio chunks to transcribe

# Initialize Whisper model
model = WhisperModel(model_size, device=device, compute_type="float16" if device == "cuda" else "int8")

# Audio stream setup
RATE = 16000  # Sampling rate for Whisper compatibility
CHUNK = int(RATE * chunk_duration)  # Number of frames per buffer

audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

def transribe():
    global wa
    wa = ''
    print("Recording and transcribing...")
    try:
        timeout = 10
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Record audio chunk
            audio_data = stream.read(CHUNK)
            # Convert audio data to NumPy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Transcribe chunk
            segments, info = model.transcribe(audio_np, beam_size=5)
            print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")

            # Print transcription for each segment
            for segment in segments:
                wa += segment.text + ' '
                print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")


    except KeyboardInterrupt:
        print("\nTranscription stopped.")

    finally:
        # Clean up
        stream.stop_stream()
        stream.close()
        audio.terminate()

def saving(string):
    with open("transcription.txt", "w") as file:
        file.write(string)
transribe()
saving(wa)

