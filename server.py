from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Globalna zmienna do przechowywania transkrypcji
current_text = ""


@app.route("/")
def index():
    """Wyświetla główną stronę z transkrypcją na żywo."""
    return render_template("index.html")


@socketio.on("get_transcription")
def send_transcription():
    """
    Wysyła pełną transkrypcję do klienta na żądanie.
    """
    emit("transcription", {"text": current_text})


@socketio.on("update_text")
def handle_update_text(data):
    """
    Obsługuje aktualizację konkretnej linii transkrypcji i wyślij zmiany.
    """
    global current_text
    lines = current_text.split("\n")  # Podziel transkrypcję na linie
    index = data["index"]  # Indeks aktualizowanej linii
    updated_line = data["text"]  # Zaktualizowany tekst linii

    if 0 <= index < len(lines):
        lines[index] = updated_line  # Zaktualizuj istniejącą linię
    elif index >= len(lines):
        # Dodaj brakujące linie, jeśli indeks wykracza poza istniejące
        lines.extend([""] * (index - len(lines) + 1))
        lines[index] = updated_line

    current_text = "\n".join(lines)  # Zaktualizuj pełny tekst transkrypcji
    print(f"Zaktualizowano linię {index}: {updated_line}")

    # Wyślij aktualizację konkretnej linii do wszystkich klientów oprócz nadawcy
    socketio.emit("line_update", {"index": index, "text": updated_line}, include_self=False)


def send_new_text(text):
    """
    Dodaje nowy tekst i wyślij go do wszystkich połączonych klientów.
    """
    global current_text
    current_text += text + "\n"  # Dodaj nowy tekst do pełnej transkrypcji
    index = len(current_text.split("\n")) - 2  # Oblicz indeks nowej linii
    print(f"Wysyłanie nowego tekstu na linii {index}: {text}")

    # Wyślij nowy tekst jako aktualizację linii
    socketio.emit("line_update", {"index": index, "text": text}, skip_sid=None)


def start_server():
    """Uruchomia serwer Flask-SocketIO."""
    print("Uruchamianie serwera pod adresem http://localhost:5000...")
    socketio.run(app, host="0.0.0.0", port=5000, use_reloader=False, allow_unsafe_werkzeug=True)
