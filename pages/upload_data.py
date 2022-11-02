import os

import dash
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import html, dcc

dash.register_page(__name__, path='/')

modal_emg = html.Div(
    [
        dbc.Button("Open", id="open-centered"),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Close"), close_button=True),
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col(lg=1, sm=1, md=1),
                        dbc.Col([
                            dcc.Store(id={'type': 'stored_cwd', 'index': 'emg'}, data=os.getcwd()),
                            html.H1('Select EMG file'),
                            html.Hr(), html.Br(), html.Br(), html.Br(),
                            html.H5(html.B(html.A("⬆️ Parent directory", href='#', id={'type': 'parent_dir', 'index': 'emg'}))),
                            html.H3([html.Code(os.getcwd(), id=({'type': 'cwd', 'index': 'emg'}))]),
                            html.Br(), html.Br(),
                            html.Div(id={'type': 'cwd_files', 'index': 'emg'}),
                        ], lg=10, sm=11, md=10)
                    ])]),
                dbc.ModalFooter(
                    dbc.Button(
                        "Confirm",
                        id="confirm-centered",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="modal-centered",
            centered=True,
            is_open=False,
        ),
    ]
)

modal_vent = html.Div(
    [
        dbc.Button("Open", id="open-centered-vent"),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Close"), close_button=True),
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col(lg=1, sm=1, md=1),
                        dbc.Col([
                            dcc.Store(id={'type': 'stored_cwd', 'index': 'vent'}, data=os.getcwd()),
                            html.H1('Select EMG file'),
                            html.Hr(), html.Br(), html.Br(), html.Br(),
                            html.H5(html.B(html.A("⬆️ Parent directory", href='#', id={'type': 'parent_dir', 'index': 'vent'}))),
                            html.H3([html.Code(os.getcwd(), id=({'type': 'cwd', 'index': 'vent'}))]),
                            html.Br(), html.Br(),
                            html.Div(id={'type': 'cwd_files', 'index': 'vent'}),
                        ], lg=10, sm=11, md=10)
                    ])]),
                dbc.ModalFooter(
                    dbc.Button(
                        "Confirm",
                        id="confirm-centered-vent",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="modal-centered-vent",
            centered=True,
            is_open=False,
        ),
    ]
)

def layout():
    return html.Div([

        html.H1('Upload Data'),
        dbc.Row([
            dbc.Col([html.Div([
                du.Upload(
                    id='upload-emg-data',
                    text='Click or Drag and Drop Here to upload EMG data!',
                    text_completed='Uploaded: ',
                    filetypes=['Poly5'],
                ),
            ]),

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

        dbc.Row([
            dbc.Col([html.Div([
                du.Upload(
                    id='upload-ventilator-data',
                    text='Click or Drag and Drop Here to upload Ventilator data!',
                    text_completed='Uploaded: ',
                    filetypes=['Poly5'],
                ),
            ]),

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
        modal_emg,
        modal_vent
    ])
