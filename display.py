from tkinter import Tk, Label, Scrollbar, Text, END, Frame

class TranscriptionApp:
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.root.title("Transkrypcja")
        self.root.geometry("800x200")

        #okno półprzezroczyste
        self.root.attributes('-alpha', 0.8)

        # Tworzenie ramki dla lepszego wyglądu i układu
        frame = Frame(self.root, bg="#FFFFFF")  # Białe tło
        frame.pack(expand=True, fill="both")

        # Tworzymy pole tekstowe z przewijaniem
        self.text_widget = Text(
            frame,
            wrap="word",
            font=("Helvetica", 18),
            bg="#FFFFFF",
            fg="#000000",
            borderwidth=0,
            padx=20,
            pady=20,
            spacing3=20
        )
        self.text_widget.pack(expand=True, fill="both")

        # Dodajemy pionowy scroll bar
        self.scrollbar = Scrollbar(self.text_widget)
        self.scrollbar.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_widget.yview)

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
            self.text_widget.tag_add("center", "end-1l", "end")
            self.text_widget.config(state="disabled")

            # Automatyczne przewijanie do ostatniego wiersza
            self.text_widget.see(END)

        # Ponownie ustawiamy aktualizację co 0.5 sekundy
        self.root.after(500, self.update_text)

def run_gui(queue):
    root = Tk()
    app = TranscriptionApp(root, queue)
    root.mainloop()
