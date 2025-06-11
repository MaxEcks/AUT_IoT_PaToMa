import os
from tinydb import TinyDB
import pandas as pd
import json
import math

def load_data_as_dataframe():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.normpath(os.path.join(current_dir, "..", "database", "database.json"))

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Datei nicht gefunden: {json_path}")

    db = TinyDB(json_path)
    raw_data = db.storage.read()
    rows = []

    for topic_key, topic_data in raw_data.items():
        for entry_id, entry in topic_data.items():
            payload = entry.get("payload", {})

            if isinstance(payload, dict) and "raw" in payload:
                try:
                    payload = json.loads(payload["raw"])
                except:
                    continue

            row = {}

            # Flaschen-ID
            bottle = payload.get("bottle")
            if bottle is None:
                continue  # Nur Flaschen-Daten sind relevant

            try:
                row["bottle"] = int(bottle)
            except:
                row["bottle"] = bottle  # Fallback, falls Umwandlung fehlschlägt

            # Temperatur
            if "temperature_C" in payload:
                row["temperature"] = payload["temperature_C"]

            # Füllstand und Vibration nach Farbe
            if "fill_level_grams" in payload:
                color = topic_key.split("_")[-1]
                row[f"fill_level_{color}"] = payload["fill_level_grams"]

            if "vibration-index" in payload:
                color = topic_key.split("_")[-1]
                row[f"vibration_index_{color}"] = payload["vibration-index"]

            # Endgewicht
            if "final_weight" in payload:
                row["final_weight"] = payload["final_weight"]

            # Drop-Oszillation (bei Vereinzelung)
            if "drop_oscillation" in payload:
                raw_list = payload["drop_oscillation"]
                try:
                    floats = [float(v) for v in raw_list]
                    clean = [v for v in floats if not math.isnan(v)]
                    row["drop_oscillation"] = clean
                except:
                    row["drop_oscillation"] = []

            # Flasche defekt?
            if "is_cracked" in payload:
                row["is_cracked"] = bool(int(payload["is_cracked"]))

            rows.append(row)

    # DataFrame erstellen
    df = pd.DataFrame(rows)

    # Gruppierung: alle Einträge pro "bottle" zusammenfassen
    if "bottle" not in df.columns:
        raise ValueError("Keine Spalte 'bottle' gefunden!")

    df = df.groupby("bottle", dropna=False).first().reset_index()

    # Fehlende numerische Werte durch 0 ersetzen
    numeric_cols = df.select_dtypes(include=["float", "int"]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Nicht-numerische Spalten (z. B. drop_oscillation) optional füllen
    df["drop_oscillation"] = df["drop_oscillation"].fillna("[]")
    df["is_cracked"] = df["is_cracked"].fillna(False)

    return df

# Modul-Test
if __name__ == "__main__":
    df = load_data_as_dataframe()
    print(df.head())

    # Als CSV exportieren
    output_path = os.path.join(os.path.dirname(__file__), "output.csv")
    df.to_csv(output_path, index=False)
    print(f"\nCSV gespeichert unter: {output_path}")

    print("\n=== Drop-Oszillationen in df_raw ===")
    print(df[["bottle", "drop_oscillation"]].tail(10))  # oder .sample(10)
