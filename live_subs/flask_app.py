# Import the necessary libraries
from pathlib import Path
from song import Song, SongList
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# Create a new Flask application
app = Flask(__name__)

# Create a new SocketIO instance
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")
song_list = SongList(Path("./songs"))
song: Song = song_list.current_song()


class Client:

    def __init__(self) -> None:
        self.language = "Deutsch"


clients: dict[str, Client] = {}


# Define a route for the chat application
@app.route('/')
def index():
    global song
    return render_template(
        'index.html',
        song_title=song.title["Deutsch"],
        current_line=song.current_line()["Deutsch"]
    )


@app.route('/leader')
def leader():
    print(song_list.get_list())
    return render_template(
        'leader.html',
        song_list=song_list.get_list(),
        current_line=song.current_line()["Русский"]
    )


@socketio.on('next_song')
def next_song():
    # Emit a message to all connected clients
    global song
    if (song_ := song_list.next_song()) is None:
        return
    song = song_
    song_title = song.title
    for sid, client in clients.items():
        emit('current_song_title', song_title[client.language], to=sid)
        emit('current_line', song.current_line()[client.language], to=sid)


@socketio.on('prev_song')
def prev_song():
    # Emit a message to all connected clients
    global song
    if (song_ := song_list.previous_song()) is None:
        return
    song = song_
    song_title = song.title
    for sid, client in clients.items():
        emit('current_song_title', song_title[client.language], to=sid)
        emit('current_line', song.current_line()[client.language], to=sid)


@socketio.on('get_song')
def get_song(title: str):
    # Emit a message to all connected clients
    global song
    if (song_ := song_list.get_song(title)) is None:
        return
    song = song_
    song_title = song.title
    for sid, client in clients.items():
        emit('current_song_title', song_title[client.language], to=sid)
        emit('current_line', song.current_line()[client.language], to=sid)


# Define a function to handle incoming messages
@socketio.on('message')
def handle_message(message):
    # Emit a message to all connected clients
    emit('message', message, broadcast=True)


# Define a function to handle incoming messages
@socketio.on('next_line')
def next_line():
    # Emit a message to all connected clients
    line = song.next_line()
    if line is None:
        return next_song()
    for sid, client in clients.items():
        emit('current_line', line[client.language], to=sid)


# Define a function to handle incoming messages
@socketio.on('prev_line')
def prev_line():
    # Emit a message to all connected clients
    line = song.previous_line()
    if line is None:
        return prev_song()
    for sid, client in clients.items():
        emit('current_line', line[client.language], to=sid)


@socketio.on("greet")
def greet():
    greets = {"English": "Hello!", "Deutsch": "Hallo!", "Русский": "Привет!"}
    for sid, client in clients.items():
        emit("message", f"{greets[client.language]}", to=sid)


@socketio.on("language")
def language(lang):
    line = song.current_line()
    sid = request.sid
    clients[sid].language = lang
    emit('current_song_title', song.title[lang], to=sid)
    emit('current_line', line[lang], to=sid)


# Define a function to handle user connections
@socketio.on('connect')
def handle_connect():
    # raise ConnectionError(f"someone is connected! {request}")
    clients[request.sid] = Client()


# Define a function to handle user disconnections
@socketio.on('disconnect')
def handle_disconnect():
    del clients[request.sid]


# Run the application
if __name__ == '__main__':
    socketio.run(app)
