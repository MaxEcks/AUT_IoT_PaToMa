# 📦 Projektdokumentation: IoT-Datenspeicherung & Visualisierung

## 🧾 Aufgabenstellung

In dieser Aufgabe sollte ein System zur **Datenspeicherung** und **Visualisierung von Zeitreihen** implementiert werden, welches später für die **Fehleranalyse** genutzt wird.

Folgende Anforderungen wurden gestellt:

- Speicherung aller relevanten Topics des MQTT-Servers (`iot1/teaching_factory/#`)
- Nutzung von CSV oder alternativer Datenbankstruktur
- Visualisierung von Zeitreihen mit Python
- Dokumentation inkl. ausgewähltem Plot
- Datenerfassung über mindestens 15 Minuten

---

## 🛠️ Umsetzung

### 🔌 Datenquelle

Die Daten wurden über MQTT vom Broker `158.180.44.197` abonniert (Port 1883, Topic: `iot1/teaching_factory/#`).  
Verwendete Topics u. a.:

- `dispenser_red`, `dispenser_blue`, `dispenser_green`
- `temperature`
- `scale/final_weight`
- `ground_truth`
- `drop_oscillation`

### 💾 Datenspeicherung

- Verwendet wurde [`TinyDB`](https://tinydb.readthedocs.io/en/latest/), eine JSON-basierte, dokumentenorientierte Datenbank.
- Die Struktur wurde vereinheitlicht nach `bottle-id` gruppiert.
- Alle Messwerte einer Flasche befinden sich in einer zusammengefassten Zeile.

> Alternative CSV-Speicherung wurde ebenfalls getestet (siehe `output_single_row_per_bottle.csv`).

### 📊 Visualisierung

Die Visualisierung erfolgt mit:

- [`Dash`](https://dash.plotly.com/) als Web-UI-Framework
- [`Plotly Express`](https://plotly.com/python/plotly-express/) für flexible, interaktive Plots

**Features:**

- Dropdown zur Auswahl einer Flasche (`bottle-id`)
- Zeitreihendarstellung der Drop-Oszillation
- Statusanzeige, ob die Flasche laut `ground_truth` gesprungen ist

---

## 📈 Beispielplot

> Hinweis: Screenshot des Dashboards oder eingebundener Plot (Beispiel siehe unten)

![Vibration Plot](./example_plot.png)

![Dashboard Screenshot](./img/test.png)


---

## 🧪 Beispielcode (Ausschnitt)

```python
@app.callback(
    Output("vibration-plot", "figure"),
    Output("status-box", "children"),
    Input("bottle-dropdown", "value")
)
def update_plot(selected_bottle):
    row = df[df["bottle"] == selected_bottle].iloc[0]
    values = row["vibration_values"]
    ...
