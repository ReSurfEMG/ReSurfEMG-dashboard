import os
from dash import Input, Output, callback, ctx, MATCH, State, html, ALL, callback_context
import dash_uploader as du
from app import app, variables
import utils
import numpy as np
import resurfemg.converter_functions as cv
from pathlib import Path
from dash.exceptions import PreventUpdate
from definitions import (PATH_BTN, FILE_PATH_INPUT, STORED_CWD, CWD,
                         CWD_FILES, CONFIRM_CENTERED, MODAL_CENTERED,
                         EMG_OPEN_CENTERED, VENT_OPEN_CENTERED, PARENT_DIR,
                         LISTED_FILES)

du.configure_upload(app, r"C:\tmp\Uploads", use_upload_id=True)

# variable to keep track of which upload button has been clicked
clicked_input_btn = None


@callback(Output('emg-frequency-div', 'data'),
          Input('emg-sample-freq', 'value'))
def update_emg_frequency(freq, ):
    variables.set_emg_freq(freq)
    return 'set'


@callback(Output('ventilator-frequency-div', 'data'),
          Input('ventilator-sample-freq', 'value'))
def update_ventilator_frequency(freq):
    variables.set_ventilator_freq(freq)
    return 'set'


@callback(Output('emg-graphs-container', 'children'),
          Output('emg-header', 'hidden'),
          Output('emg-filename', 'children'),
          Input('hidden-div', 'data'),
          Input('emg-delete-button', 'n_clicks'))
def show_raw_data(emg_data, delete):
    emg_data = variables.get_emg()
    hidden = True

    trigger_id = ctx.triggered_id
    filename = variables.get_emg_filename()

    if trigger_id == 'emg-delete-button':
        variables.set_emg(None)
        children_emg = []
    else:
        if emg_data is not None:
            emg_frequency = variables.get_emg_freq()
            children_emg = utils.add_emg_graphs(np.array(emg_data), emg_frequency)
            hidden = False
        else:
            children_emg = []

    return children_emg, hidden, filename


@callback(Output('ventilator-graphs-container', 'children'),
          Output('ventilator-header', 'hidden'),
          Output('ventilator-filename', 'children'),
          Input('hidden-div', 'data'),
          Input('ventilator-delete-button', 'n_clicks'))
def show_raw_data(ventilator_data, delete):
    ventilator_data = variables.get_ventilator()
    hidden = True

    trigger_id = ctx.triggered_id
    filename = variables.get_ventilator_filename()

    if trigger_id == 'ventilator-delete-button':
        variables.set_ventilator(None)
        children_vent = []
    else:
        if ventilator_data is not None:
            ventilator_frequency = variables.get_ventilator_freq()
            children_vent = utils.add_ventilator_graphs(np.array(ventilator_data), ventilator_frequency)
            hidden = False
        else:
            children_vent = []

    return children_vent, hidden, filename


@app.callback(
    Output({"type": "dynamic-updater", "index": MATCH}, "updateData"),
    Input({"type": "dynamic-graph", "index": MATCH}, "relayoutData"),
    State({"type": "dynamic-graph", "index": MATCH}, "id"),
    prevent_initial_call=True,
)
def update_figure(relayoutdata: dict, graph_id_dict: dict):
    return utils.get_dict(graph_id_dict, relayoutdata)


@app.callback(
    Output(MODAL_CENTERED, 'is_open'),
    [Input(EMG_OPEN_CENTERED, 'n_clicks'), Input(VENT_OPEN_CENTERED, 'n_clicks'), Input(CONFIRM_CENTERED, 'n_clicks')],
    [State(MODAL_CENTERED, 'is_open'), State(STORED_CWD, 'data')],
    prevent_initial_call=True
)
def toggle_modal(n1, n2, n3, is_open, selected_file):
    global clicked_input_btn

    if ctx.triggered_id in [EMG_OPEN_CENTERED, VENT_OPEN_CENTERED]:
        clicked_input_btn = ctx.triggered_id

    if ctx.triggered_id == CONFIRM_CENTERED:
        data = cv.poly5unpad(selected_file)
        if clicked_input_btn == EMG_OPEN_CENTERED:
            variables.set_emg(data)
            variables.set_emg_filename('File: ' + selected_file)
        elif clicked_input_btn == VENT_OPEN_CENTERED:
            variables.set_ventilator(data)
            variables.set_ventilator_filename('File: ' + selected_file)
    return not is_open


@app.callback(
    Output(CWD, 'children'),
    Input(STORED_CWD, 'data'),
    Input(PARENT_DIR, 'n_clicks'),
    Input(CWD, 'children'),
    prevent_initial_call=True)
def get_parent_directory_emg(stored_cwd, n_clicks, currentdir):
    triggered_id = callback_context.triggered_id
    if triggered_id == STORED_CWD:
        return stored_cwd
    parent = Path(currentdir).parent.as_posix()
    return parent


@app.callback(
    Output(CWD_FILES, 'children'),
    State(FILE_PATH_INPUT, 'value'),
    Input(CWD, 'children'),
    Input(PATH_BTN, 'n_clicks')
    )
def list_cwd_files(path_input, cwd, path_btn):
    trigger = ctx.triggered_id
    manual_input = False
    if trigger is not None and trigger == PATH_BTN:
        path = Path(path_input)
        manual_input = True
    else:
        path = Path(cwd)

    cwd_files = []
    if path.is_dir():
        files = sorted(os.listdir(path), key=str.lower)
        for i, file in enumerate(files):
            filepath = Path(file)
            if manual_input:
                full_path = path
            else:
                full_path = os.path.join(cwd, filepath.as_posix())

            is_dir = Path(full_path).is_dir()
            link = html.A([
                html.Span(
                file, id={'type': LISTED_FILES, 'index': i},
                title=full_path,
                style={'fontWeight': 'bold'} if is_dir else {}
            )], href='#')
            prepend = '' if not is_dir else '📂'
            cwd_files.append(prepend)
            cwd_files.append(link)
            cwd_files.append(html.Br())

    return cwd_files


@app.callback(
    Output(STORED_CWD, 'data'),
    Input({'type': LISTED_FILES, 'index': ALL}, 'n_clicks'),
    State({'type': LISTED_FILES, 'index': ALL}, 'children'),
    State({'type': LISTED_FILES, 'index': ALL}, 'title'),
    State(CWD, 'children'))
def store_clicked_file(n_clicks, href, title, cwd):
    if not n_clicks or set(n_clicks) == {None}:
        raise PreventUpdate
    index = ctx.triggered_id['index']
    return title[index]
