from dash import Input, Output, callback, ctx, MATCH, State
import dash_uploader as du
from app import app, variables
import utils
import numpy as np
import resurfemg.converter_functions as cv


du.configure_upload(app, r"C:\tmp\Uploads", use_upload_id=True)


@du.callback(
    output=Output('emg-uploaded-div', 'data'),
    id='upload-emg-data',
)
def parse_emg(status):
    emg_data = cv.poly5unpad(status[0])
    variables.set_emg(emg_data)

    filename = 'File: ' + status[0].split("\\")[-1]
    variables.set_emg_filename(filename)

    # children = utils.add_emg_graphs(emg_data)
    return 'set'


@du.callback(
    output=Output('ventilator-uploaded-div', 'data'),
    id='upload-ventilator-data',
)
def parse_vent(status):
    vent_data = cv.poly5unpad(status[0])
    variables.set_ventilator(vent_data)

    filename = 'File: ' + status[0].split("\\")[-1]
    variables.set_ventilator_filename(filename)

    # children = utils.add_ventilator_graphs(vent_data)
    print('vent uploaded')
    return 'set'


@callback(Output('emg-frequency-div', 'data'),
          Input('emg-sample-freq', 'value'))
def update_emg_frequency(freq,):
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
