import io
import random

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


people = {}
started = False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/locations')
def locations():
    locations = get_locations()
    return jsonify({"locations": locations})


@app.route('/locations/<location_name>', methods=['POST'])
def locations_add(location_name):
    locations = get_locations()
    if location_name in locations:
        return jsonify({
            "error": "Already exists!"
        }), 409
    add_location(location_name)
    return jsonify({
        "location_name": location_name
    })


@socketio.on('receive_nickname')
def connected(data):
    people.update({request.sid: data.get('nickname')})
    names = get_people()
    emit('before_start', {"names": names}, broadcast=True)


@socketio.on('disconnect')
def disconnected():
    people.pop(request.sid)
    names = get_people()
    emit('before_start', {"names": names}, broadcast=True)


@socketio.on('start')
def start():
    players = [Player(sid, people[sid]) for sid in people]
    locations = get_locations()
    _ = Game(players, locations)
    for player in players:
        emit(
            "role",
            {
                "name": player.name,
                "location": player.role
            },
            room=player.sid
        )


def get_locations():
    with io.open("locations.txt", 'r') as f:
        locations = [line[:-1] for line in f.readlines()]
    return locations


def add_location(location_name):
    with io.open("locations.txt", 'a') as f:
        print(location_name, file=f)


def get_people():
    names = []
    for key in people:
        names.append(people[key])
    return names


if __name__ == '__main__':
    socketio.run(app)


class Game(object):
    def __init__(self, players, locations):
        self.locations = locations
        self.location = random.choice(self.locations)
        self.players = players
        self.spy = random.choice(self.players)
        self.spy.role = "Spy"
        for player in players:
            if player != self.spy:
                player.role = self.location


class Location(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Player(object):
    def __init__(self, sid, name):
        self.sid = sid
        self.role = ""
        self.name = name


class Regular(Player):
    def __init__(self, sid, name):
        super(Player, self).__init__(sid, name)


class Spy(Player):
    def __init__(self, sid, name):
        super(Player, self).__init__(sid, name)
