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
        
        dbc.Tabs(
            [
                dbc.Tab(label="Time corrected", tab_id="adjusted_signal"),
                dbc.Tab(label="Original signal", tab_id="original_signal"),
                
            ],
            id="tabs",
            active_tab="original_signal",
        ),
        html.Div(id="tab-content", className="p-4"),

        dbc.Col([html.Div([
                dcc.Input(
                    id='time-shift-numb',
                    type="number",
                    placeholder="Time shift number",
                    value=0,
                    style={'color': 'green'},
                ),
            ],
                style={'textAlign': 'right'}),
            ], width=2,),
        
        dbc.Col([
                html.Div('EMG time shift, milliseconds', style={'textAlign': 'left'})
                ], width=2, style={"color": "green"}),

            
        dbc.Col([html.Div([
                dcc.Input(
                    id='emg-lead-numb',
                    type="number",
                    placeholder="EMG lead number",
                    value=0,
                    min=0,
                    max= 25,
                    style={'color': 'purple'}
                ),
            ],
                style={'textAlign': 'right'}),
            ], width=2),
        
        dbc.Col([
                html.Div('EMG lead number', style={'textAlign': 'left'})
                ], width=2, style={"color": "purple"}),

        
        dbc.Col([html.Div([
                dcc.Input(
                    id='vent-lead-numb',
                    type="number",
                    placeholder="Vent lead number",
                    value=1,
                    min=0,
                    max=10,
                ),
            ],
                style={'textAlign': 'right'}),
            ], width=2),
        
        dbc.Col([
                html.Div('Vent lead number', style={'textAlign': 'left'})
                ], width=2),
       
       
    ]
)




if __name__ == "__main__":
    layout.run_server(debug=True, port=8888)

#])
