import dash
import dash_bootstrap_components as dbc
import json
import utils
import numpy as np
import pandas as pd
from app import variables
from dash import Input, Output, State, callback, MATCH, ALL, html, ctx, dcc
from definitions import ProcessTypology, EcgRemovalMethods, EnvelopeMethod
from resurfemg import helper_functions as hf
from scipy.signal import find_peaks

card_counter = 0
json_parameters = []


@callback(Output('preprocessing-original-container', 'children'),
          Input('load-preprocessing-div', 'data'))
def show_raw_data(data):
    global card_counter

    emg_data = variables.get_emg()
    emg_frequency = variables.get_emg_freq()

    if emg_data is not None:
        children_emg = utils.add_emg_graphs(np.array(emg_data), emg_frequency)
    else:
        children_emg = []

    return children_emg


@callback(Output('preprocessing-processed-container', 'children'),
          Output('download-data-btn', 'disabled'),
          Input('apply-pipeline-btn', 'n_clicks'),
          State('tail-cut-percent', 'value'),
          State('tail-cut-tolerance', 'value'),
          State('base-filter-low', 'value'),
          State('base-filter-high', 'value'),
          State('ecg-filter-select', 'value'),
          State('envelope-extraction-select', 'value'),
          State({"type": "additional-step-core", "index": ALL}, "id"),
          State({"type": "additional-step-type", "index": ALL}, "value"),
          State({"type": "additional-step-low", "index": ALL}, "value"),
          State({"type": "additional-step-low", "index": ALL}, "id"),
          State({"type": "additional-step-high", "index": ALL}, "value"),
          State({"type": "additional-step-high", "index": ALL}, "id"),
          State({"type": "additional-step-removal", "index": ALL}, "value"),
          State({"type": "additional-step-removal", "index": ALL}, "id"))
def show_data(click,
              cut_percent,
              cut_tolerance,
              low_freq,
              high_freq,
              ecg_method,
              envelope_method,
              additional_card,
              additional_steps,
              additional_low,
              additional_low_idx,
              additional_high,
              additional_high_idx,
              additional_rem,
              additional_rem_idx):

    save_data_enabled = False

    global json_parameters
    json_parameters.clear()

    emg_data = variables.get_emg()
    sample_rate = variables.get_emg_freq()

    if emg_data is not None:
        emg_cut = hf.bad_end_cutter_for_samples(emg_data, cut_percent, cut_tolerance)
        json_parameters.append(utils.build_cutter_params_json(1, cut_percent, cut_tolerance))

        emg_data_filtered = hf.emg_bandpass_butter_sample(emg_cut,
                                                          low_freq,
                                                          high_freq,
                                                          sample_rate)
        json_parameters.append(utils.build_bandpass_params_json(2, low_freq, high_freq))

        emg_cut_final = hf.bad_end_cutter_for_samples(emg_data_filtered, 3, 5)
        json_parameters.append(utils.build_cutter_params_json(3, 3, 5))

        emg_ecg, titles = apply_ecg_removal(ecg_method, emg_cut_final, sample_rate)
        json_parameters.append(utils.build_ecgfilt_params_json(4, EcgRemovalMethods(ecg_method)))

        new_step_emg = emg_ecg

        for n, card in enumerate(additional_card):
            card_id = card['index']
            step = additional_steps[n]
            if step == ProcessTypology.BAND_PASS.value:
                idx_low = utils.get_idx_dict_list(additional_low_idx, 'index', card_id)
                idx_high = utils.get_idx_dict_list(additional_high_idx, 'index', card_id)

                low_cut = additional_low[idx_low]
                high_cut = additional_high[idx_high]

                new_step_emg = hf.emg_bandpass_butter_sample(new_step_emg, low_cut, high_cut, sample_rate)
                json_parameters.append(utils.build_bandpass_params_json(n+5, low_cut, high_cut))

            elif step == ProcessTypology.HIGH_PASS.value:
                idx = utils.get_idx_dict_list(additional_low_idx, 'index', card_id)
                low_cut = additional_low[idx]

                new_step_emg = hf.emg_highpass_butter(new_step_emg, low_cut, sample_rate)
                json_parameters.append(utils.build_highpass_params_json(n + 5, low_cut))

            elif step == ProcessTypology.LOW_PASS.value:
                idx = utils.get_idx_dict_list(additional_high_idx, 'index', card_id)
                high_cut = additional_high[idx]

                # TODO: add function when it will be available in helper_functions
                # new_step_emg = hf.emg_lowpass_butter(new_step_emg, low_cut, sample_rate)
                #json_parameters.append(utils.build_lowpass_params_json(n + 5, high_cut))

            elif step == ProcessTypology.ECG_REMOVAL.value:
                idx = utils.get_idx_dict_list(additional_rem_idx, 'index', card_id)

                ecg_additional_method = additional_rem[idx]

                # at the moment we need to create a metrix with 3 leads to use the methods
                # the lead 0 is the  ecg lead, the other two are the same processed signal
                # if the matrix is still bi-dimensional, we use it

                if new_step_emg.ndim == 1:
                    tmp_matrix = [emg_cut_final[0, :], new_step_emg, new_step_emg]
                else:
                    tmp_matrix = new_step_emg

                new_step_emg, titles = apply_ecg_removal(ecg_additional_method, tmp_matrix, sample_rate)
                json_parameters.append(utils.build_ecgfilt_params_json(n + 5, EcgRemovalMethods(ecg_additional_method)))

        emg_env = get_envelope(envelope_method, new_step_emg, sample_rate)
        json_parameters.append(utils.build_envelope_params_json(len(json_parameters)+1, EnvelopeMethod(envelope_method)))

        variables.set_emg_processed(emg_env)

        children_emg = utils.add_emg_graphs(emg_env, sample_rate, titles)

        save_data_enabled = False
    else:
        children_emg = []
        save_data_enabled = True
    return children_emg, save_data_enabled


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
          Input({"type": "step-close-button", "index": ALL}, "n_clicks"),
          State('custom-preprocessing-steps', 'children'),
          prevent_initial_call=False)
