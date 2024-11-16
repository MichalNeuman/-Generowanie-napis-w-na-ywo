from transcription import transcribe
from utils import save_transcription
from queue import Queue
from threading import Thread
from display import run_gui
from server import start_server

if __name__ == "__main__":
    # Tworzymy kolejkę do komunikacji z GUI
    queue = Queue()

    # Uruchamiamy GUI w osobnym wątku
    gui_thread = Thread(target=run_gui, args=(queue,))
    gui_thread.start()

    server_thread = Thread(target=start_server)
    server_thread.daemon = True  # Daemon pozwala zakończyć serwer przy zamknięciu aplikacji
    server_thread.start()

    # Uruchamiamy transkrypcję
    try:
        # Funkcja `transcribe` przetwarza dźwięk i wysyła dane do kolejki
        segments_data = transcribe(queue)

        # Zapisujemy wynik w pliku SRT
        save_transcription(segments_data, "transcription.srt")
    except KeyboardInterrupt:
        print("\nProgram zakończony.")
