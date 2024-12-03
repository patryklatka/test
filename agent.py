import paho.mqtt.client as mqtt
import ssl

# Funkcja wywoływana po połączeniu z brokerem
def on_connect(client, userdata, flags, rc):
    print(f"Połączono z brokerem, kod: {rc}")
    # Subskrybuj temat 'encyclopedia/#'
    client.subscribe("encyclopedia/#")

# Funkcja wywoływana po otrzymaniu wiadomości
def on_message(client, userdata, msg):
    print(f"Otrzymano wiadomość na temat {msg.topic}: {msg.payload.decode()}")

# Tworzymy klienta MQTT
client = mqtt.Client()
client.clean_session = True  # Zapewnia czystą sesję

# Ustawiamy funkcje obsługi
client.on_connect = on_connect

client.on_message = on_message

# Włączamy szyfrowanie TLS
client.tls_set(tls_version=ssl.PROTOCOL_TLS)
client.username_pw_set("grupa1", "Haslogrupa1")
# Łączymy się z brokerem (np. broker.hivemq.com)
broker_address = "1855d1e75c264a00b0fdffc55e0ec025.s1.eu.hivemq.cloud"
client.connect(broker_address, 8883, 60)

# Pętla, która utrzymuje połączenie i nasłuchuje wiadomości
client.loop_forever()
