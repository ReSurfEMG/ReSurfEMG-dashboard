from typing import List

from dash import Input, Output, callback, dcc, ctx, State, html, ALL, callback_context
from app import app, variables
from resurfemg import helper_functions as hf
import numpy as np
import plotly.graph_objects as go
import utils
from pathlib import Path
from dash.exceptions import PreventUpdate
from definitions import ComputedFeatures, FEATURES_COMPUTE_BTN
from definitions import (EMG_FILENAME_FEATURES, FEATURES_EMG_GRAPH, FEATURES_EMG_GRAPH_DIV,
                         FEATURES_SELECT_LEAD, LOAD_FEATURES_DIV, FEATURES_TABLE, FEATURES_SELECT_COMPUTATION)


class Breath:

    def __init__(self,
                 start_sample: int = None,
                 stop_sample: int = None,
                 amplitude: np.array = None):

        self.start_sample = start_sample
        self.stop_sample = stop_sample
        self.amplitude = amplitude


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
          State(FEATURES_EMG_GRAPH, 'figure'),
          Input(FEATURES_SELECT_COMPUTATION, 'value'),
          Input(FEATURES_COMPUTE_BTN, 'n_clicks'),
          prevent_initial_call=True)
def show_graph(slidebar_stat, method_stat, lead_n, figure, method_input, btn_input):
    """
    When the slide bar is updated by the user, or the computation method is changed
    computes the features and updates the table
    """
    
    data = variables.get_emg_processed()
    time_array = utils.get_time_array(data[int(lead_n)].shape[0], variables.get_emg_freq())

    if slidebar_stat is None or 'xaxis.range' not in slidebar_stat:
        start_sample = 0
        stop_sample = time_array.shape[0]
    else:
        start_sample = (np.abs(time_array - slidebar_stat['xaxis.range'][0])).argmin()
        stop_sample = (np.abs(time_array - slidebar_stat['xaxis.range'][1])).argmin()

    breaths = get_breaths(data[int(lead_n)], start_sample, stop_sample, 1)

    features = [{ComputedFeatures.BREATHS_COUNT: len(breaths),
                 ComputedFeatures.MAX_AMPLITUDE: '',
                 ComputedFeatures.BASELINE_AMPLITUDE: '',
                 ComputedFeatures.TONIC_AMPLITUDE: '',
                 ComputedFeatures.AUC: '',
                 ComputedFeatures.RISE_TIME: '',
                 ComputedFeatures.ACTIVITY_DURATION: ''}]
    #
    # figure['data'].append({
    #     'x': time_array[200:],
    #     'y': tmp,
    #     'type': 'scatter',
    #     'mode': 'lines',
    #     'name': 'a_level'
    # })
    #
    # figure_updated = figure

    return features


def get_slider_graph(emg: np.array, time: np.array):
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


def get_features_table(emg: np.array, start_sample: int, stop_sample: int):
    """
    Produces a table with the features computed over the selected signal.
        Args:
            emg: a numpy array containing a single lead of the emg signal to plot
            start_sample: number of the sample where the signal to be computed starts
            stop_sample: number of the sample where the signal to be computed stops

    """

    return []


def get_breaths(emg: np.array, start_sample: int, stop_sample: int, method: int) -> List[Breath]:
    """
    Produces a list of breaths from the time window in the signal.
        Args:
            emg: a numpy array containing a single lead of the emg signal to analyse
            start_sample: number of the sample where the signal to be computed starts
            stop_sample: number of the sample where the signal to be computed stops
            method: the method used to compute the breaths

    """
    big_list = np.round_(emg[start_sample:stop_sample], decimals=5)
    slice_length = 100

    index_hold = []
    for slice in sliceIterator(big_list, slice_length):
        entropy_index = hf.entropical(slice)
        index_hold.append(entropy_index)

    high_decision_cutoff = 0.9 * ((np.max(index_hold)) - (np.min(index_hold))) + np.min(index_hold)
    decision_cutoff = 0.5 * ((np.max(index_hold)) - (np.min(index_hold))) + np.min(index_hold)

    rms_rolled = hf.vect_naive_rolling_rms(index_hold, 100)  # so rms is rms entropy

    hi = np.array(hf.zero_one_for_jumps_base(rms_rolled, high_decision_cutoff))
    lo = np.array(hf.zero_one_for_jumps_base(rms_rolled, decision_cutoff))

    rhi = hf.ranges_of(hi)
    rlo = hf.ranges_of(lo)

    keep = hf.intersections(rlo, rhi)

    seven_line = np.zeros(len(rms_rolled))
    for seven_range in keep:
        seven_line[seven_range.to_slice()] = 7


    zippy = zip(seven_line, seven_line[1:])
    breath_indeces = []
    for val in enumerate(zippy):
        if val[1][0] < val[1][1]:
            breath_indeces.append(val[0])

        grouped_breaths = np.split(emg[start_sample:stop_sample], breath_indeces)
        grouped_entropy = np.split(rms_rolled, breath_indeces)
        grouped_breaths = grouped_breaths[1:]
        grouped_entropy = grouped_entropy[1:]

    return grouped_breaths


def sliceIterator(lst, sliceLen):
    for i in range(len(lst) - sliceLen + 1):
        yield lst[i:i + sliceLen]

