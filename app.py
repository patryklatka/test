from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import paho.mqtt.client as paho
import json
import plotly.graph_objs as go
from plotly.io import to_html
import os
from flask_mqtt import Mqtt
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()
app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent')

"""
Uruchamiaj w render.com z: gunicorn -w 1 -k gevent -b 0.0.0.0:$PORT app:app

Przez to że używam flask_mqtt, warning z websocketem naprawia uruchamianie z: gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app
"""

# # Konfiguracja bazy danych MySQL (freemysqlhosting)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql7747736:dh5p3q81iR@sql7.freemysqlhosting.net/sql7747736'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Inicjalizacja bazy danych
# db = SQLAlchemy(app)

# # Model do przechowywania stanów urządzeń
# class DeviceState(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     device_name = db.Column(db.String(50), unique=True, nullable=False)
#     state = db.Column(db.String(10), nullable=False)  # np. 'on'/'off'

# # Tworzenie tabeli w bazie (tylko przy pierwszym uruchomieniu)
# with app.app_context():
#     db.create_all()
    
# Konfiguracja MQTT
app.config['MQTT_BROKER_URL'] = "1855d1e75c264a00b0fdffc55e0ec025.s1.eu.hivemq.cloud"
app.config['MQTT_BROKER_PORT'] = 8883
app.config['MQTT_USERNAME'] = "grupa1"
app.config['MQTT_PASSWORD'] = "Haslogrupa1"
app.config['MQTT_TLS_ENABLED'] = True
app.config['MQTT_KEEP_ALIVE'] = 60
app.config['MQTT_TLS_VERSION'] = paho.ssl.PROTOCOL_TLS   # przetestuj też ssl.PROTOCOL_TLS_CLIENT

mqtt = Mqtt(app)

# Tematy MQTT
gr1_temperature_topic = "gr1/temperature"
gr1_light_topic = "gr1/swiatlo"
gr1_fan_topic = "gr1/wiatrak"
gr1_humidity_topic = "gr1/wilgotnosc"

# Zmienna przechowująca dane dla wilgotności
humidity_first_group = {
    "x": [],
    "y": []
}

# Zmienna przechowująca dane
temperature_first_group = {
    "x": [],
    "y": []
}


# Obsługa połączenia MQTT
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    if rc == 0:
        mqtt.subscribe(gr1_temperature_topic)  # Subskrypcja danych sensora
        mqtt.subscribe(gr1_light_topic)  # Subskrypcja światła
        mqtt.subscribe(gr1_fan_topic)  # Subskrypcja wiatraka
        mqtt.subscribe(gr1_humidity_topic)  # Subskrypcja wilgotności
    else:
        print(f"Connection failed with error code {rc}")

# Obsługa wiadomości MQTT
@mqtt.on_message()
def handle_message(client, userdata, message):
    topic = message.topic  # Temat wiadomości MQTT
    payload = message.payload.decode()  # Dekodowanie ładunku wiadomości
    print(f"Odebrano wiadomość na temacie '{topic}': {payload}")

    if topic == gr1_temperature_topic:  # Obsługa danych sensora
        try:
            json_data = json.loads(payload)
            if "x" in json_data and "y" in json_data:
                x_value = json_data["x"]
                y_value = json_data["y"]
            else:
                raise ValueError("Message JSON lacks 'x' and 'y'")
        except json.JSONDecodeError:
            try:
                value = int(payload)
                x_value = len(temperature_first_group["x"]) + 1
                y_value = value
            except ValueError:
                print("Message is neither JSON nor integer")
                return

        temperature_first_group["x"].append(x_value)
        temperature_first_group["y"].append(y_value)

        # Emitowanie nowych danych do klienta
        with app.app_context():
            socketio.emit('gr1_new_temperature_data', {'x': x_value, 'y': y_value})

    elif topic == gr1_light_topic:  # Obsługa światła
        if payload in ['on', 'off']:
            state = 'włączono' if payload == 'on' else 'wyłączono'
            print(f"Światło zostało {state}")
            # Emitowanie stanu swiatla do klienta
            with app.app_context():
                socketio.emit('gr1_light_state', {'state': payload})

    elif topic == gr1_fan_topic:  # Obsługa wiatraka
        if payload in ['on', 'off']:
            state = 'włączony' if payload == 'on' else 'wyłączony'
            print(f"Wiatrak został {state}")
            # Emitowanie stanu wiatraka do klienta
            with app.app_context():
                socketio.emit('gr1_fan_state', {'state': payload})

    elif topic == gr1_humidity_topic:  # Obsługa wilgotności
        try:
            json_data = json.loads(payload)
            if "x" in json_data and "y" in json_data:
                x_value = json_data["x"]
                y_value = json_data["y"]
            else:
                raise ValueError("Message JSON lacks 'x' and 'y'")
        except json.JSONDecodeError:
            try:
                value = float(payload)
                x_value = len(humidity_first_group["x"]) + 1
                y_value = value
            except ValueError:
                print("Message is neither JSON nor float")
                return

        humidity_first_group["x"].append(x_value)
        humidity_first_group["y"].append(y_value)

        # Emitowanie nowych danych do klienta
        with app.app_context():
            socketio.emit('gr1_new_humidity_data', {'x': x_value, 'y': y_value})


# Funkcja do obsługi komendy włącz/wyłącz światło
@socketio.on('gr1_light_command')
def handle_light_command(data):
    command = data['command']
    if command in ['on', 'off']:
        mqtt.publish(gr1_light_topic, command)
        print(f"Wysłano komendę {command} do tematu {gr1_light_topic}")

# Funkcja do obsługi komendy włącz/wyłącz wiatraka
@socketio.on('fan_command')
def handle_fan_command(data):
    command = data['command']
    if command in ['on', 'off']:
        mqtt.publish(gr1_fan_topic, command)
        print(f"Wysłano komendę {command} do tematu {gr1_fan_topic}")


# Flask routes
@app.route('/')
def menu():
    return render_template('menu.html')

# Uruchamianie aplikacji
if __name__ == '__main__':
    print("Próbuję połączyć się z brokerem...")
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
