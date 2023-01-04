import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from definitions import (ComputedFeatures, FEATURES_COMPUTE_BTN, FEATURES_LOADING)

from definitions import (EMG_FILENAME_FEATURES, FEATURES_EMG_GRAPH_DIV,
                         LOAD_FEATURES_DIV, FEATURES_SELECT_LEAD,
                         FEATURES_SELECT_COMPUTATION, FEATURES_TABLE)

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

select_computation_card = dbc.Card([
    dbc.CardHeader("Select the computation"),
    dbc.CardBody([
        dbc.Label("Breath identification method"),
        dbc.Select(
            id=FEATURES_SELECT_COMPUTATION,
            options=[
                {"label": "Entropy", "value": 1},
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
            html.Div(id=FEATURES_EMG_GRAPH_DIV)
        ])
    ]),
    dbc.Row([
        html.Div([
            html.Button(
                className="fas fa-play",
                id=FEATURES_COMPUTE_BTN,
                style={'color': 'green',
                       'background': 'transparent',
                       'border': 'none',
                       'font-size': '34px'}
            ),
            dbc.Label("Compute features"),
            dbc.Tooltip(
                "Compute features",
                id="tooltip-apply-pipeline",
                target="apply-pipeline-btn",
            )
        ],
            style={'text-align': 'center'}
        ),
    ]),
    dbc.Row([
        html.P(),
        html.Hr(), html.Br(), html.Br(), html.Br(),
        html.H1('Computed features', style={'textAlign': 'center'})
    ]),
    dbc.Row([
        dbc.Col([
            html.P(),
            select_computation_card
        ], width=2),
        dbc.Col([
            dcc.Loading(
                id=FEATURES_LOADING,
                type="default",
                children=dash_table.DataTable(
                    [{feature: '' for feature in ComputedFeatures.features_list}],
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        # all three widths are needed
                        'minWidth': '10%', 'width': '10%', 'maxWidth': '10%',
                    },
                    style_header={'textAlign': 'center'},
                    id=FEATURES_TABLE
                )
            )
        ],
            style={'textAlign': 'center',
                   'margin-left': '0px'})
    ]),
])
