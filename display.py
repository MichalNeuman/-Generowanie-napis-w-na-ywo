from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Frame, Label, Combobox
from ttkbootstrap import StringVar  # Dodaj ten import
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
        window_height = 200
        taskbar_height = 50
        position_right = (screen_width // 2) - (window_width // 2)
        position_down = screen_height - window_height - taskbar_height
        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

        # Ustawienie przezroczystości okna (wartość od 0.0 do 1.0)
        self.root.attributes('-alpha', 0.9)

        # Usunięcie górnego paska okna
        self.root.overrideredirect(True)

        # Ustawienie okna jako zawsze na wierzchu
        self.root.attributes('-topmost', 1)

        # Tworzenie ramki głównej
        frame = Frame(self.root, padding=10, style="TFrame")
        frame.pack(expand=True, fill="both")

        # Tworzymy dwa Label - jeden na poprzednią, a drugi na aktualną transkrypcję
        self.previous_label = Label(
            frame,
            font=("Helvetica", 20),
            background="#000000",
            foreground="#AAAAAA",
            anchor="center",
            wraplength=750,
            bootstyle="inverse"
        )
        self.previous_label.pack(expand=True, fill="both")

        self.current_label = Label(
            frame,
            font=("Helvetica", 25),
            background="#000000",
            foreground="#FFFFFF",
            anchor="center",
            wraplength=750,
            bootstyle="inverse"
        )
        self.current_label.pack(expand=True, fill="both")

        # Panel opcji (początkowo ukryty, poza oknem)
        self.options_frame = Frame(self.root, padding=5, style="TFrame")
        self.options_frame.place(x=0, y=-100, width=window_width, height=100)

        # Inicjalizacja opcji z ComboBoxami
        self.init_combobox_options()

        # Aktualizacja tekstu co 0.5 sekundy
        self.root.after(500, self.update_text)

        # Flaga wskazująca, czy panel jest widoczny
        self.options_visible = False

        # Obsługa kliknięcia w okno
        self.root.bind("<Button-1>", self.handle_click)

    def add_combobox_option(self, label, values, variable, command):
        """Dodaje opcję w panelu opcji z etykietą i ComboBoxem."""
        option_label = Label(self.options_frame, text=f"{label}:", foreground="#DDDDDD", font=("Helvetica", 9))
        option_label.pack(side="left", padx=5)
        option_combobox = Combobox(
            self.options_frame,
            textvariable=variable,
            values=values,
            state="readonly",
            width=10
        )
        option_combobox.pack(side="left", padx=5)
        option_combobox.bind("<<ComboboxSelected>>", command)

    def init_combobox_options(self):
        # Rozmiar tekstu
        self.size_var = StringVar(value="25")
        self.add_combobox_option("Text Size", [str(size) for size in range(10, 51, 5)], self.size_var,
                                 self.update_styles)

        # Czcionka
        self.font_var = StringVar(value="Helvetica")
        self.add_combobox_option("Font", ["Helvetica", "Arial", "Courier", "Times New Roman"], self.font_var,
                                 self.update_styles)

        # Przezroczystość
        #self.alpha_var = StringVar(value="90%")
        #self.add_combobox_option("Transparency", [f"{i}%" for i in range(10, 101, 10)], self.alpha_var,
                                 #self.update_transparency)

        # Tryb jasny/ciemny
        self.mode_var = StringVar(value="Dark")
        self.add_combobox_option("Mode", ["Light", "Dark"], self.mode_var, self.update_mode)

        # Styl czcionki (normalny/pogrubiony)
        self.weight_var = StringVar(value="Normal")
        self.add_combobox_option("Font Weight", ["Normal", "Bold"], self.weight_var, self.update_styles)

        self.screen_size = StringVar(value="Small")
        self.add_combobox_option("Screen Size", ["Small", "Fullscreen"], self.screen_size, self.update_styles)

    def update_mode(self, event=None):
        """Zmienia tryb na jasny lub ciemny."""
        mode = self.mode_var.get()
        if mode == "Light":
            self.previous_label.config(background="#FFFFFF", foreground="#000000")
            self.current_label.config(background="#FFFFFF", foreground="#000000")
        else:
            self.previous_label.config(background="#000000", foreground="#AAAAAA")
            self.current_label.config(background="#000000", foreground="#FFFFFF")

    def handle_click(self, event):
        """Sprawdza, czy kliknięto poza opcje, aby schować pasek."""
        if not self.options_frame.winfo_ismapped():
            self.toggle_options_panel()  # Otwórz, jeśli nie jest widoczny
        else:
            # Pobierz współrzędne kursora
            x, y = event.x_root, event.y_root
            # Pobierz współrzędne opcji
            panel_x1 = self.options_frame.winfo_rootx()
            panel_y1 = self.options_frame.winfo_rooty()
            panel_x2 = panel_x1 + self.options_frame.winfo_width()
            panel_y2 = panel_y1 + self.options_frame.winfo_height()

            # Jeśli kliknięto poza opcjami, schowaj panel
            if not (panel_x1 <= x <= panel_x2 and panel_y1 <= y <= panel_y2):
                self.toggle_options_panel()

    def toggle_options_panel(self):
        """Rozpocznij animację wysuwania lub chowania panelu."""
        self.animate_panel(0 if not self.options_visible else -100)
        self.options_visible = not self.options_visible

    def animate_panel(self, target_y, step=5):
        """Animacja paska opcji."""
        current_y = self.options_frame.winfo_y()
        if current_y == target_y:
            return
        new_y = current_y + step if current_y < target_y else current_y - step
        self.options_frame.place(y=new_y)
        self.root.after(10, lambda: self.animate_panel(target_y, step))

    def update_text(self):
        """Aktualizacja tekstu co 0.5 sekundy."""
        while not self.queue.empty():
            segment = self.queue.get()
            text = segment['text']
            self.previous_label.config(text=self.current_label.cget("text"))
            self.current_label.config(text=text)
        self.root.after(500, self.update_text)

    def update_styles(self, event=None):
        """Aktualizacja czcionki, stylu i rozmiaru tekstu."""
        font_name = self.font_var.get()
        font_size = int(self.size_var.get())
        font_weight = "bold" if self.weight_var.get() == "Bold" else "normal"
        self.current_label.config(font=(font_name, font_size, font_weight))
        self.previous_label.config(font=(font_name, font_size - 5, font_weight))

        # Obsługa zmiany rozmiaru okna na podstawie wyboru w Screen Size
        screen_size = self.screen_size.get()
        if screen_size == "Fullscreen":
            self.toggle_screen_size(fullscreen=True)
        else:
            self.toggle_screen_size(fullscreen=False)

    def toggle_screen_size(self, fullscreen):
        """Zmienia rozmiar okna na pełny ekran lub początkowy."""
        if fullscreen:
            # Przejście do trybu pełnoekranowego
            self.root.overrideredirect(True)  # Usuń pasek tytułu
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")

            # Dostosowanie układu w trybie pełnoekranowym
            self.previous_label.pack_forget()  # Usuń z obecnego układu
            self.current_label.pack_forget()

            self.previous_label.pack(expand=False, fill="x", pady=(50, 0))  # Trochę wyżej
            self.current_label.pack(expand=True, fill="both", pady=(0, 50))  # Na środku
        else:
            # Powrót do początkowego rozmiaru
            window_width = 800
            window_height = 200
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            taskbar_height = 50

            # Wyliczenie pozycji do wyśrodkowania
            position_right = (screen_width - window_width) // 2
            position_down = screen_height - window_height - taskbar_height

            # Ustawienie rozmiaru i pozycji okna
            self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

            # Usuń pasek tytułu w trybie "small"
            self.root.overrideredirect(True)

            # Przywrócenie początkowego układu
            self.previous_label.pack_forget()
            self.current_label.pack_forget()

            self.previous_label.pack(expand=True, fill="both")  # Na górze
            self.current_label.pack(expand=True, fill="both")  # Na dole

        # Odświeżenie wyglądu okna
        self.root.update_idletasks()

    def update_transparency(self, event=None):
        """Aktualizacja przezroczystości okna."""
        alpha_percentage = int(self.alpha_var.get().strip('%'))
        self.root.attributes('-alpha', alpha_percentage / 100)


def run_gui(queue):
    root = Style(theme="darkly").master  # Ustawienie głównego okna z ttkbootstrap
    app = TranscriptionApp(root, queue)
    root.mainloop()