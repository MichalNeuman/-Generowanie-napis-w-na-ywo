from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tkinter import Tk, END, ttk
from queue import Queue

class TranscriptionApp:
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.root.title("Transkrypcja")

        # Konfiguracja stylu ttkbootstrap
        style = Style(theme="darkly")

        # Pobieramy wymiary ekranu
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Ustawiamy pozycję okna w dolnej części ekranu
        window_width = 800
        window_height = 150
        taskbar_height = 50
        position_right = (screen_width // 2) - (window_width // 2)
        position_down = screen_height - window_height - taskbar_height
        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

        # Ustawienie przezroczystości okna (wartość od 0.0 do 1.0)
        self.root.attributes('-alpha', 0.8)

        # Usunięcie górnego paska okna
        self.root.overrideredirect(True)

        # Ustawienie okna jako zawsze na wierzchu
        self.root.attributes('-topmost', 1)

        # Tworzenie ramki dla lepszego wyglądu i układu
        frame = ttk.Frame(self.root, padding=10, style="TFrame")
        frame.pack(expand=True, fill="both")

        # Tworzymy dwa Label - jeden na poprzednią, a drugi na aktualną transkrypcję
        self.previous_label = ttk.Label(
            frame,
            font=("Helvetica", 20),
            background="#000000",
            foreground="#AAAAAA",
            anchor="center",
            wraplength=750
        )
        self.previous_label.pack(expand=True, fill="both")

        self.current_label = ttk.Label(
            frame,
            font=("Helvetica", 25),
            background="#000000",
            foreground="#FFFFFF",
            anchor="center",
            wraplength=750
        )
        self.current_label.pack(expand=True, fill="both")

        # Aktualizacja tekstu co 0.5 sekundy
        self.root.after(500, self.update_text)

    def update_text(self):
        # Pobieramy tekst z kolejki i dodajemy do etykiet
        while not self.queue.empty():
            segment = self.queue.get()
            text = segment['text']

            # Ustawiamy poprzednią transkrypcję jako bieżącą, a nową jako aktualną
            self.previous_label.config(text=self.current_label.cget("text"))
            self.current_label.config(text=text)

        # Ponownie ustawiamy aktualizację co 0.5 sekundy
        self.root.after(500, self.update_text)

def run_gui(queue):
    root = Style(theme="darkly").master  # Ustawienie głównego okna z ttkbootstrap
    app = TranscriptionApp(root, queue)
    root.mainloop()
