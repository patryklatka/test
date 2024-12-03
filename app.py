import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, has_request_context, request, jsonify
from flask_socketio import SocketIO, emit
import paho.mqtt.client as paho
import threading
import json
import plotly.graph_objs as go
from plotly.io import to_html
import os

app = Flask(__name__)
socketio = SocketIO(app)

# MQTT konfiguracja
mqtt_broker = "1855d1e75c264a00b0fdffc55e0ec025.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_topic = "sensor/data"

# Zmienna przechowująca dane, które będą wysyłane na stronę
data = {
    "x": [],
    "y": []
}

# Funkcja do tworzenia wykresu
def create_plot():
    trace = go.Scatter(
        x=data["x"],
        y=data["y"],
        mode='lines+markers',
        name='Dane',
        hovertext=[f"X: {x_val}, Y: {y_val}" for x_val, y_val in zip(data["x"], data["y"])],
        hoverinfo='text'
    )
    layout = go.Layout(
        title='Dane z MQTT',
        xaxis=dict(title='X'),
        yaxis=dict(title='Y')
    )
    fig = go.Figure(data=[trace], layout=layout)
    return to_html(fig, full_html=False)

# Funkcja do obsługi połączenia MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    if rc == 0:
        print("Połączono z brokerem MQTT!")
        client.subscribe(mqtt_topic)
    else:
        print(f"Połączenie nieudane z kodem błędu {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received message: {payload} on topic {msg.topic}")

    try:
        json_data = json.loads(payload)
        if "x" in json_data and "y" in json_data:
            x_value = json_data["x"]
            y_value = json_data["y"]
        else:
            raise ValueError("Wiadomość JSON nie zawiera kluczy 'x' i 'y'")

    except json.JSONDecodeError:
        try:
            value = int(payload)
            x_value = len(data["x"]) + 1
            y_value = value
        except ValueError:
            print("Wiadomość nie jest liczbą ani JSON-em")
            return

    data["x"].append(x_value)
    data["y"].append(y_value)

    # Sprawdzamy, czy kontekst żądania jest dostępny
    if has_request_context():
        print("Kontekst żądania jest dostępny.")
    else:
        print("Kontekst żądania NIE jest dostępny.")

    # Wysyłamy dane do front-endu przez WebSocket
    socketio.emit('new_data', {'x': x_value, 'y': y_value})

# Uruchamiamy klienta MQTT w osobnym wątku
def start_mqtt():
    client = paho.Client()
    client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
    client.username_pw_set("grupa1", "Haslogrupa1")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_start()

# Trasa Flask
@app.route('/')
def index():
    plot_html = create_plot()
    return render_template('index.html', plot_html=plot_html)

# Uruchamiamy aplikację Flask
if __name__ == '__main__':
    # Uruchamiamy MQTT w osobnym wątku
    print("Próbuję połączyć się z brokerem...")
    mqtt_thread = threading.Thread(target=start_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Uruchamiamy serwer Flask z SocketIO
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
