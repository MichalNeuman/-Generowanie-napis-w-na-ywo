from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Globalna zmienna do przechowywania transkrypcji
current_text = ""


@app.route("/")
def index():
    """Wyświetl główną stronę z transkrypcją."""
    return render_template("index.html")


@socketio.on("update_text")
def handle_update_text(data):
    """
    Obsługa aktualizacji tekstu z klienta.
    """
    global current_text
    current_text = data["text"]
    print(f"Zaktualizowano tekst: {current_text}")


@socketio.on("get_transcription")
def send_transcription():
    """
    Wysyłanie bieżącej transkrypcji do klienta.
    """
    emit("transcription", {"text": current_text})


def send_new_text(text):
    """Wysyłanie nowego tekstu transkrypcji do klienta."""
    global current_text
    current_text += text + "\n"  # Dodaj nowy fragment do pełnego tekstu
    socketio.emit("transcription", {"text": text})  # Emituj tylko nowy fragment


def start_server():
    """Uruchomienie serwera Flask-SocketIO."""
    print("Uruchamiam serwer na http://localhost:5000...")
    socketio.run(app, host="0.0.0.0", port=5000, use_reloader=False, allow_unsafe_werkzeug=True)

