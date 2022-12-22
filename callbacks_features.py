import numpy
from dash import Input, Output, callback, dcc, ctx, State, html, ALL, callback_context
from app import app, variables
import numpy as np
import plotly.graph_objects as go
import utils
from pathlib import Path
from dash.exceptions import PreventUpdate
from definitions import (EMG_FILENAME_FEATURES, FEATURES_EMG_GRAPH, FEATURES_EMG_GRAPH_DIV,
                         FEATURES_SELECT_LEAD, LOAD_FEATURES_DIV)


# on loading add the PAGE
@callback(Output(EMG_FILENAME_FEATURES, 'children'),
          Input(LOAD_FEATURES_DIV, 'data'))
def show_filename(data):
    """
    When loading the page, the path of the file selected is displayed in th EMG_FILENAME_FEATURES
    """
    filename = variables.get_emg_filename()

    return filename if filename is not None else []


@callback(Output(FEATURES_SELECT_LEAD, 'options'),
          Input(LOAD_FEATURES_DIV, 'data'))
def show_filename(data):
    """
    When loading the page, the dropdown menu for selecting the lead is populated
    """
    data = variables.get_emg_processed()

    if data is not None:
        options = [{'label': 'Lead ' + str(n), 'value': n} for n in range(data.shape[0])]
        return options
    return []


@callback(Output(FEATURES_EMG_GRAPH_DIV, 'children'),
          Input(FEATURES_SELECT_LEAD, 'value'))
def show_graph(value):
    """
    When loading the page, the path of the file selected is displayed in th EMG_FILENAME_FEATURES
    """
    data = variables.get_emg_processed()

    if data is not None and value is not None:
        lead = data[int(value)]
        time_array = utils.get_time_array(lead.shape[0], variables.get_emg_freq())

        graph = get_slider_graph(lead, time_array)
        return graph

    return []


@callback(Output('test-component', 'children'),
          State(FEATURES_SELECT_LEAD, 'value'),
          Input(FEATURES_EMG_GRAPH, 'relayoutData'),
          prevent_initial_call=True)
def show_graph(lead_n, slidebar):

    """
    When the slide bar is updated by the user, gets the new starting and stopping time
    """

    if slidebar is None or 'xaxis.range' not in slidebar:
        return []

    data = variables.get_emg_processed()
    time_array = utils.get_time_array(data[int(lead_n)].shape[0], variables.get_emg_freq())

    start_sample = (np.abs(time_array - slidebar['xaxis.range'][0])).argmin()
    stop_sample = (np.abs(time_array - slidebar['xaxis.range'][1])).argmin()

    return ['start: ' + str(start_sample) + ' ' + str(time_array[start_sample]) + ' stop: ' + str(stop_sample) + ' ' + str(time_array[stop_sample])]


def get_slider_graph(emg: numpy.array, time: numpy.array):
    traces = [{
        'x': time,
        'y': emg,
        'type': 'scatter',
        'mode': 'lines',
        'name': 'a_level'
    }]

    figure = go.Figure(
                data=traces,
                layout=go.Layout(
                    xaxis={
                        'rangeslider': {'visible': True}
                    },
                )
            )
    figure.update_layout(
        title='EMG lead',
        xaxis_title='Time [s]',
        yaxis_title='micro Volts',
    )

    graph = [
        dcc.Graph(
            id=FEATURES_EMG_GRAPH,
            figure=figure
        )
    ]

    return graph
