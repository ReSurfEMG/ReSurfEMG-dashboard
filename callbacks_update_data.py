import os
from dash import Input, Output, callback, ctx, State, html, ALL, callback_context
from app import app, variables
import resurfemg.converter_functions as cv
from pathlib import Path
from dash.exceptions import PreventUpdate
from definitions import (PATH_BTN, FILE_PATH_INPUT, STORED_CWD, CWD,
                         CWD_FILES, CONFIRM_CENTERED, MODAL_CENTERED,
                         EMG_OPEN_CENTERED, VENT_OPEN_CENTERED, PARENT_DIR,
                         LISTED_FILES, VENT_FREQUENCY_DIV, VENT_SAMPLING_FREQUENCY, EMG_FREQUENCY_DIV,
                         EMG_SAMPLING_FREQUENCY)

# variable to keep track of which upload button has been clicked
clicked_input_btn = None


@callback(Output(EMG_FREQUENCY_DIV, 'data'),
          Input(EMG_SAMPLING_FREQUENCY, 'value'))
def update_emg_frequency(freq, ):
    variables.set_emg_freq(freq)
    return 'set'


@callback(Output(VENT_FREQUENCY_DIV, 'data'),
          Input(VENT_SAMPLING_FREQUENCY, 'value'))
def update_ventilator_frequency(freq):
    variables.set_ventilator_freq(freq)
    return 'set'


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
    State(FILE_PATH_INPUT, 'value'),
    Input(STORED_CWD, 'data'),
    Input(PARENT_DIR, 'n_clicks'),
    Input(CWD, 'children'),
    Input(PATH_BTN, 'n_clicks'),
    prevent_initial_call=True)
def get_parent_directory_emg(path_input, stored_cwd, n_clicks, currentdir, path_btn):
    triggered_id = callback_context.triggered_id
    path = None

    if triggered_id == STORED_CWD:
        path = stored_cwd
    elif triggered_id == PATH_BTN:
        path = Path(path_input).parent.as_posix()
    elif triggered_id == PARENT_DIR:
        path = Path(currentdir).parent.as_posix()

    return path if os.path.exists(path) or os.path.isfile(path) else 'Path not valid'


@app.callback(
    Output(CWD_FILES, 'children'),
    Input(CWD, 'children'))
def list_cwd_files(cwd):
    path = Path(cwd)

    cwd_files = []
    if path.is_dir():
        files = sorted(os.listdir(path), key=str.lower)
        for i, file in enumerate(files):
            filepath = Path(file)
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
