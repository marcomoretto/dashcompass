import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from pycompass import Compendium, Connect
from dash.dependencies import Input, Output, State

from app import app

####
# LAYOUT

edit_module_bf_layout =  html.Div([
    dbc.Row([
        dbc.Col(children=[
            html.Div([
                html.Br(),
                dcc.Markdown('''
                Type Biological Features names to add (or remove) them to the module, or click on the **top right** 
                distribution plot to select **new** Biological Features to add based on the selected cut-off.
                '''),
                html.Br(),
                dcc.Loading(
                    id="tool-textarea-biologicalfeatures-loading",
                    children=[html.Div([
                        dcc.Textarea(
                            id='tool-textarea-biologicalfeatures',
                            style={'width': '100%', 'height': 300}
                        )
                    ])],
                    type="default",
                ),
                html.Br(),
                dbc.Button(
                    f"Add",
                    id='tools-bf-add'
                ),
                dbc.Button(
                    f"Remove",
                    id='tools-bf-remove',
                    style={"margin-left": "15px"}
                ),
            ])
        ], id="card-1-ss"),
        dbc.Col(children=[
            html.Label("Plot type"),
            dcc.Loading(
                id="bf-add-graph-option-json-loading",
                children=[html.Div([html.Div(id='bf-add-graph-option-json')])],
                type="default",
            ),
            html.Br(),
            html.Br(),
            dcc.Loading(
                id="bf-add-graph-json-loading",
                children=[html.Div([html.Div(id='bf-add-graph-json')])],
                type="default",
            )
        ])
    ])
], className="p-5")

edit_module_ss_layout = html.Div([
    dbc.Row([
        dbc.Col(children=[
            html.Div([
                html.Br(),
                dcc.Markdown('''
                Type Sample Sets names to add (or remove) them to the module, or click on the **top right** 
                distribution plot to select **new** Sample Sets to add based on the selected cut-off.
                '''),
                html.Br(),
                dcc.Loading(
                    id="tool-textarea-samplesets-loading",
                    children=[html.Div([
                        dcc.Textarea(
                            id='tool-textarea-samplesets',
                            style={'width': '100%', 'height': 300}
                        ),
                    ])],
                    type="default",
                ),
                html.Br(),
                dbc.Button(
                    f"Add",
                    id='tools-ss-add'
                ),
                dbc.Button(
                    f"Remove",
                    id='tools-ss-remove',
                    style={"margin-left": "15px"}
                ),
            ])
        ], id="card-1-ss"),
        dbc.Col(children=[
            html.Label("Plot type"),
            dcc.Loading(
                id="ss-add-graph-option-json-loading",
                children=[html.Div([html.Div(id='ss-add-graph-option-json')])],
                type="default",
            ),
            html.Br(),
            html.Br(),
            dcc.Loading(
                id="ss-add-graph-json-loading",
                children=[html.Div([html.Div(id='ss-add-graph-json')])],
                type="default",
            )
        ])
    ])
], className="p-5")

layout = html.Div([
    dbc.Card([
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        f"Download module",
                        color="link",
                        id=f"group-1-io-toggle",
                    )
                ),
            ),
            dbc.Collapse(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(children=[
                            html.H3('Download module TSV file'),
                            dbc.Button(
                                "Create TSV file",
                                id="tool-download-module-button",
                                className="mb-3",
                                color="info",
                            ),
                            dcc.Loading(
                                id="tool-download-module",
                                children=[html.Div([
                                    html.Ul(id="download-file-list")
                                ])],
                                type="default",
                            )
                        ]),
                        #dbc.Col(children=[
                        #    html.H3('Upload module'),
                        #    dcc.Upload(
                        #        id="upload-module-data",
                        #        children=html.Div(
                        #            ["Drag and drop or click to select a file to upload."]
                        #        ),
                        #        style={
                        #            "width": "100%",
                        #            "height": "60px",
                        #            "lineHeight": "60px",
                        #            "borderWidth": "1px",
                        #            "borderStyle": "dashed",
                        #            "borderRadius": "5px",
                        #            "textAlign": "center",
                        #            "margin": "10px",
                        #        },
                        #        multiple=True,
                        #    ),
                        #    html.Br(),
                        #    dcc.Loading(
                        #        id="upload-file-list-loading",
                        #        children=[html.Div([
                        #            html.Ul(id="upload-file-list")
                        #        ])],
                        #        type="default",
                        #    )
                        #]),
                    ], className="p-5")
                ], id="card-1-io"),
                id=f"collapse-1-io",
            ),
        ],
    ),
    dbc.Card([
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        f"Edit Module",
                        color="link",
                        id=f"group-2-edit-toggle",
                    )
                )
            ),
            dbc.Collapse(
                dbc.CardBody([
                    html.Div([
                        dcc.Tabs(
                                id="tabs-edit-module",
                                value='bf-edit-module',
                                parent_className='custom-tabs',
                                className='custom-tabs-container',
                                children=[
                                    dcc.Tab(
                                        label='Biological features',
                                        value='bf-edit-module',
                                        className='custom-tab',
                                        selected_className='custom-tab--selected',
                                    ),
                                    dcc.Tab(
                                        label='Sample set',
                                        value='ss-edit-module',
                                        className='custom-tab',
                                        selected_className='custom-tab--selected'
                                    )
                                ]
                        ),
                        html.Div(id='tabs-edit-module-content')
                    ])
                ], className="p-5"),
                id=f"collapse-2-edit",
            ),
        ]
    ),
    dbc.Modal([
            dbc.ModalHeader("Module modified"),
            dbc.ModalBody("Sample Sets added to the module!"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal-modify-module-ss-add", className="ml-auto")
            ),
        ],
        id="modal-tool-modify-module-ss-add",
    ),
    dbc.Modal([
            dbc.ModalHeader("Module modified"),
            dbc.ModalBody("Sample Sets removed to the module!"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal-modify-module-ss-remove", className="ml-auto")
            ),
        ],
        id="modal-tool-modify-module-ss-remove",
    ),
    dbc.Modal([
            dbc.ModalHeader("Module modified"),
            dbc.ModalBody("Biological Features added to the module!"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal-modify-module-bf-add", className="ml-auto")
            ),
        ],
        id="modal-tool-modify-module-bf-add",
    ),
    dbc.Modal([
            dbc.ModalHeader("Module modified"),
            dbc.ModalBody("Biological Features removed to the module!"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal-modify-module-bf-remove", className="ml-auto")
            ),
        ],
        id="modal-tool-modify-module-bf-remove",
    ),
], className="p-5")
