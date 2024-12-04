import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import paho.mqtt.client as paho
import json
import plotly.graph_objs as go
from plotly.io import to_html
import os
import threading

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# MQTT konfiguracja
mqtt_broker = "1855d1e75c264a00b0fdffc55e0ec025.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_topic = "sensor/data"

# Zmienna przechowująca dane
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


# Funkcja do obsługi MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    if rc == 0:
        client.subscribe(mqtt_topic)
    else:
        print(f"Connection failed with error code {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
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
            x_value = len(data["x"]) + 1
            y_value = value
        except ValueError:
            print("Message is neither JSON nor integer")
            return

    data["x"].append(x_value)
    data["y"].append(y_value)
    
    # Użycie kontekstu aplikacji przed wywołaniem emit
    with app.app_context():  # Zapewnia dostęp do kontekstu aplikacji
        socketio.emit('new_data', {'x': x_value, 'y': y_value})

def start_mqtt():
    print("Próbuję połączyć się z brokerem...")
    client = paho.Client()
    client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
    client.username_pw_set("grupa1", "Haslogrupa1")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker, mqtt_port, 60)
    print("print przed loop_start")
    client.loop_start()

def start_mqtt_thread():
    # Funkcja start_mqtt uruchomiona w tle
    with app.app_context():  # Upewnij się, że kontekst aplikacji jest aktywowany
        start_mqtt()
ap
# Flask routes
@app.route('/')
def index():
    plot_html = create_plot()
    return render_template('index.html', plot_html=plot_html)

# Uruchamianie MQTT w tle (zgodne z Gunicornem)
if __name__ != '__main__':
    threading.Thread(target=start_mqtt_thread).start()
    print("działa")