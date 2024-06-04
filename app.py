from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Almacenar las sesiones de los usuarios conectados
active_rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@socketio.on('connect')
def handle_connect():
    if 'username' not in session:
        return False

@socketio.on('join_room')
def on_join(data):
    room = data['room']
    join_room(room)
    if room not in active_rooms:
        active_rooms[room] = []
    active_rooms[room].append(session['username'])
    socketio.emit('user_status', {'users': active_rooms[room]}, room=room)

@socketio.on('leave_room')
def on_leave(data):
    room = data['room']
    leave_room(room)
    if room in active_rooms:
        active_rooms[room].remove(session['username'])
    socketio.emit('user_status', {'users': active_rooms[room]}, room=room)

@socketio.on('draw')
def on_draw(data):
    room = data['room']
    socketio.emit('draw', data['xml'], room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)

