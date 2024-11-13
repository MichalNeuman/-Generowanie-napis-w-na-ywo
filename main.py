import pyaudio
import numpy as np
import torch
from faster_whisper import WhisperModel
import time
from datetime import timedelta
import threading
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window

# Konfiguracja modelu
print(torch.version.cuda)
model_size = "medium"
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)
chunk_duration = 3

# Inicjalizacja modelu Whisper
model = WhisperModel(model_size, device=device, compute_type="float16" if device == "cuda" else "int8")

# Ustawienia audio
RATE = 16000
CHUNK = int(RATE * chunk_duration)
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Ustawienia okna Kivy
Window.clearcolor = (0, 0, 0, 0.3)  # Przezroczyste tło
Window.size = (800, 200)  # Rozmiar okna


class TranscriptionOverlay(App):
    def build(self):
        # Układ aplikacji
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Etykieta dla napisów
        self.subtitle_label = Label(
            text="Starting transcription...",
            font_size='24sp',
            color=(1, 1, 1, 0.9),  # Kolor biały, 90% nieprzezroczystości
            size_hint=(1, 0.5),
            halign="center",
            valign="middle"
        )
        self.subtitle_label.bind(size=self.subtitle_label.setter('text_size'))  # Wyśrodkowanie tekstu
        self.layout.add_widget(self.subtitle_label)

        # Uruchomienie transkrypcji w osobnym wątku
        threading.Thread(target=self.transcribe, daemon=True).start()

        return self.layout

    def transcribe(self):
        """Transkrypcja i aktualizacja napisów w aplikacji Kivy oraz zapis do pliku SRT."""
        print("Recording and transcribing...")
        segments_list = []  # Lista do przechowywania segmentów do zapisu w SRT
        start_time = time.time()
        segment_start_time = start_time

        try:
            while True:
                # Odczyt dźwięku
                audio_data = stream.read(CHUNK)
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                # Transkrypcja segmentu
                segments, info = model.transcribe(audio_np, beam_size=5)
                print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")

                # Wyświetlanie tekstu w czasie rzeczywistym i zapis segmentów
                for segment in segments:
                    text = segment.text
                    relative_start = segment_start_time - start_time
                    relative_end = relative_start + (segment.end - segment.start)

                    # Zapis segmentu do listy dla SRT
                    segment_info = {
                        "start": relative_start,
                        "end": relative_end,
                        "text": text
                    }
                    segments_list.append(segment_info)

                    # Aktualizacja napisu w aplikacji Kivy
                    Clock.schedule_once(lambda dt, text=text: self.update_subtitle(text))

                    # Przesunięcie czasu rozpoczęcia kolejnego segmentu
                    segment_start_time += segment.end - segment.start

        except KeyboardInterrupt:
            print("\nTranscription stopped.")
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
            self.saving(segments_list)  # Zapis na koniec transkrypcji

    def update_subtitle(self, text):
        """Aktualizacja tekstu w oknie Kivy."""
        self.subtitle_label.text = text

    def format_time(self, seconds):
        """Konwersja czasu do formatu SRT: HH:MM:SS,ms"""
        delta = timedelta(seconds=seconds)
        total_seconds = int(delta.total_seconds())
        milliseconds = int((delta.total_seconds() - total_seconds) * 1000)
        return f"{str(delta)[:-3]},{milliseconds:03d}"

    def saving(self, segments_list):
        """Zapis transkrypcji do pliku SRT."""
        with open("transcription.srt", "w") as file:
            for index, segment in enumerate(segments_list, start=1):
                start_time = self.format_time(segment['start'])
                end_time = self.format_time(segment['end'])
                text = segment['text']

                # Zapis w formacie SRT
                file.write(f"{index}\n")
                file.write(f"{start_time} --> {end_time}\n")
                file.write(f"{text}\n\n")


if __name__ == "__main__":
    TranscriptionOverlay().run()
