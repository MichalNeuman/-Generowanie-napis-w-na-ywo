from tkinter import Text
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Frame, Label, Combobox
from ttkbootstrap import StringVar
from queue import Queue
import re
import time

class TranscriptionApp:
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.text_widget = None
        self.last_timestamp = None
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

        # skróty klawiszowe
        self.root.bind("<Control-b>", self.toggle_bold)
        self.root.bind("<Control-i>", self.toggle_italic)
        self.root.bind("<Control-=>", self.increase_font_size)
        self.root.bind("<Control-minus>", self.decrease_font_size)
        self.root.bind("<Control-f>", self.toggle_fullscreen)
        self.root.bind("<Control-m>", self.toggle_mode)

        # Ustawienie przezroczystości okna (wartość od 0.0 do 1.0)
        self.root.attributes('-alpha', 0.9)

        # Usunięcie górnego paska okna
        self.root.overrideredirect(True)

        # Ustawienie okna jako zawsze na wierzchu
        self.root.attributes('-topmost', 1)

        # Tworzenie ramki głównej
        frame = Frame(self.root, padding=10, style="TFrame")
        frame.pack(expand=True, fill="both")

        # Tworzymy Text widget do wyświetlania transkrypcji
        self.text_widget = Text(
            frame,
            font=("Roboto", 25),
            background="#000000",
            foreground="#FFFFFF",
            wrap="word",
            state="disabled",
            spacing1=10,
            spacing2=10,
            spacing3=10
        )
        self.text_widget.pack(expand=True, fill="both")

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
        self.root.bind("<Button-3>", self.handle_click)

        # obsługa przesuwania okna
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def update_text(self):
        """Dodawanie słowo po słowie i czyszczenie, gdy zabraknie miejsca."""
        while not self.queue.empty():
            segment = self.queue.get()
            text = segment['text']
            timestamp = segment.get('timestamp', time.time())

            if self.last_timestamp is not None and (timestamp - self.last_timestamp) > 1:
                self.text_widget.config(state="normal")
                self.text_widget.insert("end", "\n")
                self.text_widget.config(state="disabled")

            words = text.split()

            self.text_widget.config(state="normal")
            for word in words:
                self.text_widget.insert("end", word + " ")
                self.text_widget.see("end")
                self.root.update_idletasks()
                time.sleep(0.1)

            self.text_widget.config(state="disabled")

            self.last_timestamp = timestamp

        # Zaplanuj kolejną aktualizację za 0.5 sekundy
        self.root.after(500, self.update_text)

    def split_text_into_lines(self, text):
        sentence_endings = re.compile(r'(?<=[.!?]) +')
        lines = sentence_endings.split(text)
        return '\n'.join(lines)

    def add_combobox_option(self, label, values, variable, command):
        """Dodaje ComboBox z etykietą jako placeholderem wewnątrz."""

        def on_focus_in(event):
            if option_combobox.get() == label:  # Jeśli tekst to placeholder, wyczyść
                option_combobox.set('')

        def on_focus_out(event):
            if not option_combobox.get():  # Jeśli pole jest puste, przywróć placeholder
                option_combobox.set(label)

        # Tworzymy Combobox
        option_combobox = Combobox(
            self.options_frame,
            textvariable=variable,
            values=values,
            state="readonly",
            width=15
        )
        option_combobox.set(label)  # Ustawienie placeholdera (etykiety jako domyślnej wartości)
        option_combobox.pack(side="left", padx=10, pady=5)
        option_combobox.bind("<<ComboboxSelected>>", command)  # Obsługa wyboru
        option_combobox.bind("<FocusIn>", on_focus_in)  # Obsługa wejścia w pole
        option_combobox.bind("<FocusOut>", on_focus_out)  # Obsługa wyjścia z pola

    def init_combobox_options(self):
        # Rozmiar tekstu
        self.size_var = StringVar(value="25")
        self.add_combobox_option("Text Size", [str(size) for size in range(10, 51, 5)], self.size_var,
                                 self.update_styles)

        # Styl czcionki (normalny/italic)
        self.style_var = StringVar(value="Normal")
        self.add_combobox_option("Font Style", ["Normal", "Italic"], self.style_var, self.update_styles)

        # Tryb jasny/ciemny
        self.mode_var = StringVar(value="Dark")
        self.add_combobox_option("Mode", ["Light", "Dark"], self.mode_var, self.update_mode)

        # Styl czcionki (normalny/pogrubiony)
        self.weight_var = StringVar(value="Normal")
        self.add_combobox_option("Font Weight", ["Normal", "Bold"], self.weight_var, self.update_styles)

        # Rozmiar ekranu
        self.screen_size = StringVar(value="Small")
        self.add_combobox_option("Screen Size", ["Small", "Fullscreen"], self.screen_size, self.update_styles)


    def toggle_mode(self, event=None):
        """Przełącza tryb jasny/ciemny."""
        current_mode = self.mode_var.get()
        self.mode_var.set("Light" if current_mode == "Dark" else "Dark")
        self.update_mode()

    def update_mode(self, event=None):
        """Zmienia tryb na jasny lub ciemny."""
        mode = self.mode_var.get()
        if mode == "Light":
            self.text_widget.config(background="#FFFFFF", foreground="#000000")
            self.root.attributes('-alpha', 0.8)  # Set transparency for light mode
        else:
            self.text_widget.config(background="#000000", foreground="#FFFFFF")
            self.root.attributes('-alpha', 0.8)  # Set transparency for dark mode

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

    def update_styles(self, event=None):
        """Update the font, style, and size of the text."""
        font_name = "Roboto"  # Font remains constant
        font_size = int(self.size_var.get())
        font_weight = "bold" if self.weight_var.get() == "Bold" else "normal"
        font_slant = "italic" if self.style_var.get() == "Italic" else "roman"

        # Update the Text widget's font
        self.text_widget.config(font=(font_name, font_size, font_weight, font_slant))

        # Handle window size change based on Screen Size selection
        screen_size = self.screen_size.get()
        if screen_size == "Fullscreen":
            self.toggle_screen_size(fullscreen=True)
        else:
            self.toggle_screen_size(fullscreen=False)

    def toggle_screen_size(self, fullscreen):
        """Toggle between fullscreen and windowed mode."""
        if fullscreen:
            # Switch to fullscreen mode
            self.root.overrideredirect(True)  # Remove title bar
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")

            # Adjust layout in fullscreen mode
            self.text_widget.pack_forget()  # Remove from current layout
            self.text_widget.pack(expand=True, fill="both", pady=(50, 50))  # Centered with padding
        else:
            # Return to initial size
            window_width = 800
            window_height = 200
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            taskbar_height = 50

            # Calculate position to center
            position_right = (screen_width - window_width) // 2
            position_down = screen_height - window_height - taskbar_height

            # Set window size and position
            self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

            # Remove title bar in "small" mode
            self.root.overrideredirect(True)

            # Restore initial layout
            self.text_widget.pack_forget()
            self.text_widget.pack(expand=True, fill="both")  # Fill the window

        # Refresh window appearance
        self.root.update_idletasks()

    def update_transparency(self, event=None):
        """Aktualizacja przezroczystości okna."""
        alpha_percentage = int(self.alpha_var.get().strip('%'))
        self.root.attributes('-alpha', alpha_percentage / 100)

    def toggle_bold(self, event=None):
        """Przełącza pogrubienie tekstu."""
        current_weight = self.weight_var.get()
        self.weight_var.set("Normal" if current_weight == "Bold" else "Bold")
        self.update_styles()

    def toggle_italic(self, event=None):
        """Przełącza kursywę tekstu."""
        current_style = self.style_var.get()
        self.style_var.set("Normal" if current_style == "Italic" else "Italic")
        self.update_styles()

    def increase_font_size(self, event=None):
        """Zwiększa rozmiar tekstu."""
        current_size = int(self.size_var.get())
        if current_size < 50:  # Maksymalny rozmiar
            self.size_var.set(str(current_size + 1))
            self.update_styles()

    def decrease_font_size(self, event=None):
        """Zmniejsza rozmiar tekstu."""
        current_size = int(self.size_var.get())
        if current_size > 10:  # Minimalny rozmiar
            self.size_var.set(str(current_size - 1))
            self.update_styles()

    def toggle_fullscreen(self, event=None):
        """Przełącza tryb pełnoekranowy."""
        current_size = self.screen_size.get()
        self.screen_size.set("Small" if current_size == "Fullscreen" else "Fullscreen")
        self.update_styles()

    def get_max_chars(self):
        """Oblicza maksymalną liczbę znaków na podstawie szerokości okna."""
        window_width = self.root.winfo_width()
        char_width = 10  # Przybliżona szerokość jednego znaku w pikselach
        return window_width // char_width

    def start_move(self, event):
        """Rozpoczyna przesuwanie okna."""
        if self.screen_size.get() != "Fullscreen":
            self.x = event.x
            self.y = event.y

    def do_move(self, event):
        """Przesuwa okno."""
        if self.screen_size.get() != "Fullscreen":
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

def run_gui(queue):
    root = Style(theme="darkly").master  # Ustawienie głównego okna z ttkbootstrap
    app = TranscriptionApp(root, queue)
    root.mainloop()