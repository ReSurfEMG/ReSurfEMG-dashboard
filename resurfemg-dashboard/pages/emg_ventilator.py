import dash
from dash import html, dcc
import trace_updater


dash.register_page(__name__, path='/emg_ventilator')


layout = html.Div([
    dcc.Graph(
        id={"type": "dynamic-graph", "index": "emgventilator"}
    ),
    trace_updater.TraceUpdater(
            id={"type": "dynamic-updater", "index": "emgventilator"},
            gdID="emgventilator"),
    html.Div(id='emgventilator-secret-div')
])
