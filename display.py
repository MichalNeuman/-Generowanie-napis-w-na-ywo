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
        line_height = 50  # Zakładamy, że każda linia ma 50 pikseli wysokości
        window_height = line_height * 3  # Dopasowujemy wysokość okna do trzech linii
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
            padx=10,
            pady=5,
            spacing3=5,  # Dopasowujemy odstęp między wierszami
            height=3
        )
        self.text_widget.pack(expand=True, fill="both")

        # Wyłączamy edycję tekstu przez użytkownika
        self.text_widget.config(state="disabled")

        # Tworzymy tag dla wyrównania środka
        self.text_widget.tag_configure("center", justify="center")

        # Usunięcie nadmiarowych linii tekstu po uruchomieniu
        self.clear_text_widget()

        # Aktualizacja tekstu co 0.5 sekundy
        self.root.after(500, self.update_text)

    def clear_text_widget(self):
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", END)
        self.text_widget.config(state="disabled")

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

            # Jeśli jest więcej niż trzy linie tekstu, przewijamy tylko po dodaniu nowej linii
            current_line_count = int(self.text_widget.index('end-1c').split('.')[0])
            if current_line_count > 3:
                self.text_widget.see('end-3l')  # Ustawienie widoczności ostatnich trzech linii

        # Ponownie ustawiamy aktualizację co 0.5 sekundy
        self.root.after(500, self.update_text)


def run_gui(queue):
    root = Tk()
    app = TranscriptionApp(root, queue)
    root.mainloop()
