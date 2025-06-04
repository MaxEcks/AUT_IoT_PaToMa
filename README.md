# AUT_IoT_PaToMa
IoT part of AUT final project

## IoT Teaching Factory MQTT Client
Ein MQTT-Client, der Daten einer IoT-Lehrfabrik empfängt und in einer TinyDB-Datenbank speichert.

## Link:
  [Automatisierungstechnik IoT](https://jhumci.github.io/2024_SoSe_Automatisierungstechnik/)

## Virtuelle Umgebung erstellen:
  python -m venv .venv

## Virtuelle Umgebung aktivieren:
  .\\.venv\Scripts\activate

## Virtuelle Umgebung beenden:
  deactivate

## Abhängigkeiten in requirements.txt schreiben:
  pip freeze > requirements.txt

## Abhängigkeiten installieren:
  pip install -r requirements.txt

## Projekt starten (genau so, weil Module in verschiedenen Ordnern sind):
  python -m mqtt_client.mqtt_client
  
## Projektstruktur:
<pre>
AUT_IoT_PaToMa/
├── .venv
├── database/
│   ├── __init__.py
│   └── database.py
├── mqtt_client/
|   ├── __init__.py
│   └── mqtt_client.py
├── visualization/
│   └── __init__.py
├── requirements.txt
├── .gitignore
└── README.md
</pre>
