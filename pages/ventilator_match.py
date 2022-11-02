import dash
import dash_uploader as du
import dash_bootstrap_components as dbc
from dash import html, dcc


dash.register_page(__name__, path='/ventilator-match')



layout = html.Div([
    html.P(),
    dbc.Row([
        html.Span([

            
        ]),
        
    ],
        style={'text-align': 'center'}
    ),

    html.P(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Switch(
                        id="timeline-switch",
                        label="Custom time alignment",
                        value=False
                    ),
                ], "Timeline", style={'text-align': 'center'}
                ),
                dbc.Collapse([
                    html.P(),
                    dbc.Col([
                        dbc.Row([
                            dbc.Alert(
                                "The file is not valid",
                                id="alert-invalid-file",
                                dismissable=True,
                                is_open=False,
                                duration=4000,
                                color="danger",
                                style={'width': 'auto',
                                       'left': '18px'}
                            ),
                            dcc.Upload(
                                className="fas fa-upload",
                                id='upload-processing-params',
                                accept='application/json',
                                style={'color': 'blue',
                                       'background': 'transparent',
                                       'border': 'none',
                                       'font-size': '34px'},
                            ),
                            dbc.Tooltip(
                                "Upload the parameters file",
                                id="tooltip-upload-params",
                                target="upload-processing-params",
                            )
                        ],
                            style={'text-align': 'center'}),
                        html.Div("Upload the parameters file",
                                 style={'text-align': 'center'}),

                      
                        html.P(),
                        html.Div([], id='custom-preprocessing-steps'),
                        html.Div([], id='test-preprocessing-steps'),

                        html.Div([
                            html.Button(
                                className="fas fa-plus-circle",
                                id='add-steps-btn',
                                style={'color': 'blue',
                                       'background': 'transparent',
                                       'border': 'none',
                                       'font-size': '34px'}),
                            dbc.Tooltip(
                                "Apply time difference",
                                id="apply-time-difference",
                                target="add-time-btn",
                            )
                        ],
                            style={'text-align': 'center'}
                        ),
                        html.P(),
                    ]),
                    html.P(),
                    html.Div([
                        html.Button(
                            className="fas fa-play",
                            id='apply-pipeline-btn',
                            style={'color': 'green',
                                   'background': 'transparent',
                                   'border': 'none',
                                   'font-size': '34px'}
                        ),
                        dbc.Tooltip(
                            "Apply processing",
                            id="tooltip-apply-pipeline",
                            target="apply-pipeline-btn",
                        )
                    ],
                        style={'text-align': 'center'}
                    ),
                    html.P(),

                ],
                    id='pipeline-card-body',
                    is_open=False),
            ])
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Signals and ventilator", style={'text-align': 'center'}),
                html.Div(id='signals_and_ventilator-container'),
            ]),

        ], width=9, id='processed-signals-column'),
    
])
])
