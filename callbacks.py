import os
from dash import Input, Output, callback, ctx, MATCH, State, html, ALL
import dash_uploader as du
from app import app, variables
import utils
import numpy as np
import resurfemg.converter_functions as cv
from pathlib import Path
from dash.exceptions import PreventUpdate

du.configure_upload(app, r"C:\tmp\Uploads", use_upload_id=True)


@du.callback(
    output=Output("emg-uploaded-div", "data"),
    id="upload-emg-data",
)
def parse_emg(status):
    emg_data = cv.poly5unpad(status.latest_file.__str__())
    variables.set_emg(emg_data)

    filename = 'File: ' + status.latest_file.name
    variables.set_emg_filename(filename)

    # children = utils.add_emg_graphs(emg_data)
    return 'set'


@du.callback(
    output=Output('ventilator-uploaded-div', 'data'),
    id='upload-ventilator-data',
)
def parse_vent(status):
    vent_data = cv.poly5unpad(status.latest_file.__str__())
    variables.set_ventilator(vent_data)

    filename = 'File: ' + status.latest_file.name
    variables.set_ventilator_filename(filename)

    # children = utils.add_ventilator_graphs(vent_data)
    print('vent uploaded')
    return 'set'


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
    Output("modal-centered", "is_open"),
    [Input("open-centered", "n_clicks"), Input("confirm-centered", "n_clicks")],
    [State("modal-centered", "is_open"), State({'type': 'stored_cwd', 'index': 'emg'}, 'data')],
    prevent_initial_call=True
)
def toggle_modal(n1, n2, is_open, selected_file):
    if ctx.triggered_id == "confirm-centered":
        emg_data = cv.poly5unpad(selected_file)
        variables.set_emg(emg_data)

        filename = 'File: ' + selected_file
        variables.set_emg_filename(filename)
    return not is_open


@app.callback(
    Output("modal-centered-vent", "is_open"),
    [Input("open-centered-vent", "n_clicks"), Input("confirm-centered-vent", "n_clicks")],
    [State("modal-centered-vent", "is_open"), State({'type': 'stored_cwd', 'index': 'vent'}, 'data')],
    prevent_initial_call=True
)
def toggle_modal(n1, n2, is_open, selected_file):
    if ctx.triggered_id == "confirm-centered-vent":
        ventilator_data = cv.poly5unpad(selected_file)
        variables.set_ventilator(ventilator_data)

        filename = 'File: ' + selected_file
        variables.set_ventilator_filename(filename)
    return not is_open


@app.callback(
    Output({'type': 'cwd', 'index': MATCH}, 'children'),
    Input({'type': 'stored_cwd', 'index': MATCH}, 'data'),
    Input({'type': 'parent_dir', 'index': MATCH}, 'n_clicks'),
    Input({'type': 'cwd', 'index': MATCH}, 'children'),
    prevent_initial_call=True)
def get_parent_directory(stored_cwd, n_clicks, currentdir):
    triggered_id = ctx.triggered_id
    if triggered_id['type'] == 'stored_cwd':
        return stored_cwd
    parent = Path(currentdir).parent.as_posix()
    return parent


@app.callback(
    Output({'type': 'cwd_files', 'index': MATCH}, 'children'),
    Input({'type': 'cwd', 'index': MATCH}, 'children'))
def list_cwd_files(cwd):
    path = Path(cwd)
    cwd_files = []
    if path.is_dir():
        files = sorted(os.listdir(path), key=str.lower)
        for i, file in enumerate(files):
            filepath = Path(file)
            full_path=os.path.join(cwd, filepath.as_posix())
            is_dir = Path(full_path).is_dir()
            link = html.A([
                html.Span(
                file, id={'type': 'listed_file', 'index': i},
                title=full_path,
                style={'fontWeight': 'bold'} if is_dir else {}
            )], href='#')
            prepend = '' if not is_dir else '📂'
            cwd_files.append(prepend)
            cwd_files.append(link)
            cwd_files.append(html.Br())
    return cwd_files


@app.callback(
    Output({'type': 'stored_cwd', 'index': 'emg'}, 'data'),
    Input({'type': 'listed_file', 'index': ALL}, 'n_clicks'),
    State({'type': 'listed_file', 'index': ALL}, 'children'),
    State({'type': 'listed_file', 'index': ALL}, 'title'),
    State({'type': 'cwd', 'index': 'emg'}, 'children'))
def store_clicked_file(n_clicks, href, title, cwd):
    if not n_clicks or set(n_clicks) == {None}:
        raise PreventUpdate
    index = ctx.triggered_id['index']
    return title[index]



@app.callback(
    Output({'type': 'stored_cwd', 'index': 'vent'}, 'data'),
    Input({'type': 'listed_file', 'index': ALL}, 'n_clicks'),
    State({'type': 'listed_file', 'index': ALL}, 'children'),
    State({'type': 'listed_file', 'index': ALL}, 'title'),
    State({'type': 'cwd', 'index': 'vent'}, 'children'))
def store_clicked_file(n_clicks, href, title, cwd):
    if not n_clicks or set(n_clicks) == {None}:
        raise PreventUpdate
    index = ctx.triggered_id['index']
    return title[index]