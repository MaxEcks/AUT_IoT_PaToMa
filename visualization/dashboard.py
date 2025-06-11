import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from visualization.data_formatter import load_data_as_dataframe

# --- Daten vorbereiten ---
df_raw = load_data_as_dataframe()

df_raw["vibration_values"] = df_raw["drop_oscillation"]

# Nur Flaschen mit gültiger Zeitreihe anzeigen (mind. 50 Werte)
df = df_raw[df_raw["vibration_values"].apply(lambda x: isinstance(x, list) and len(x) >= 50)].copy()

# Sicherheitsabbruch, wenn keine brauchbaren Daten vorhanden sind
if df.empty:
    raise ValueError("Keine Flaschen mit gültigen vibration_values vorhanden!")

# --- Dash App Setup ---
app = dash.Dash(__name__)
app.title = "Flaschenklassifikation"

app.layout = html.Div([
    html.H1("Vibrationsanalyse - Flaschendefekte", style={"textAlign": "center"}),

    html.Label("Flasche auswählen:"),
    dcc.Dropdown(
        id="bottle-dropdown",
        options=[{"label": str(b), "value": b} for b in df["bottle"]],
        value=df["bottle"].iloc[0]
    ),

    html.Div(id="status-box", style={"marginTop": "10px", "fontWeight": "bold"}),

    dcc.Graph(id="vibration-plot", style={"height": "500px"})
])

# --- Callback für Plot und Statusanzeige ---
@app.callback(
    Output("vibration-plot", "figure"),
    Output("status-box", "children"),
    Input("bottle-dropdown", "value")
)
def update_plot(selected_bottle):
    row = df[df["bottle"] == selected_bottle].iloc[0]
    values = row["vibration_values"]
    is_cracked = row["is_cracked"]

    fig = px.line(
        x=list(range(len(values))),
        y=values,
        labels={"x": "Messpunkt", "y": "Amplitude"},
        title=f"Schwingungsverlauf Vereinzelung Flasche Nr. {selected_bottle}"
    )

    cracked_text = "Flasche ist GESPRUNGEN!" if is_cracked else "Flasche ist INTAKT."
    return fig, cracked_text

# --- App starten ---
if __name__ == "__main__":
    app.run(debug=True)
