import dash
import utils
import numpy as np
from app import variables
from dash import Input, Output, State, callback, ctx
from resurfemg import helper_functions as hf


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
          State('envelope-extraction-select', 'value'))
def show_raw_data(click, cut_percent, cut_tolerance, low_freq, high_freq, ecg_method, envelope_method):
    print(ecg_method)
    emg_data = variables.get_emg()
    sample_rate = variables.get_emg_freq()
    id_trigger = ctx.triggered_id

    if emg_data is not None:
        emg_frequency = variables.get_emg_freq()
        # if id_trigger == 'apply-baseline-btn':

        emg_cut = hf.bad_end_cutter_for_samples(emg_data, cut_percent, cut_tolerance)

        emg_data_filtered = hf.emg_bandpass_butter_sample(emg_cut,
                                                          low_freq,
                                                          high_freq,
                                                          emg_frequency)

        emg_cut_final = hf.bad_end_cutter_for_samples(emg_data_filtered, 3, 5)

        if ecg_method == '1':
            emg_ica = hf.compute_ICA_two_comp(emg_cut_final)
            ecg_lead = emg_cut_final[0]
            emg_ecg = hf.pick_lowest_correlation_array(emg_ica, ecg_lead)
        else:
            emg_ecg = emg_cut_final

        if envelope_method == '1':
            # I set the window here to 100ms, but this may be changed
            emg_env = hf.full_rolling_rms(abs(emg_ecg), int(sample_rate / 10))
        elif envelope_method == '2':
            # THIS SHOULD BE CHANGED TO LOW PASS!
            emg_env = hf.emg_highpass_butter(abs(emg_ecg), 150, sample_rate)
        else:
            emg_env = emg_ecg

        children_emg = utils.add_emg_graphs(emg_env, emg_frequency)
    # else:
    #    children_emg = utils.add_emg_graphs(np.array(emg_data), emg_frequency)
    else:
        children_emg = []

    return children_emg


@callback(Output('pipeline-card-body', 'is_open'),
          Input('pipeline-switch', 'value'))
def show_raw_data(toggle_value):
    return toggle_value
