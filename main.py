import tkinter as tk
from threading import Thread
from queue import Queue
from server import start_server
from transcription import transcribe
from display import run_gui


def main_menu():
    # Główne okno menu
    root = tk.Tk()
    root.title("Menu Główne")

    # Tworzymy zmienne do checkboxów
    server_var = tk.BooleanVar()
    gui_var = tk.BooleanVar()

    def zatwierdz_wybor():
        # Zamyka główne okno po kliknięciu Zatwierdź
        root.destroy()

        # Transkrypcja zawsze się uruchamia
        queue = Queue()
        transkrypcja_thread = Thread(target=transcribe, args=(queue,))
        transkrypcja_thread.daemon = False
        transkrypcja_thread.start()
        print("Transkrypcja została uruchomiona!")

        # Uruchamiamy serwer, jeśli zaznaczono
        if server_var.get():
            server_thread = Thread(target=start_server)
            server_thread.daemon = True
            server_thread.start()
            print("Serwer został uruchomiony!")

        # Uruchamiamy GUI, jeśli zaznaczono
        if gui_var.get():
            gui_thread = Thread(target=run_gui, args=(queue,))
            gui_thread.daemon = True
            gui_thread.start()
            print("GUI zostało uruchomione!")

    def zamknij_aplikacje():
        # Zamyka aplikację
        root.destroy()
        print("Aplikacja została zamknięta.")

    # Label na górze
    tk.Label(root, text="Wybierz opcje do uruchomienia:", font=("Arial", 14)).pack(pady=10)

    # Checkboxy
    tk.Checkbutton(root, text="Uruchom serwer", variable=server_var).pack(anchor="w", padx=20)
    tk.Checkbutton(root, text="Uruchom GUI (Okno)", variable=gui_var).pack(anchor="w", padx=20)

    # Przyciski
    tk.Button(root, text="Zatwierdź", command=zatwierdz_wybor).pack(pady=10)
    tk.Button(root, text="Zamknij aplikację", command=zamknij_aplikacje).pack(pady=10)

    # Uruchomienie pętli głównej Tkintera
    root.mainloop()


if __name__ == "__main__":
    main_menu()
