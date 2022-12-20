import os

import dash
import dash_bootstrap_components as dbc
from definitions import (PATH_BTN, FILE_PATH_INPUT, STORED_CWD, CWD,
                         CWD_FILES, CONFIRM_CENTERED, MODAL_CENTERED,
                         EMG_OPEN_CENTERED, VENT_OPEN_CENTERED, PARENT_DIR,
                         EMG_SAMPLING_FREQUENCY, VENT_SAMPLING_FREQUENCY,
                         VENT_FREQUENCY_DIV, EMG_FREQUENCY_DIV, VENT_FILE_UPDATED, EMG_FILE_UPDATED)
from dash import html, dcc

dash.register_page(__name__, path='/')

modal_dialog = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Close"), close_button=True),
                dbc.ModalBody([
                    dbc.Row([
                        html.H1('Select file'),
                        dbc.Col([
                            dbc.Button('GO TO', id=PATH_BTN)
                        ], width=2, className="d-grid gap-2"),
                        dbc.Col([
                            dcc.Input(id=FILE_PATH_INPUT, placeholder='Insert the path to the file')
                        ], className="d-grid gap-2")
                    ]),
                    dbc.Row([
                        html.P()
                    ]),
                    dbc.Row([
                        dcc.Store(id=STORED_CWD, data=os.getcwd()),
                        html.H5(html.B(html.A("⬆️ Parent directory", href='#', id=PARENT_DIR))),
                        html.H3([html.Code(os.getcwd(), id=CWD)]),
                        html.Br(), html.Br(),
                        html.Div(id=CWD_FILES)
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
            scrollable=True
        ),
    ]
)


def layout():
    return html.Div([

        html.H1('Upload Data'),
        modal_dialog,
        dbc.Row([
            dbc.Col([html.Div([
                dbc.Button("UPLOAD EMG DATA", id=EMG_OPEN_CENTERED),
            ],
                className="d-grid gap-2"),

            ], width=6),

            dbc.Col([html.Div([
                dcc.Input(
                    id=EMG_SAMPLING_FREQUENCY,
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
            html.P(),
            html.Div(id=EMG_FILE_UPDATED),
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
                    id=VENT_SAMPLING_FREQUENCY,
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
            html.P(),
            html.Div(id=VENT_FILE_UPDATED),
        ]),
        # the following elements are only needed
        # to provide outputs to the callbacks
        html.Div(id=EMG_FREQUENCY_DIV),
        html.Div(id=VENT_FREQUENCY_DIV)
    ])
