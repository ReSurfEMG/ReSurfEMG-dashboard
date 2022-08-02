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
            {"label": "Gating", "value": "2"},
            {"label": "None", "value": "3"},
        ],
        value="1"
    )
])

envelope_card = dbc.Card([
    dbc.CardHeader("Envelope extraction"),
    dbc.Label("Envelope computation method"),
    dbc.Select(
        id="envelope-extraction-select",
        options=[
            {"label": "RMS", "value": "1"},
            {"label": "Filtering", "value": "2"},
            {"label": "None", "value": "3"},
        ],
        value="1"
    )
])

layout = html.Div([
    html.P(),
    dbc.Row([
        dbc.Col([
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
                    dbc.Col([
                        tailcut_card,
                        html.P(),
                        baseline_card,
                        html.P(),
                        ecg_card,
                        html.P(),
                        html.Div([], id='custom-preprocessing-steps'),
                        html.Div([
                            dbc.Button('Add steps', id='add-steps-btn')
                        ],
                            style={'text-align': 'center'}
                        ),
                        html.P(),
                        envelope_card
                    ]),
                    html.P(),
                    html.Div([dbc.Button('Apply', id='apply-pipeline-btn', size="lg", className="me-1")],
                             style={'text-align': 'center'}),
                    html.P(),

                ],
                    id='pipeline-card-body',
                    is_open=False),
            ])
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Processed signals", style={'text-align': 'center'}),
                html.Div(id='preprocessing-processed-container'),
            ]),

        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Raw signals", style={'text-align': 'center'}),
                html.Div(id='preprocessing-original-container'),
            ]),
        ], width=4),
        html.Div(id='load-preprocessing-div')
    ]),

])
