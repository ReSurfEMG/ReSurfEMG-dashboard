from typing import List

from dash import Input, Output, callback, dcc, ctx, State, html, ALL, callback_context
from app import app, variables
from resurfemg import helper_functions as hf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import utils
from pathlib import Path
from dash.exceptions import PreventUpdate
from definitions import ComputedFeatures, FEATURES_COMPUTE_BTN, FEATURES_DOWNLOAD_BTN, FEATURES_DOWNLOAD_DCC
from definitions import (EMG_FILENAME_FEATURES, FEATURES_EMG_GRAPH, FEATURES_EMG_GRAPH_DIV,
                         FEATURES_SELECT_LEAD, LOAD_FEATURES_DIV, FEATURES_TABLE, FEATURES_SELECT_COMPUTATION)

features_df = None


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

    global features_df

    data = variables.get_emg_processed()
    frequency = variables.get_emg_freq()
    time_array = utils.get_time_array(data[int(lead_n)].shape[0], frequency)

    if slidebar_stat is None or 'xaxis.range' not in slidebar_stat:
        start_sample = 0
        stop_sample = time_array.shape[0]
    else:
        start_sample = (np.abs(time_array - slidebar_stat['xaxis.range'][0])).argmin()
        stop_sample = (np.abs(time_array - slidebar_stat['xaxis.range'][1])).argmin()

    breaths = get_breaths(data[int(lead_n)], start_sample, stop_sample, 1)

    features_df = create_features_dataframe(breaths)

    features = [{ComputedFeatures.BREATHS_COUNT: len(breaths),
                 ComputedFeatures.MAX_AMPLITUDE: str(round(features_df['maxima'].mean(), 2)) + ' ± ' + str(
                     round(features_df['maxima'].std(), 2)),
                 ComputedFeatures.BASELINE_AMPLITUDE: '',
                 ComputedFeatures.TONIC_AMPLITUDE: '',
                 ComputedFeatures.AUC: str(round(features_df['auc'].mean(), 2)) + ' ± ' + str(
                     round(features_df['auc'].std(), 2)),
                 ComputedFeatures.RISE_TIME: '',
                 ComputedFeatures.ACTIVITY_DURATION: str(round(features_df['length'].mean(), 2)) + ' ± ' + str(
                     round(features_df['length'].std(), 2)), }]

    return features


# download the csv file with the features
@callback(Output(FEATURES_DOWNLOAD_DCC, 'data'),
          Input(FEATURES_DOWNLOAD_BTN, 'n_clicks'),
          prevent_initial_call=True)
def download_data(click):
    global features_df

    if features_df is not None:
        features_file = dcc.send_data_frame(features_df.to_csv, 'features.csv')
        return features_file


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

    breaths = [Breath(start_sample=int(keep[i].start),
                      stop_sample=int(keep[i + 1].start),
                      amplitude=emg[int(keep[i].start):int(keep[i + 1].start)])
               for i, element in enumerate(keep[:-1])]

    return breaths


def get_breaths_length(breaths: List[Breath]) -> List[int]:
    """
    Computes and returns the numpy array containing the length of each breath
    of the breaths list
        Args:
            breaths: list of the breaths

    """
    length = [(breath.stop_sample - breath.start_sample) for breath in breaths]

    return length


def get_breaths_maxima(breaths: List[Breath]) -> List[int]:
    """
    Computes and returns the numpy array containing the maximum
    of each breath of the breaths list
        Args:
            breaths: list of the breaths

    """
    maxima = [hf.find_peak_in_breath(abs(breath.amplitude), 0, len(breath.amplitude))[1]
              for breath in breaths]

    return maxima


def get_breaths_auc(breaths: List[Breath]) -> List[float]:
    """
    Computes and returns the numpy array containing the area under the curve
    of each breath of the breaths list
        Args:
            breaths: list of the breaths

    """

    auc = [hf.area_under_curve(
        abs(breath.amplitude),
        0,
        (len(breath.amplitude) - 1),
        end_curve=70,
        smooth_algorithm='mid_savgol'
    )
        for breath in breaths]

    return auc


def create_features_dataframe(breaths: List[Breath]) -> pd.DataFrame:
    """
    Computes and returns the numpy array containing the area under the curve
    of each breath of the breaths list
        Args:
            breaths: list of the breaths
    """
    start_samples = []
    stop_samples = []
    for breath in breaths:
        start_samples.append(breath.start_sample)
        stop_samples.append(breath.stop_sample)

    length = get_breaths_length(breaths)
    maxima = get_breaths_maxima(breaths)
    auc = get_breaths_auc(breaths)

    d = {'start_samples': start_samples,
         'stop_samples': stop_samples,
         'length': length,
         'maxima': maxima,
         'auc': auc}

    df = pd.DataFrame(d)

    df.index.name = 'breath_number'

    return df


def sliceIterator(lst, sliceLen):
    for i in range(len(lst) - sliceLen + 1):
        yield lst[i:i + sliceLen]
