import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import trace_updater
from app import app
from dash import dcc, html
from definitions import ProcessTypology, EcgRemovalMethods, EnvelopeMethod
from plotly_resampler import FigureResampler
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


def blank_fig(text=None):
    """Creates a blank figure."""
    fig = go.Figure(data=go.Scatter(x=[], y=[]))
    fig.update_layout(
        paper_bgcolor=colors['blue4'],
        plot_bgcolor=colors['blue4'],
        width=300,
        height=300)

    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    if text is not None:
        fig.update_layout(
            width=300,
            height=300,
            annotations=[
                {
                    "text": text,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 14,
                        "color": colors['blue1']
                    },
                    "valign": "top",
                    "yanchor": "top",
                    "xanchor": "center",
                    "yshift": 60,
                    "xshift": 10
                }
            ]
        )

    return fig


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


def get_time_array(data_size, frequency):
    time_array = np.arange(0, data_size / frequency, 1 / frequency)

    return time_array


def get_dict(graph_id_dict, relayoutdata):
    return graph_dict_raw.get(graph_id_dict["index"]).construct_update_data(relayoutdata)


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


def get_idx_dict_list(dict_list, key, value):
    idx = next((i for i, item in enumerate(dict_list)
                if item[key] == value), None)

    return idx


def build_cutter_params_json(step_number: int, percentage: int, tolerance: int):
    data = {
        'step_number': step_number,
        'step_type': 'cut',
        'percentage': percentage,
        'tolerance': tolerance
    }

    return data


def build_bandpass_params_json(step_number: int, low_frequency: int, high_frequency: int):
    data = {
        'step_number': step_number,
        'step_type': 'bandpass',
        'low_frequency': low_frequency,
        'high_frequency': high_frequency
    }

    return data


def build_highpass_params_json(step_number: int, cut_frequency: int):
    data = {
        'step_number': step_number,
        'step_type': 'highpass',
        'cut_frequency': cut_frequency
    }

    return data


def build_lowpass_params_json(step_number: int, cut_frequency: int):
    data = {
        'step_number': step_number,
        'step_type': 'lowpass',
        'cut_frequency': cut_frequency
    }

    return data


def build_ecgfilt_params_json(step_number: int, method: EcgRemovalMethods):
    data = {
        'step_number': step_number,
        'step_type': 'ecg_removal',
        'method': method.name
    }

    return data


def build_envelope_params_json(step_number: int, method: EnvelopeMethod):
    data = {
        'step_number': step_number,
        'step_type': 'envelope',
        'method': method.name
    }

    return data
