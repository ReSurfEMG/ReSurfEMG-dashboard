import dash_bootstrap_components as dbc
import resurfemg.helper_functions as hf
import numpy as np
import plotly.graph_objects as go
import trace_updater
from app import app
from dash import dcc, html
from definitions import ProcessTypology, EcgRemovalMethods, EnvelopeMethod
from plotly_resampler import FigureResampler
from scipy.signal import find_peaks
from typing import Dict
from uuid import uuid4

graph_dict_raw: Dict[str, FigureResampler] = {}

# colors
colors = {
    'white': '#FFFFFF',
    'text': '#091D58',
    'blue1': '#063446',  # dark blue
    'blue2': '#0e749b',
    'blue3': '#15b3f0',
    'blue4': '#E4F3F9',  # light blue
    'yellow1': '#f0d515'
}


# build the layout for emg graphs
def add_emg_graphs(emg_data, frequency, titles=None):
    if emg_data is None:
        return []

    graphs = []

    if emg_data.ndim == 1:
        leads_n = 1
        time_array = get_time_array(emg_data.shape[0], frequency)
    else:
        leads_n = emg_data.shape[0]
        time_array = get_time_array(emg_data.shape[1], frequency)

    for i in range(leads_n):

        uid = 'emg' + str(i) + '-graph' + str(uuid4())

        if leads_n == 1:
            y = emg_data
        else:
            y = emg_data[i]

        if titles is None:
            fig_title = "EMG Track " + str(i)
        else:
            fig_title = titles[i]

        fig = FigureResampler(go.Figure())
        fig.add_trace(go.Scatter(),
                      hf_x=time_array,
                      hf_y=y)

        fig.update_layout(
            xaxis_title="Time [s]",
            yaxis_title="micro Volts",
            legend_title="Legend Title"
        )

        graphs.append(
            dbc.Switch(
                id={"type": "emg-graph-switch", "index": uid},
                label=fig_title,
                value=True
            ),
        )
        graphs.append(
            dbc.Collapse([
                dcc.Graph(
                    id={"type": "dynamic-graph", "index": uid},
                    figure=fig
                )
            ],
                id={"type": "emg-graph-collapse", "index": uid},
                is_open=True
            )
        )

        graphs.append(trace_updater.TraceUpdater(
            id={"type": "dynamic-updater", "index": uid},
            gdID=uid))

        graph_dict_raw[uid] = fig

    return graphs


# build the layout for ventilator graphs
def add_ventilator_graphs(vent_data, frequency):
    if vent_data is None:
        return []

    graphs = []

    for i in range(vent_data.shape[0]):
        uid = 'vent' + str(i) + '-graph'

        length = vent_data.shape[vent_data.ndim - 1]

        time_array = get_time_array(length, frequency)

        fig = FigureResampler(go.Figure())
        fig.add_trace(go.Scatter(),
                      hf_x=time_array,
                      hf_y=vent_data[i])

        fig.update_layout(
            title="Ventilator Track " + str(i),
            xaxis_title="Time [s]",
            legend_title="Legend Title"
        )

        graphs.append(dcc.Graph(
            id={"type": "dynamic-graph", "index": uid},
            figure=fig
        ))

        graphs.append(trace_updater.TraceUpdater(
            id={"type": "dynamic-updater", "index": uid},
            gdID=uid))

        graph_dict_raw[uid] = fig

    return graphs


# get the time array, computed from the sampling rate
def get_time_array(data_size, frequency):
    time_array = np.arange(0, data_size / frequency, 1 / frequency)

    return time_array


# function needed to update graphs using plotly_resampler
def get_dict(graph_id_dict, relayoutdata):
    return graph_dict_raw.get(graph_id_dict["index"]).construct_update_data(relayoutdata)


# get the layout for the band pass filter card
def get_band_pass_layout(id_low, id_high):
    layout = [
        dbc.Row([
            dbc.Col([
                html.P("Low cut frequency"),
                dcc.Input(
                    id=id_low,
                    type="number",
                    placeholder="low cut",
                    value=3
                )
            ]),
            dbc.Col([
                html.P("High cut frequency"),
                dcc.Input(
                    id=id_high,
                    type="number",
                    placeholder="high cut",
                    value=450
                )
            ])
        ])
    ]

    return layout


# get the layout for the high pass filter card
def get_high_pass_layout(id_low):
    layout = [
        dbc.Col([
            html.P("Low cut frequency"),
            dcc.Input(
                id=id_low,
                type="number",
                placeholder="low cut",
                value=3
            )
        ])
    ]

    return layout


# get the layout for the low pass filter card
def get_low_pass_layout(id_low):
    layout = [
        dbc.Col([
            html.P("High cut frequency"),
            dcc.Input(
                id=id_low,
                type="number",
                placeholder="high cut",
                value=450
            )
        ])
    ]

    return layout


# get the layout for the ecg removal filter card
def get_ecg_removal_layout(id_removal):
    layout = [
        dbc.Label("ECG removal method"),
        dbc.Select(
            id=id_removal,
            options=[
                {"label": "ICA", "value": EcgRemovalMethods.ICA.value},
                {"label": "Gating", "value": EcgRemovalMethods.GATING.value},
                {"label": "None", "value": EcgRemovalMethods.NONE.value},
            ],
            value="1"
        )
    ]

    return layout


# get the layout fot the new processing step card
def get_new_step_body(index):
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
        html.Div([], id={"type": "additional-step-core", "index": str(index)})
    ],
        id={"type": "additional-step-card", "index": str(index)})

    return new_card


# get the index of the dict containing the key-value
# in a list of dicts
def get_idx_dict_list(dict_list, key, value):
    idx = next((i for i, item in enumerate(dict_list)
                if item[key] == value), None)

    return idx


# compute the envelope, using the method selected
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


# apply the ecg removal, using the method selected
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


# build the json containing the params for the cutter
def build_cutter_params_json(step_number: int, percentage: int, tolerance: int):
    data = {
        'step_number': step_number,
        'step_type': 'cut',
        'percentage': percentage,
        'tolerance': tolerance
    }

    return data


# build the json containing the params for the band pass filter
def build_bandpass_params_json(step_number: int, low_frequency: int, high_frequency: int):
    data = {
        'step_number': step_number,
        'step_type': 'bandpass',
        'low_frequency': low_frequency,
        'high_frequency': high_frequency
    }

    return data


# build the json containing the params for the high pass filter
def build_highpass_params_json(step_number: int, cut_frequency: int):
    data = {
        'step_number': step_number,
        'step_type': 'highpass',
        'cut_frequency': cut_frequency
    }

    return data


# build the json containing the params for the low pass filter
def build_lowpass_params_json(step_number: int, cut_frequency: int):
    data = {
        'step_number': step_number,
        'step_type': 'lowpass',
        'cut_frequency': cut_frequency
    }

    return data


# build the json containing the params for the ecg removal
def build_ecgfilt_params_json(step_number: int, method: EcgRemovalMethods):
    data = {
        'step_number': step_number,
        'step_type': 'ecg_removal',
        'method': method.name
    }

    return data


# build the json containing the params for the envelope extraction
def build_envelope_params_json(step_number: int, method: EnvelopeMethod):
    data = {
        'step_number': step_number,
        'step_type': 'envelope',
        'method': method.name
    }

    return data
