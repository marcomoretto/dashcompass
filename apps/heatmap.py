import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table

from pycompass import Compendium, Connect
from dash.dependencies import Input, Output, State
import dash_dangerously_set_inner_html

from app import app

layout = html.Div([
    dcc.Loading(
        id="heatmap-json-loading",
        children=[html.Div([
            dcc.Graph(
                    id="heatmap-json"
                ),
        ])],
        type="default",
    ),
    html.H5('Click on the heatmap to see the annotation'),
    dbc.Row([
            dbc.Col(children=[
                html.H3('Biological Feature'),
                dcc.Loading(
                    id="heatmap-bf-json-loading",
                    children=[html.Div([
                        dash_table.DataTable(
                            id='bf-rdf-annotation-table',
                            page_current=0,
                            page_size=20,
                            page_action='custom',
                            columns=[{'name': 'Subject', 'id':'subject', 'presentation':'markdown'},
                                     {'name': 'Predicate', 'id':'predicate'},
                                     {'name': 'Object', 'id':'object'}],

                        )
                    ])],
                    type="default",
                )], align="start", width={"size": 6, "order": 1},
            ),
            dbc.Col(children=[
                html.H3('Sample Sets'),
                dcc.Loading(
                    id="heatmap-ss-json-loading",
                    children=[html.Div([
                        dash_table.DataTable(
                            id='ss-rdf-annotation-table',
                            page_current=0,
                            page_size=20,
                            page_action='custom',
                            columns=[{'name': 'Sample', 'id': 'sample', 'presentation':'markdown'},
                                     {'name': 'Subject', 'id': 'subject'},
                                     {'name': 'Predicate', 'id': 'predicate'},
                                     {'name': 'Object', 'id': 'object'}]
                        )
                    ])],
                    type="default",
                )], align="end", width={"size": 5, "order": 2, "offset": 1},
            ),
    ]),
    ],
    className="p-5")