def add_step(click, close, previous_content):
    global card_counter

    id_ctx = ctx.triggered_id
    # if the page is reloaded the steps are reset
    if id_ctx is None:
        card_counter = 0
        return []

    elif id_ctx == 'add-steps-btn':
        card_counter += 1
        new_card = new_step_body(card_counter)

        if previous_content is None:
            updated_content = new_card
        else:
            updated_content = previous_content + [new_card, html.P()]

    else:
        remove_idx = id_ctx['index']
        for n, el in enumerate(previous_content):
            if el['type'] == 'Card' and el['props']['id']['index'] == remove_idx:
                del previous_content[n + 1]
                previous_content.remove(el)

        updated_content = previous_content

    return updated_content


@callback(Output({"type": "additional-step-core", "index": MATCH}, "children"),
          Input({"type": "additional-step-type", "index": MATCH}, "value"),
          State({"type": "additional-step-core", "index": MATCH}, "id"),
          prevent_initial_call=True)
def get_body(selected_value, card_id):

    new_section = []
    if selected_value == ProcessTypology.BAND_PASS.value:
        new_section = utils.get_band_pass_layout({"type": "additional-step-low", "index": card_id['index']},
                                                 {"type": "additional-step-high", "index": card_id['index']})
    elif selected_value == ProcessTypology.HIGH_PASS.value:
        new_section = utils.get_high_pass_layout({"type": "additional-step-low", "index": card_id['index']})
    elif selected_value == ProcessTypology.LOW_PASS.value:
        new_section = utils.get_low_pass_layout({"type": "additional-step-high", "index": card_id['index']})
    elif selected_value == ProcessTypology.ECG_REMOVAL.value:
        new_section = utils.get_ecg_removal_layout({"type": "additional-step-removal", "index": card_id['index']})

    return new_section


@callback(Output('download-params', 'data'),
          Output('download-emg-processed', 'data'),
          Input('download-data-btn', 'n_clicks'),
          prevent_initial_call=True)
def download_data(click):

    params_file = dict(content=json.dumps(json_parameters), filename='parameters.txt')

    df = pd.DataFrame(variables.get_emg_processed().transpose())
    emg_file = dcc.send_data_frame(df.to_csv, 'emg.csv')

    return params_file, emg_file


def apply_ecg_removal(removal_method: int, emg_signal, sample_rate):
    if removal_method == EcgRemovalMethods.ICA.value:
        emg_ica = hf.compute_ICA_two_comp(emg_signal)
        ecg_lead = emg_signal[0]

        emg_ecg = hf.pick_lowest_correlation_array(emg_ica, ecg_lead)

        titles = ["Filtered Track 2"]
    elif removal_method == EcgRemovalMethods.GATING.value:
        # TODO: change with QRS identification when available in library
        peak_width = 0.001
        peak_fraction = 0.40
        ecg_rms = hf.full_rolling_rms(emg_signal[0, :], 10)
        peak_height = peak_fraction * (max(ecg_rms) - min(ecg_rms))
        ecg_peaks, _ = find_peaks(ecg_rms, height=peak_height, width=peak_width * sample_rate)

        emg_ecg = hf.gating(emg_signal[2, :], ecg_peaks, method=0)

        titles = ["Filtered Track 2"]
    else:
        emg_ecg = emg_signal
        titles = None

    return emg_ecg, titles


def get_envelope(envelope_method: int, emg_signal, sample_rate):
    if envelope_method == EnvelopeMethod.RMS.value:
        # I set the window here to 100ms, but this may be changed
        if emg_signal.ndim == 1:
            emg_env = hf.full_rolling_rms(abs(emg_signal), int(sample_rate / 10))
        else:
            emg_env = np.array([hf.full_rolling_rms(lead, int(sample_rate / 10)) for lead in abs(emg_signal)])
    elif envelope_method == EnvelopeMethod.FILTERING.value:
        # THIS SHOULD BE CHANGED TO LOW PASS!
        emg_env = hf.emg_highpass_butter(abs(emg_signal), 150, sample_rate)
    else:
        emg_env = emg_signal

    return emg_env


def new_step_body(index):
    new_card = dbc.Card([
        dbc.CardHeader([
            html.Button(
                html.I(className="fas fa-times", style={'color': 'red'}),
                className="ml-auto close",
                id={"type": "step-close-button", "index": str(index)},
                style={'border': 'none',
                       'background': 'transparent'}
            ),
            dbc.Label("Additional step")
        ]),
        dbc.Label("Step type"),
        dbc.Select(
            id={"type": "additional-step-type", "index": str(index)},
            options=[
                {"label": "", "value": "0"},
                {"label": "Band-pass filter", "value": ProcessTypology.BAND_PASS.value},
                {"label": "High-pass filter", "value": ProcessTypology.HIGH_PASS.value},
                {"label": "Low-pass filter", "value": ProcessTypology.LOW_PASS.value},
                {"label": "ECG removal", "value": ProcessTypology.ECG_REMOVAL.value},
            ],
            value="0"
        ),
        html.Div([], id={"type": "additional-step-core", "index": str(card_counter)})
    ],
        id={"type": "additional-step-card", "index": str(card_counter)})

    return new_card
