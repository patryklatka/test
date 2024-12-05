import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_mqtt import Mqtt
import json
import plotly.graph_objs as go
from plotly.io import to_html

app = Flask(__name__)

# Flask-MQTT konfiguracja
app.config['MQTT_BROKER_URL'] = '1855d1e75c264a00b0fdffc55e0ec025.s1.eu.hivemq.cloud'
app.config['MQTT_BROKER_PORT'] = 8883
app.config['MQTT_USERNAME'] = 'grupa1'  # Nazwa użytkownika
app.config['MQTT_PASSWORD'] = 'Haslogrupa1'  # Hasło użytkownika
app.config['MQTT_TLS_ENABLED'] = True  # Szyfrowanie TLS

# Inicjalizacja SocketIO i Flask-MQTT
socketio = SocketIO(app, async_mode='eventlet')
mqtt = Mqtt(app)

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

# Obsługa zdarzeń MQTT
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    mqtt.subscribe('sensor/data')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
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

    # Emitowanie nowych danych do klientów w czasie rzeczywistym
    socketio.emit('new_data', {'x': x_value, 'y': y_value})

# Flask routes
@app.route('/')
def index():
    plot_html = create_plot()
    return render_template('index.html', plot_html=plot_html)

# Konfiguracja Gunicorna
if __name__ != '__main__':
    print("Gunicorn started with app:app")
