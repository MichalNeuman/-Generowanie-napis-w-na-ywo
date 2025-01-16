import tkinter as tk
from threading import Thread
from queue import Queue
import socket
import subprocess
from server import start_server
from transcription import transcribe
from display import run_gui
from utils import save_transcription

def main_menu():
    root = tk.Tk()
    root.title("Menu Główne")

    server_var = tk.BooleanVar()
    gui_var = tk.BooleanVar()
    global queue
    queue = Queue()

    server_label = tk.Label(root, text="", font=("Arial", 12), fg="green")
    server_label.pack(pady=5)
    ngrok_label = tk.Label(root, text="", font=("Arial", 12), fg="blue")
    ngrok_label.pack(pady=5)

    def copy_to_clipboard(text):
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()  # Uaktualnij schowek
        print(f"Skopiowano do schowka: {text}")

    server_label.bind("<Button-1>", lambda e: copy_to_clipboard(server_label.cget("text")))
    ngrok_label.bind("<Button-1>", lambda e: copy_to_clipboard(ngrok_label.cget("text")))

    def get_local_ip():
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip

    def start_ngrok():
        try:
            ngrok_process = subprocess.Popen(
                ["ngrok", "http", "5000"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            while True:
                output = ngrok_process.stdout.readline().decode("utf-8").strip()
                if "http://" in output or "https://" in output:
                    for line in output.split():
                        if line.startswith("http://") or line.startswith("https://"):
                            return line
        except Exception as e:
            print(f"Błąd podczas uruchamiania ngrok: {e}")
            return None

    def update_server_label():
        local_ip = get_local_ip()
        server_label.config(text=f"Lokalny serwer: http://{local_ip}:5000")

        public_url = start_ngrok()
        if public_url:
            ngrok_label.config(text=f"Publiczny adres: {public_url}")
        else:
            ngrok_label.config(text="Nie udało się uruchomić ngrok.")

    def zatwierdz_wybor():
        transkrypcja_thread = Thread(target=transcribe, args=(queue,))
        transkrypcja_thread.daemon = True
        transkrypcja_thread.start()
        print("Transkrypcja została uruchomiona!")

        if server_var.get():
            server_thread = Thread(target=start_server)
            server_thread.daemon = True
            server_thread.start()
            print("Serwer został uruchomiony!")
            update_server_label()

        if gui_var.get():
            root.destroy()
            print("Uruchamiam GUI...")
            run_gui(queue)

    def zamknij_aplikacje():
        segments_list = []
        while not queue.empty():
            segments_list.append(queue.get())

        save_transcription(segments_list, "transcription.srt")
        print("Transkrypcja zapisana do pliku transcription.srt.")
        root.destroy()
        print("Aplikacja została zamknięta.")

    tk.Label(root, text="Wybierz opcje do uruchomienia:", font=("Arial", 14)).pack(pady=10)
    tk.Checkbutton(root, text="Uruchom serwer", variable=server_var).pack(anchor="w", padx=20)
    tk.Checkbutton(root, text="Uruchom GUI (Okno)", variable=gui_var).pack(anchor="w", padx=20)
    tk.Button(root, text="Zatwierdź", command=zatwierdz_wybor).pack(pady=10)
    tk.Button(root, text="Zamknij aplikację", command=zamknij_aplikacje).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
