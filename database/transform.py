"""
@file data_formatter.py
@brief Extrahiert und aggregiert alle MQTT-Daten, die sich auf Flaschen beziehen

Dieses Modul lädt gezielt Daten mit Flaschenbezug aus der TinyDB-Datenbank ("database.json")
und erstellt ein "tidy" Pandas DataFrame mit einer Zeile pro Flasche.

Berücksichtigt werden nur die Topics:
- "dispenser_red", "dispenser_green", "dispenser_blue"
- "final_weight"
- "drop_oscillation"
- "ground_truth"

Sensorwerte wie Füllstand, Vibration und Klassifikationslabel (`is_cracked`) werden extrahiert
und nach Flasche aggregiert.
"""

import os
import json
import math
import pandas as pd
from tinydb import TinyDB

def load_data_as_dataframe():
    """
    @brief Lädt alle Sensordaten mit Flaschenbezug aus TinyDB und gibt sie als tidy DataFrame zurück

    Dabei werden nur Topics berücksichtigt, die ein "bottle"-Feld enthalten:
    - dispenser_red, dispenser_green, dispenser_blue
    - final_weight
    - drop_oscillation
    - ground_truth

    @return Pandas DataFrame mit aggregierten Werten pro Flasche
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

            row = {}

            if "bottle" not in payload:
                continue  # Zeile überspringen, wenn keine Flaschen-ID vorhanden

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