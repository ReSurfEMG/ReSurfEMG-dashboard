import numpy
from dash import Input, Output, callback, dcc, ctx, State, html, ALL, callback_context
from app import app, variables
import numpy as np
import plotly.graph_objects as go
import utils
from pathlib import Path
from dash.exceptions import PreventUpdate
from definitions import (EMG_FILENAME_FEATURES, FEATURES_EMG_GRAPH, FEATURES_EMG_GRAPH_DIV,
                         FEATURES_SELECT_LEAD, LOAD_FEATURES_DIV, FEATURES_TABLE, FEATURES_SELECT_COMPUTATION)


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


@callback(Output(FEATURES_TABLE, 'data'),
          State(FEATURES_EMG_GRAPH, 'relayoutData'),
          State(FEATURES_SELECT_COMPUTATION, 'value'),
          State(FEATURES_SELECT_LEAD, 'value'),
          Input(FEATURES_EMG_GRAPH, 'relayoutData'),
          Input(FEATURES_SELECT_COMPUTATION, 'value'),
          prevent_initial_call=True)
def show_graph(slidebar_stat, method_stat, lead_n, slidebar_input, method_input):

    """
    When the slide bar is updated by the user, or the computation method is changed
    computes the features and updates the table
    """
    trigger = ctx.triggered_id

    data = variables.get_emg_processed()
    time_array = utils.get_time_array(data[int(lead_n)].shape[0], variables.get_emg_freq())

    if trigger == FEATURES_EMG_GRAPH and (slidebar_input is not None or 'xaxis.range' not in slidebar_input):
        start_sample = 0
        stop_sample = time_array.shape[0]
    else:
        start_sample = (np.abs(time_array - slidebar_stat['xaxis.range'][0])).argmin()
        stop_sample = (np.abs(time_array - slidebar_stat['xaxis.range'][1])).argmin()

    features = [{'MAX AMPLITUDE': start_sample,
                  'BASELINE APLITUDE': stop_sample,
                  'TONIC AMPLITUDE': start_sample,
                  'AUC': stop_sample,
                  'RISE TIME': start_sample,
                  'ACTIVITY DURATION': stop_sample}]

    return features


def get_slider_graph(emg: numpy.array, time: numpy.array):

    """
    Produces a line plot with a range slider selector of the signal specified in the emg argument, with the
    time basis specified in the time argument.
        Args:
            emg: a numpy array containing a single lead of the emg signal to plot
            time: a numpy array containing the time basis for the emg signal

    """

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


def get_features_table(emg: numpy.array, start_sample: int, stop_sample: int):

    """
    Produces a table with the features computed over the selected signal.
        Args:
            emg: a numpy array containing a single lead of the emg signal to plot
            start_sample: number of the sample where the signal to be computed starts
            stop_sample: number of the sample where the signal to be computed stops

    """

    return []
