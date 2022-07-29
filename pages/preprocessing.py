import dash
import dash_uploader as du
import dash_bootstrap_components as dbc
from dash import html, dcc

dash.register_page(__name__, path='/preprocessing')

tailcut_card = dbc.Card([
    dbc.CardHeader("Cut tail"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.P("Tail portion [%]"),
                dcc.Input(
                    id='tail-cut-percent',
                    type="number",
                    placeholder="%",
                    value=3
                )
            ]),
            dbc.Col([
                html.P("Tolerance on variation"),
                dcc.Input(
                    id='tail-cut-tolerance',
                    type="number",
                    placeholder="%",
                    value=5
                )
            ])
        ])
    ])
])

baseline_card = dbc.Card([
    dbc.CardHeader("Baseline removal"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.P("Low cut frequency"),
                dcc.Input(
                    id='base-filter-low',
                    type="number",
                    placeholder="low cut",
                    value=3
                )
            ]),
            dbc.Col([
                html.P("High cut frequency"),
                dcc.Input(
                    id='base-filter-high',
                    type="number",
                    placeholder="high cut",
                    value=450
                )
            ])
        ])
    ])
])

ecg_card = dbc.Card([
    dbc.CardHeader("ECG removal"),
    dbc.Label("ECG removal method"),
    dbc.Select(
        id="ecg-filter-select",
        options=[
            {"label": "ICA", "value": "1"},
            {"label": "None", "value": "2"},
        ],
        value=1
    )
])

envelope_card = dbc.Card([
    dbc.CardHeader("Envelope extraction")
])

layout = html.Div([
    dbc.Card([
        dbc.CardHeader([
            dbc.Switch(
                id="pipeline-switch",
                label="Custom pipeline",
                value=False
            ),
        ], "Processing pipeline", style={'text-align': 'center'}
        ),
        dbc.Collapse([
            html.P(),
            dbc.Row([
                dbc.Col([tailcut_card], width=3),
                dbc.Col([baseline_card], width=3),
                dbc.Col([ecg_card], width=3),
                dbc.Col([envelope_card], width=3)
            ]),
            html.P(),
            dbc.Row([dbc.Button('Apply',
                       id='apply-pipeline-btn')
                      ], style={'align': 'center'})

        ],
            id='pipeline-card-body',
            is_open=False),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='preprocessing-processed-container')
        ], width=6),
        dbc.Col([
            html.Div(id='preprocessing-original-container')
        ], width=6),
        html.Div(id='load-preprocessing-div')
    ]),

])
