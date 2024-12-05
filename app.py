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

app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent')

# Konfiguracja MQTT
app.config['MQTT_BROKER_URL'] = "1855d1e75c264a00b0fdffc55e0ec025.s1.eu.hivemq.cloud"
app.config['MQTT_BROKER_PORT'] = 8883
app.config['MQTT_USERNAME'] = "grupa1"
app.config['MQTT_PASSWORD'] = "Haslogrupa1"
app.config['MQTT_TLS_ENABLED'] = True
app.config['MQTT_KEEP_ALIVE'] = 60
app.config['MQTT_TLS_VERSION'] = paho.ssl.PROTOCOL_TLS

mqtt = Mqtt(app)

# Tematy MQTT
mqtt_topic = "sensor/data"
light_topic = "swiatlo"

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

# Obsługa połączenia MQTT
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    if rc == 0:
        mqtt.subscribe(mqtt_topic)
    else:
        print(f"Connection failed with error code {rc}")

# Obsługa wiadomości MQTT
@mqtt.on_message()
def handle_message(client, userdata, message):
    payload = message.payload.decode()
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
    with app.app_context():
        socketio.emit('new_data', {'x': x_value, 'y': y_value})

# Funkcja do obsługi komendy włącz/wyłącz światło
@socketio.on('light_command')
def handle_light_command(data):
    command = data['command']
    if command in ['on', 'off']:
        mqtt.publish(light_topic, command)
        print(f"Wysłano komendę {command} do tematu {light_topic}")

# Flask routes
@app.route('/')
def index():
    plot_html = create_plot()
    return render_template('index.html', plot_html=plot_html)

# Uruchamianie aplikacji
if __name__ == '__main__':
    print("Próbuję połączyć się z brokerem...")
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
