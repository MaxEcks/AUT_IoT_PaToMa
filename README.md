# AUT_IoT_PaToMa
Finalprojekt Automatisierungstechnik IoT-Teil

## Informationen zur Verwendung von Large Language Models (LLMs)
Bei der Umsetzung dieses Projekts wurden Large Language Models (LLMs) wie ChatGPT verwendet, um Code-Snippets zu generieren und zu optimieren. 

## Link zur Aufgabenstellung
[Automatisierungstechnik – IoT Lehrfabrik](https://jhumci.github.io/2024_SoSe_Automatisierungstechnik/)

---

## Umgesetzte Aufgaben

Dieses Projekt umfasst mehrere Teilaufgaben aus dem Modul Automatisierungstechnik:

| Aufgabe   | Titel                                              | Kurzbeschreibung                                                                 |
|-----------|----------------------------------------------------|----------------------------------------------------------------------------------|
| **12.1.1** | MQTT-Client                                        | Füllstandswerte werden über MQTT gesendet, Retain-Flag und Metadaten berücksichtigt |
| **12.1.2** | Datenempfang, Speicherung & Visualisierung        | Empfang der Daten per MQTT, Speicherung in TinyDB, Visualisierung via Dash      |
| **12.3**   | Regressionsmodell für Endgewicht                  | Lineares Modell zur Vorhersage des Endgewichts, Anwendung auf neuen Datensatz   |
| **12.4**   | Klassifikationsmodell für defekte Flaschen        | Extraktion statistischer & spektraler Features, Modellvergleich, Evaluation     |


---

## Projektstruktur

```plaintext
AUT_IoT_PaToMa/
├── .venv/                     # Virtuelle Umgebung
├── config/
│   └── config.yaml            # MQTT-Konfiguration
├── database/
│   ├── data.csv               # gespeicherte Flaschendaten (dataframe)
│   ├── database.py            # TinyDB-Schnittstelle
│   ├── transform.py           # Datenaufbereitung (erstellt data.csv)
├── mqtt_client/
│   └── mqtt_client.py         # MQTT-Client zur Datenaufnahme (Aufgabe 12.1.2)
├── visualization/
│   └── dashboard.py           # Dash Web-App zur Visualisierung (Aufgabe 12.1.2)
├── regression/
│   ├── reg_Czermak-Eckstein-Neuner.csv   # vorhergesagte Flaschengewichte
│   └── X.csv                  # Daten für Vorhersage der Flaschengewichte
├── notebooks/
│   ├── Aufgabe_12.1.1_Report.ipynb   # MQTT-Implementierung TwinCAT
│   ├── Aufgabe_12.1.2_Report.ipynb   # Datenspeicherung und Visualisierung
│   ├── Aufgabe_12.3_Regressionsmodell.ipynb      # Regressionsmodell für Endgewicht
│   └── Aufgabe_12.4_Klassifikationsmodell.ipynb  # Klassifikation defekter Flaschen
├── requirements.txt
├── README.md
└── .gitignore
```

## Virtuelle Umgebung

- erstellen:  `python -m venv .venv`
- aktivieren: `.\.venv\Scripts\activate`
- beenden:    `deactivate`

## Abhängigkeiten

- erstellen:    `pip freeze > requirements.txt`
- installieren: `pip install -r requirements.txt`

## Scripte ausführen
Die Module befinden sich in Unterordnern, deshalb ist der **Start via Modulpfad** notwendig.

- MQTT-Client starten:    `python -m mqtt_client.mqtt_client`
- Daten aufbereiten:      `python -m database.transform`
- Visualisierung starten: `python -m visualization.dashboard`