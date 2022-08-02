import dash
import dash_bootstrap_components as dbc
import utils
import numpy as np
from app import variables
from dash import Input, Output, State, callback, MATCH, ALL, html
from resurfemg import helper_functions as hf
from scipy.signal import find_peaks


card_counter = 0


@callback(Output('preprocessing-original-container', 'children'),
          Input('load-preprocessing-div', 'data'))
def show_raw_data(data):
    emg_data = variables.get_emg()
    emg_frequency = variables.get_emg_freq()

    if emg_data is not None:
        children_emg = utils.add_emg_graphs(np.array(emg_data), emg_frequency)
    else:
        children_emg = []

    return children_emg


@callback(Output('preprocessing-processed-container', 'children'),
          Input('apply-pipeline-btn', 'n_clicks'),
          State('tail-cut-percent', 'value'),
          State('tail-cut-tolerance', 'value'),
          State('base-filter-low', 'value'),
          State('base-filter-high', 'value'),
          State('ecg-filter-select', 'value'),
          State('envelope-extraction-select', 'value'),
          State({"type": "emg-graph-switch", "index": ALL}, "value"))
def show_data(click, cut_percent, cut_tolerance, low_freq, high_freq, ecg_method, envelope_method, steps):
    emg_data = variables.get_emg()
    sample_rate = variables.get_emg_freq()

    if emg_data is not None:

        emg_cut = hf.bad_end_cutter_for_samples(emg_data, cut_percent, cut_tolerance)

        emg_data_filtered = hf.emg_bandpass_butter_sample(emg_cut,
                                                          low_freq,
                                                          high_freq,
                                                          sample_rate)

        emg_cut_final = hf.bad_end_cutter_for_samples(emg_data_filtered, 3, 5)

        emg_ecg, titles = apply_ecg_removal(ecg_method, emg_cut_final, sample_rate)

        emg_env = get_envelope(envelope_method, emg_ecg, sample_rate)

        children_emg = utils.add_emg_graphs(emg_env, sample_rate, titles)

    else:
        children_emg = []
    return children_emg


@callback(Output('pipeline-card-body', 'is_open'),
          Input('pipeline-switch', 'value'))
def show_raw_data(toggle_value):
    return toggle_value


@callback(
    Output({"type": "emg-graph-collapse", "index": MATCH}, "is_open"),
    Input({"type": "emg-graph-switch", "index": MATCH}, "value"),
    prevent_initial_call=True
)
def collapse_graph(toggle_value):
    return toggle_value


@callback(Output('custom-preprocessing-steps', 'children'),
          Input('add-steps-btn', 'n_clicks'),
          State('custom-preprocessing-steps', 'children'),
          prevent_initial_call=True)
def show_raw_data(click, previous_content):
    global card_counter

    card_counter += 1

    new_card = dbc.Card([
        dbc.CardHeader("New step"),
        dbc.Label("ECG removal method"),
        dbc.Select(
            id={"type": "emg-graph-switch", "index": str(card_counter)},
            options=[
                {"label": "ICA", "value": "1"},
                {"label": "Gating", "value": "2"},
                {"label": "None", "value": "3"},
            ],
            value="1"
        )
    ]
    )

    if previous_content is None:
        updated_content = new_card
    else:
        updated_content = previous_content + [new_card, html.P()]

    return updated_content


def apply_ecg_removal(removal_method: int, emg_signal, sample_rate):
    if removal_method == '1':
        emg_ica = hf.compute_ICA_two_comp(emg_signal)
        ecg_lead = emg_signal[0]
        emg_ecg = hf.pick_lowest_correlation_array(emg_ica, ecg_lead)
        titles = ["Filtered Track 2"]
    elif removal_method == '2':
        peak_width = 0.001
        peak_fraction = 0.40
        ecg_rms = hf.full_rolling_rms(emg_signal[0, :], 10)
        peak_height = peak_fraction * (max(ecg_rms) - min(ecg_rms))

        # A better identification of the QRS complex should be implemented in the library
        ecg_peaks, _ = find_peaks(ecg_rms, height=peak_height, width=peak_width * sample_rate)
        emg_ecg = hf.gating(emg_signal[2, :], ecg_peaks, method=0)
        titles = ["Filtered Track 2"]
    else:
        emg_ecg = emg_signal
        titles = None

    return emg_ecg, titles


def get_envelope(envelope_method: int, emg_signal, sample_rate):

    if envelope_method == '1':
        # I set the window here to 100ms, but this may be changed
        if emg_signal.ndim == 1:
            emg_env = hf.full_rolling_rms(abs(emg_signal), int(sample_rate / 10))
        else:
            emg_env = np.array([hf.full_rolling_rms(lead, int(sample_rate / 10)) for lead in abs(emg_signal)])
    elif envelope_method == '2':
        # THIS SHOULD BE CHANGED TO LOW PASS!
        emg_env = hf.emg_highpass_butter(abs(emg_signal), 150, sample_rate)
    else:
        emg_env = emg_signal

    return emg_env
