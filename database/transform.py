"""
@file transform.py
@brief Extrahiert und aggregiert alle MQTT-Daten, die sich auf Flaschen beziehen

Dieses Modul lädt gezielt Daten mit Flaschenbezug aus der TinyDB-Datenbank ("database.json")
und erstellt ein "tidy" Pandas DataFrame mit einer Zeile pro Flasche.

Berücksichtigt werden:
- Flaschenbezogene Topics: dispenser_red, dispenser_green, dispenser_blue, final_weight, drop_oscillation, ground_truth
- Temperatur-Topic: temperature (nur mit Zeitstempel, ohne bottle-ID)

Die Temperaturdaten werden den Flaschen anhand von Zeitstempel-Matching zugeordnet:
Für jede Flasche werden drei direkt davorliegende Temperaturwerte (rot, grün, blau) zugeordnet.

Nach Analyse von "database.json" wurde festgestellt, dass die Timestamps von "dispenser_green"
und den Temperaturmessungen (jeweils rot, grün, blau) zeitlich zusammenpassen (Verhältnis 3:1).

Ergebnis: Pro Flasche liegen nun auch "temperature_red", "temperature_green", "temperature_blue" als separate Features vor.
"""

import os
import json
import math
import pandas as pd
from tinydb import TinyDB

def load_data_as_dataframe():
    """
    @brief Lädt und aggregiert alle Sensordaten mit Flaschenbezug aus TinyDB als tidy Pandas DataFrame

    Es werden folgende MQTT-Topics aus "database.json" berücksichtigt:

    - Flaschenbezogene Topics mit "bottle"-Feld:
      - dispenser_red, dispenser_green, dispenser_blue
      - final_weight
      - drop_oscillation
      - ground_truth

    - Temperatur-Topic (temperature):
      - Enthält keine bottle-ID, sondern nur Zeitstempel und Temperaturwert

    Die Temperaturdaten werden über Timestamp-Vergleich exakt den Flaschen aus "dispenser_green" zugewiesen:
    Für jede Flasche werden drei direkt davorliegende Temperaturwerte als `temperature_red`, `temperature_green`, `temperature_blue` gespeichert.

    Die Zuordnung basiert auf der Beobachtung, dass:
    - jede Flasche genau 3 zugehörige Temperaturmessungen hat (Verhältnis 3:1)
    - die Timestamps im Topic "temperature" chronologisch vor dem zugehörigen dispenser_green-Eintrag liegen

    @return Tidy Pandas DataFrame mit aggregierten Flaschendaten (eine Zeile pro bottle)
    @throws FileNotFoundError, ValueError
    """

    # Pfad zur JSON-Datenbank
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.normpath(os.path.join(current_dir, "database.json"))

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Datei nicht gefunden: {json_path}")

    db = TinyDB(json_path)
    raw_data = db.storage.read()
    rows = []
    temperature_entries = []
    green_time = []

    for topic_key, topic_data in raw_data.items():
        # Nur relevante Topics: enthalten "bottle" in Payload
        for entry_id, entry in topic_data.items():
            payload = entry.get("payload", {})

            # falls verschachtelter "raw"-String vorhanden ist
            if isinstance(payload, dict) and "raw" in payload:
                try:
                    payload = json.loads(payload["raw"])
                except:
                    continue

            # Temperaturdaten auslesen
            if topic_key == "temperature":
                if "temperature_C" in payload and "time" in payload:
                    temperature_entries.append({
                        "time": payload["time"],
                        "temperature": payload["temperature_C"]
                    })
                continue

            # Timestamps von dispenser_green für Zuordnung merken
            if topic_key == "dispenser_green" and "bottle" in payload and "time" in payload:
                green_time.append({
                    "time": payload["time"],
                    "bottle": int(payload["bottle"])
                })

            if "bottle" not in payload:
                continue  # Zeile überspringen, wenn keine Flaschen-ID vorhanden
            
            row = {}
            
            try:
                row["bottle"] = int(payload["bottle"])
            except:
                row["bottle"] = payload["bottle"]

            # Füllstand & Vibration nach Farbe
            if "fill_level_grams" in payload:
                color = topic_key.split("_")[-1]
                row[f"fill_level_{color}"] = payload["fill_level_grams"]

            if "vibration-index" in payload:
                color = topic_key.split("_")[-1]
                row[f"vibration_index_{color}"] = payload["vibration-index"]

            # Endgewicht
            if "final_weight" in payload:
                row["final_weight"] = payload["final_weight"]

            # Zeitreihe Drop-Oszillation
            if "drop_oscillation" in payload:
                raw_list = payload["drop_oscillation"]
                try:
                    floats = [float(v) for v in raw_list]
                    clean = [v for v in floats if not math.isnan(v)]
                    row["drop_oscillation"] = clean
                except:
                    row["drop_oscillation"] = []

            # Klassifikationslabel
            if "is_cracked" in payload:
                try:
                    row["is_cracked"] = bool(int(payload["is_cracked"]))
                except:
                    row["is_cracked"] = False

            rows.append(row)

    # DataFrame erstellen
    df = pd.DataFrame(rows)

    # Gruppierung: alle Einträge pro "bottle" zusammenfassen
    if "bottle" not in df.columns:
        raise ValueError("Keine Spalte \"bottle\" gefunden!")

    df = df.groupby("bottle", dropna=False).first().reset_index()

    # Temperaturzuordnung vorbereiten
    green_df = pd.DataFrame(green_time).sort_values("time").reset_index(drop=True)
    temp_df = pd.DataFrame(temperature_entries).sort_values("time").reset_index(drop=True)

    temperature_map = {}
    temp_buffer = []
    g_idx = 0

    for t_entry in temp_df.itertuples():
        t_ts = t_entry.time
        t_val = t_entry.temperature
        temp_buffer.append(t_val)

        if g_idx < len(green_df):
            bottle_ts = green_df.iloc[g_idx]["time"]
            bottle_id = green_df.iloc[g_idx]["bottle"]

            if len(temp_buffer) == 3 and t_ts <= bottle_ts:
                temperature_map[bottle_id] = temp_buffer.copy()
                temp_buffer = []
                g_idx += 1

    if len(temperature_map) != len(green_df):
        print("Warnung: Temperaturzuordnung unvollständig!")

    temp_rows = []
    for bottle_id, temps in temperature_map.items():
        temp_rows.append({
            "bottle": bottle_id,
            "temperature_red": temps[0],
            "temperature_green": temps[1],
            "temperature_blue": temps[2],
        })

    df_temp = pd.DataFrame(temp_rows)
    df = pd.merge(df, df_temp, on="bottle", how="left")

    # Fehlende numerische Werte mit 0 füllen
    numeric_cols = df.select_dtypes(include=["float", "int"]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    if "drop_oscillation" in df.columns:
        df["drop_oscillation"] = df["drop_oscillation"].fillna("[]")

    # Klassifikationslabel wird NICHT automatisch gefüllt!
    # Falls "is_cracked" fehlt, bleibt NaN → wird später explizit behandelt!

    return df

# Modul-Test und CSV-Export
if __name__ == "__main__":
    df = load_data_as_dataframe()
    print(df.head())

    # Als CSV exportieren
    output_path = os.path.join(os.path.dirname(__file__), "data.csv")
    df.to_csv(output_path, index=False)
    print(f"CSV gespeichert unter: {output_path}")