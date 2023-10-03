from datetime import datetime
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = '10101'
socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app)

# class User:
#     def __init__(self, username, client_id):
#         self.username = username
#         self.client_id = client_id

users = {}

messages = []


@app.route('/')
def index():
    return '<h1>Hello World!</h1>'


@socketio.on('send_message')
def send_message(data):
    sender = data['sender']
    receiver = data['receiver']
    msg = data['message']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 存储消息记录
    messages.append({
        'sender': sender,
        'receiver': receiver,
        'message': msg,
        'timestamp': timestamp
    })

    # 获取接收者的WebSocket连接ID并发送消息
    receiver_sid = users.get(receiver)
    if receiver_sid:
        socketio.emit('message', {
            'sender': sender,
            'message': msg,
            'timestamp': timestamp
        }, room=receiver_sid)


@socketio.on('connect')
def connect():
    client_id = request.sid
    print('Client connected:' + client_id)

    data = request.args
    if 'username' in data:
        username = data['username']
        users[username] = client_id
        print(username)


@socketio.on('disconnect')
def disconnect():
    print(users)
    client_id = request.sid
    disconnect_user = None
    for username, sid in users.items():
        if sid == client_id:
            disconnect_user = username
            break

    if disconnect_user:
        del users[disconnect_user]
        print(f'User disconnected: {disconnect_user}')


@socketio.on('message')
def message(data):
    print(f'Message received: {data}')
    socketio.send(data)


if __name__ == '__main__':
    app.run(debug=True)
