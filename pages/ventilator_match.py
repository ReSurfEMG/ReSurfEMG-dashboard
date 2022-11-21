import dash
import dash_uploader as du
import dash_bootstrap_components as dbc
from dash import html, dcc

import time
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output


dash.register_page(__name__, path='/ventilator-match')

layout = dbc.Container(
    [
        dcc.Store(id="store"),
        html.H1("Dynamically rendered tab content for ventilator and EMG (in progress)"),
        html.Hr(),
        dbc.Button(
            "Regenerate graphs",
            color="primary",
            id="button",
            className="mb-3",
        ),
        dbc.Tabs(
            [
                dbc.Tab(label="Original signal", tab_id="original_signal"),
                dbc.Tab(label="Time corrected", tab_id="adjusted_signal"),
            ],
            id="tabs",
            active_tab="original_signal",
        ),
        html.Div(id="tab-content", className="p-4"),
    ]
)


def render_tab_content(active_tab, data):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab and data is not None:
        if active_tab == "original_signal":
            return dcc.Graph(figure=data["original_signal"])
        elif active_tab == "adjusted_signal":
            return dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=data["hist_1"]), width=6),
                    dbc.Col(dcc.Graph(figure=data["hist_2"]), width=6),
                ]
            )
    return "No tab selected"



if __name__ == "__main__":
    layout.run_server(debug=True, port=8888)

#])
