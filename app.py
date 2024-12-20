from gevent import monkey
monkey.patch_all()

from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import paho.mqtt.client as paho
import json
import plotly.graph_objs as go
from plotly.io import to_html
import os
from flask_mqtt import Mqtt
import pymysql
import database
pymysql.install_as_MySQLdb()
app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent')

"""
Uruchamiaj w render.com z: gunicorn -w 1 -k gevent -b 0.0.0.0:$PORT app:app

Przez to że używam flask_mqtt, warning z websocketem naprawia uruchamianie z: gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app
"""

# Konfiguracja bazy danych MySQL (freemysqlhosting)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql7747736:dh5p3q81iR@sql7.freemysqlhosting.net/sql7747736'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database.db.init_app(app)


# Tworzenie tabeli w bazie (tylko przy pierwszym uruchomieniu)
with app.app_context():
    database.db.create_all()  
    ###############################################
    # chwilowe uzupelnianie tabeli
    
    # database.populate_sensor_types(database.typy_sensorow)
    # database.populate_sensors(database.slownik_sensorow)

    ###################################
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

    if topic == gr1_temperature_topic:  # Obsługa temperatury
        measurement_date = datetime.now().replace(microsecond=0).isoformat()
        temperature = payload
        print(f"Odebrana temperatura to {temperature} i czas {measurement_date}")

        # Emitowanie nowych danych do klienta
        with app.app_context():
            socketio.emit('gr1_new_temperature_data', {'x': measurement_date, 'y': temperature})
            database.add_measurement(3, measurement_date, temperature)

    elif topic == gr1_light_topic:  # Obsługa światła
        if payload in ['on', 'off']:
            state = 'włączono' if payload == 'on' else 'wyłączono'
            print(f"Światło zostało {state}")
            # Emitowanie stanu swiatla do klienta
            with app.app_context():
                socketio.emit('gr1_light_state', {'state': payload})
                database.update_sensor_state(1, payload) 
                """
                Brak uniwersalności kodu. 
                Opieram się na kolejności elementów w bazie zgodnie z: ["Czujnik światła", "Wiatrak", "Czujnik temperatury", "Czujnik wilogtności"]
                                                    Odpowiednio ID:             1               2               3                   4
                KONIECZNIE DO POPRAWY
                """

    elif topic == gr1_fan_topic:  # Obsługa wiatraka
        if payload in ['on', 'off']:
            state = 'włączony' if payload == 'on' else 'wyłączony'
            print(f"Wiatrak został {state}")
            # Aktualizacja stanu wiatraka w bazie danych
            # Emitowanie stanu wiatraka do klienta
            with app.app_context():
                socketio.emit('gr1_fan_state', {'state': payload})
                database.update_sensor_state(2, payload)
                """
                Brak uniwersalności kodu. 
                Opieram się na kolejności elementów w bazie zgodnie z: ["Czujnik światła", "Wiatrak", "Czujnik temperatury", "Czujnik wilogtności"]
                                                Odpowiednio ID:             1               2               3                   4
                KONIECZNIE DO POPRAWY
                """

    elif topic == gr1_humidity_topic:  # Obsługa wilgotności
        measurement_date = datetime.now().replace(microsecond=0).isoformat()
        humidity = payload
        print(f"Odebrana wilgotnosc to {humidity} i czas {measurement_date}")

        # Emitowanie nowych danych do klienta
        with app.app_context():
            socketio.emit('gr1_new_humidity_data', {'x': measurement_date, 'y': humidity})
            database.add_measurement(4, measurement_date, humidity)


# Funkcja do obsługi komendy włącz/wyłącz światło
@socketio.on('gr1_light_command')
def handle_light_command(data):
    command = data['command']
    if command in ['on', 'off']:
        mqtt.publish(gr1_light_topic, command)
        print(f"Wysłano komendę {command} do tematu {gr1_light_topic}")

# Funkcja do obsługi komendy włącz/wyłącz wiatraka
@socketio.on('gr1_fan_command')
def handle_fan_command(data):
    command = data['command']
    if command in ['on', 'off']:
        mqtt.publish(gr1_fan_topic, command)
        print(f"Wysłano komendę {command} do tematu {gr1_fan_topic}")


# Inicjalne wysyłanie stanów sensorów do klienta
@socketio.on('get_states')
def send_states():
    try:
        # Pobranie stanów z bazy danych
        states = database.SensorsStates.query.all()
        states_list = [
            {'sensor_id': state.sensor_id, 'state': state.state}
            for state in states
        ]
        # Emitowanie do klienta
        print("Stany po odświeżeniu:", states_list)
        emit('initial_states', states_list)
    except Exception as e:
        print(f"Error fetching states: {e}")


# Funkcja do wysyłania danych wykresu przy połączeniu WebSocket
@socketio.on('connect')
def send_initial_chart_data():
    # Pobranie danych z bazy dla temperatury
    temp_measurements = database.Measurements.query.filter_by(sensor_id=3).order_by(database.Measurements.date).all()
    data = [{"x": temp.date.isoformat(), "y": temp.value} for temp in temp_measurements]
    print("initial temp data", data)
    # Wysłanie danych do klienta
    socketio.emit('initial_temp_chart_data', data)

    humidity_measurements = database.Measurements.query.filter_by(sensor_id=4).order_by(database.Measurements.date).all()
    data = [{"x": humidity.date.isoformat(), "y": humidity.value} for humidity in humidity_measurements]
    print("initial humidity", data)
    # Wysłanie danych do klienta
    socketio.emit('initial_humidity_chart_data', data)

# Flask routes
@app.route('/')
def menu():
    return render_template('menu.html')

# Uruchamianie aplikacji
if __name__ == '__main__':
    print("Próbuję połączyć się z brokerem...")
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
