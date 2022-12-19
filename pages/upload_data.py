import os

import dash
import dash_bootstrap_components as dbc
from definitions import (PATH_BTN, FILE_PATH_INPUT, STORED_CWD, CWD,
                         CWD_FILES, CONFIRM_CENTERED, MODAL_CENTERED,
                         EMG_OPEN_CENTERED, VENT_OPEN_CENTERED, PARENT_DIR)
from dash import html, dcc

dash.register_page(__name__, path='/')

modal_emg = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Close"), close_button=True),
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(id=PATH_BTN)
                        ]),
                        dbc.Col([
                            dcc.Input(id=FILE_PATH_INPUT)
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col(lg=1, sm=1, md=1),
                        dbc.Col([
                            dcc.Store(id=STORED_CWD, data=os.getcwd()),
                            html.H1('Select EMG file'),
                            html.Hr(), html.Br(), html.Br(), html.Br(),
                            html.H5(html.B(html.A("⬆️ Parent directory", href='#', id=PARENT_DIR))),
                            html.H3([html.Code(os.getcwd(), id=CWD)]),
                            html.Br(), html.Br(),
                            html.Div(id=CWD_FILES),
                        ], lg=10, sm=11, md=10)
                    ])]),
                dbc.ModalFooter(
                    dbc.Button(
                        "Confirm",
                        id=CONFIRM_CENTERED,
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id=MODAL_CENTERED,
            centered=True,
            is_open=False,
            backdrop=False,
        ),
    ]
)


def layout():
    return html.Div([

        html.H1('Upload Data'),
        modal_emg,
        dbc.Row([
            dbc.Col([html.Div([
                dbc.Button("UPLOAD EMG DATA", id=EMG_OPEN_CENTERED),
            ],
                className="d-grid gap-2"),

            ], width=6),

            dbc.Col([html.Div([
                dcc.Input(
                    id='emg-sample-freq',
                    type="number",
                    placeholder="EMG sampling frequency",
                    value=2048
                ),
            ],
                style={'textAlign': 'right'}),
            ], width=2),

            dbc.Col([
                html.Div('EMG sampling frequency', style={'textAlign': 'left'})
            ], width=2),
        ]),

        dbc.Row([html.P()]),
        dbc.Row([
            dbc.Col([html.Div([
                dbc.Button("UPLOAD VENTILATOR DATA", id=VENT_OPEN_CENTERED),
            ],
                className="d-grid gap-2"),

            ], width=6),

            dbc.Col([html.Div([


                 dcc.Input(
                     id='ventilator-sample-freq',
                     type="number",
                     placeholder="Ventilator sampling frequency",
                     value=100
                 ),
            ],
                style={'textAlign': 'right'}),
            ], width=2),

            dbc.Col([
                html.Div('Ventilator sampling frequency', style={'textAlign': 'left'})
            ], width=2),
        ]),
        html.Div(children=[
            html.H1(id='out', children='')
        ]),
        # the following elements are only needed
        # to provide outputs to the callbacks
        html.Div(id='emg-uploaded-div'),
        html.Div(id='ventilator-uploaded-div'),
        html.Div(id='emg-frequency-div'),
        html.Div(id='ventilator-frequency-div'),
    ])
