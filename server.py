from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Global variable to store transcription
current_text = ""


@app.route("/")
def index():
    """Display the main page with live transcription."""
    return render_template("index.html")


@socketio.on("update_text")
def handle_update_text(data):
    """
    Handle text updates from a client.
    Broadcast the updated text to all connected clients.
    """
    global current_text
    current_text = data["text"]

    print(f"Text updated: {current_text}")
    # Broadcast the updated text to all connected clients
    socketio.emit("task_update", {"text": current_text}, include_self=False)


@socketio.on("get_transcription")
def send_transcription():
    """
    Send the current transcription to a client.
    """
    emit("transcription", {"text": current_text})


def send_new_text(text):
    """Send new transcription text to clients."""
    global current_text
    current_text += text + "\n"  # Add the new fragment to the full text
    socketio.emit("transcription", {"text": text}, to=None)  # Broadcast to all connected clients



def start_server():
    """Start the Flask-SocketIO server."""
    print("Starting server at http://localhost:5000...")
    socketio.run(app, host="0.0.0.0", port=5000, use_reloader=False, allow_unsafe_werkzeug=True)
