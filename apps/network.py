import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from pycompass import Compendium, Connect
from dash.dependencies import Input, Output, State

from app import app

layout = html.Div([
    dcc.Loading(
        id="heatmap-json-loading",
        children=[html.Div([
            dcc.Graph(
                id="network-json",
            ),
        ])],
        type="default",
    ),
    html.Div([
        dcc.Slider(
            id='network-correlation-slider',
            min=0.0,
            max=1.0,
            step=0.1,
            value=0.7,
        ),
        html.Div(id='network-slider-output-container')
    ])
], className="p-5")