import pyaudio
import wave
import numpy as np
import torch
from faster_whisper import WhisperModel
import time
from datetime import timedelta
from queue import Queue
import threading
from display import run_gui

print(torch.version.cuda)  # Configuration
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

# Tworzymy kolejkę do przekazywania danych do GUI
queue = Queue()

def transcribe():
    segments_list = []  # List to store each segment's start, end, and transcription text
    print("Recording and transcribing...")
    try:
        start_time = time.time()
        segment_start_time = start_time

        while True:
            # Record audio chunk
            audio_data = stream.read(CHUNK)
            # Convert audio data to NumPy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Transcribe chunk
            segments, _ = model.transcribe(audio_np, beam_size=5, language="pl")

            # Calculate time elapsed for each segment
            for segment in segments:
                # Calculate segment start and end times
                relative_segment_start = segment_start_time - start_time
                relative_segment_end = relative_segment_start + (segment.end - segment.start)

                # Append each segment's transcription with timing to the list
                segment_info = {
                    "start": f"{relative_segment_start:.2f}s",
                    "end": f"{relative_segment_end:.2f}s",
                    "text": segment.text
                }
                segments_list.append(segment_info)

                # Przekazujemy segment do GUI poprzez kolejkę
                queue.put(segment_info)

                # Print and update the segment_start_time for the next segment
                print(f"[{relative_segment_start:.2f}s -> {relative_segment_end:.2f}s] {segment.text}")
                segment_start_time += segment.end - segment.start

    except KeyboardInterrupt:
        print("\nTranscription stopped.")

    finally:
        # Clean up
        stream.stop_stream()
        stream.close()
        audio.terminate()

    return segments_list  # Return the list of segments for saving

def format_time(seconds):
    """Convert seconds to SRT time format HH:MM:SS,ms"""
    delta = timedelta(seconds=seconds)
    total_seconds = int(delta.total_seconds())
    milliseconds = int((delta.total_seconds() - total_seconds) * 1000)
    return f"{str(delta)[:-3]},{milliseconds:03d}"

def saving(segments_list):
    with open("transcription.srt", "w") as file:
        for index, segment in enumerate(segments_list, start=1):
            start_time = format_time(float(segment['start'][:-1]))  # Convert start time to SRT format
            end_time = format_time(float(segment['end'][:-1]))  # Convert end time to SRT format
            text = segment['text']

            # Write in SRT format
            file.write(f"{index}\n")
            file.write(f"{start_time} --> {end_time}\n")
            file.write(f"{text}\n\n")

# Uruchamiamy GUI w osobnym wątku
gui_thread = threading.Thread(target=run_gui, args=(queue,))
gui_thread.start()

# Wykonujemy transkrypcję i zapisujemy wyniki
segments_data = transcribe()
saving(segments_data)