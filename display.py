from tkinter import Tk, Label, Scrollbar, Text, END, Frame

class TranscriptionApp:
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.root.title("Transkrypcja")

        # Pobieramy wymiary ekranu
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Ustawiamy pozycję okna w dolnej części ekranu z marginesem nad paskiem zadań
        window_width = 800
        window_height = 200  # Ustawiamy wysokość na 200 pikseli, aby zmieściły się 3 linijki tekstu
        taskbar_height = 50  # Zakładamy wysokość paska zadań, możesz dostosować
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
        frame = Frame(self.root, bg="#000000")  # Czarne tło
        frame.pack(expand=True, fill="both")

        # Tworzymy pole tekstowe
        self.text_widget = Text(
            frame,
            wrap="word",
            font=("Helvetica", 25),
            bg="#000000",  # Czarne tło
            fg="#FFFFFF",  # Biały tekst
            borderwidth=0,
            padx=30,
            pady=10,  # Zmniejszamy padding, aby zmniejszyć marginesy
            spacing3=10,  # Dodajemy odstęp między wierszami
            height=3  # Ustawiamy wysokość na 3 linie
        )
        self.text_widget.pack(expand=True, fill="both")

        # Wyłączamy edycję tekstu przez użytkownika
        self.text_widget.config(state="disabled")

        # Tworzymy tag dla wyrównania środka
        self.text_widget.tag_configure("center", justify="center")

        # Aktualizacja tekstu co 0.5 sekundy
        self.root.after(500, self.update_text)

    def update_text(self):
        # Pobieramy tekst z kolejki i dodajemy do widżetu tekstowego
        while not self.queue.empty():
            segment = self.queue.get()
            text = f"{segment['text']}\n"  # Usunięto czas z formatu tekstu

            # Odblokowujemy pole tekstowe, aby dodać nowy tekst
            self.text_widget.config(state="normal")
            self.text_widget.insert(END, text)
            self.text_widget.tag_add("center", "end-1l", "end")  # Dodajemy tag wyśrodkowujący do nowej linii
            self.text_widget.config(state="disabled")

            # Automatyczne przewijanie do ostatniego wiersza
            self.text_widget.see(END)

        # Ponownie ustawiamy aktualizację co 0.5 sekundy
        self.root.after(500, self.update_text)

def run_gui(queue):
    root = Tk()
    app = TranscriptionApp(root, queue)
    root.mainloop()
