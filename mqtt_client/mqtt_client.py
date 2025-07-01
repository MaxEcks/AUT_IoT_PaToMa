"""
@file mqtt_client.py
@brief MQTT-Client zur Aufnahme und Speicherung von Sensordaten aus der Teaching Factory

Dieses Modul liest die MQTT-Konfiguration aus einer YAML-Datei, verbindet sich mit dem Broker,
abonniert relevante Topics und speichert empfangene Nachrichten strukturiert in einer TinyDB-Datenbank.
"""

import os
import json
import yaml
import paho.mqtt.client as mqtt
from database.database import DatabaseConnector

# Konfigurationsdatei laden (config.yaml)
CONFIG_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml'))

try:
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    mqtt_config = config["mqtt"]
except Exception as e:
    raise RuntimeError(f"Fehler beim Laden der Konfigurationsdatei ({CONFIG_PATH}): {e}")

# MQTT Parameter extrahieren (von config.yaml)
broker = mqtt_config["broker"]
port = mqtt_config["port"]
topic = mqtt_config["topic"]
username = mqtt_config["username"]
password = mqtt_config["password"]

# MQTT Topic Definitionen
recipe = "iot1/teaching_factory/recipe"
temperature = "iot1/teaching_factory/temperature"
dispenser_red = "iot1/teaching_factory/dispenser_red"
dispenser_blue = "iot1/teaching_factory/dispenser_blue"
dispenser_green = "iot1/teaching_factory/dispenser_green"
scale_final_weight = "iot1/teaching_factory/scale/final_weight"
drop_oscillation = "iot1/teaching_factory/drop_oscillation"
ground_truth = "iot1/teaching_factory/ground_truth"

def table_name_from_topic(topic: str) -> str:
    """
    @brief Ordnet ein MQTT-Topic einem DB-Tabellennamen zu
    @param topic Vollständiger Topic-String
    @return Tabellenname für TinyDB
    """
    mapping = {
        recipe: "recipe",
        temperature: "temperature",
        dispenser_red: "dispenser_red",
        dispenser_blue: "dispenser_blue",
        dispenser_green: "dispenser_green",
        scale_final_weight: "final_weight",
        drop_oscillation: "drop_oscillation",
        ground_truth: "ground_truth"
    }
    if topic in mapping:
        return mapping[topic]
    else:
        raise ValueError(f"Unbekanntes Topic: {topic}")
    
def on_connect(client, userdata, flags, rc, properties=None):
    """
    @brief Callback bei erfolgreicher oder fehlerhafter MQTT-Verbindung
    @param rc Return-Code (0 ... OK; > 0 ... Fehler)
    """
    if rc == 0:
        print("Erfolgreich mit MQTT-Broker verbunden.")
    else:
        print(f"Fehler beim Verbinden mit MQTT-Broker (Code {rc})")

def on_disconnect(client, userdata, rc):
    """
    @brief Callback bei Trennung vom MQTT-Broker
    @param rc Disconnect-Code
    """
    print(f"Verbindung zum MQTT-Broker getrennt (Code {rc})")
    try:
        client.reconnect()
        print("Reconnect initiiert ...")
    except Exception as e:
        print("Reconnect fehlgeschlagen: ", e)

def on_message(client, userdata, message):
    """
    @brief Callback für eingehende MQTT-Nachrichten
    Parsed die Payload (JSON oder Rohtext) und speichert sie in die jeweilige Tabelle.
    @param message MQTT-Nachricht (inkl. Topic und Payload)
    """
    db = DatabaseConnector()
    try:
        payload_raw = message.payload.decode()
        try:
            payload = json.loads(payload_raw)
        except json.JSONDecodeError:
            payload = {"raw": payload_raw}  # Fallback für unstrukturierte Payloads
        
        table_name = table_name_from_topic(message.topic)
        table = db.get_table(table_name)
        table.insert({
            "topic": message.topic,
            "payload": payload
        })
        print(f"Daten in Tabelle \"{table_name}\" eingefügt.")

    except Exception as e:
        print(f"Fehler beim Einfügen der Daten von Topic \"{message.topic}\" in die Datenbank: ", e)

# MQTT-Client initialisieren
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set(username, password)              
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_message = on_message                          

try:
    mqttc.connect(broker, port)
    mqttc.subscribe(topic, qos=0)
except Exception as e:
    raise ConnectionError(f"Verbindungsaufbau zum MQTT-Broker fehlgeschlagen: {e}")

# MQTT-Client-Schleife (nicht-blockierend)
try:
    while True:
        mqttc.loop(0.5)
except KeyboardInterrupt:
    print("MQTT-Client wird beendet ...")
except Exception as e:
    print("Fehler im MQTT-Loop:", e)