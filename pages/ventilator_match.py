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
        
        

        dbc.Col([
                html.Div('EMG time shift (μs)', style={'textAlign': 'left'})
                ], width=2, style={"color": "green"}),
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
                html.Div('EMG lead displayed', style={'textAlign': 'left'})
                ], width=2, style={"color": "purple"}),           
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
                html.Div('Vent lead displayed', style={'textAlign': 'left'})
                ], width=2),
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
        
        dcc.Graph(id= 'overlaid'),
        dbc.Button('Save time corrected data', id='saver-button',
                           style={'background': 'blue',
                                  'border': 'transparent'}),
        html.Div(id='hidden-div'),
       
       
    ]
)




if __name__ == "__main__":
    layout.run_server(debug=True, port=8888)

#])
