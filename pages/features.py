import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from definitions import(FEATURES_SELECT_LEAD)

from definitions import (EMG_FILENAME_FEATURES, FEATURES_EMG_GRAPH_DIV,
                         LOAD_FEATURES_DIV)

dash.register_page(__name__, path='/features')

select_lead_card = dbc.Card([
    dbc.CardHeader("Select the lead"),
    dbc.CardBody([
        dbc.Select(
            id=FEATURES_SELECT_LEAD,
            options=[
            ]
        )
    ])
])

layout = html.Div([
    html.P(),
    html.Div(id=EMG_FILENAME_FEATURES),
    html.Div(id=LOAD_FEATURES_DIV),
    dbc.Row([
        dbc.Col([
            html.P(),
            select_lead_card
        ], width=2),
        dbc.Col([
            html.Div(id=FEATURES_EMG_GRAPH_DIV),
            html.Div(id='test-component')
        ])
    ])



])
