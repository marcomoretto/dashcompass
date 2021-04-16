import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from pycompass import Compendium, Connect
from dash.dependencies import Input, Output, State

from app import app


markdown_text = '''
### Overview

#### Welcome to the COMPASS Dash interface for VESPUCCI!
* [VESPUCCI](https://vespucci.readthedocs.io/) is a database for exploring and analyzing a comprehensive Vitis vinifera specific cross-platform expression compendium. 
  This compendium was carefully constructed by collecting, homogenizing and formally annotating publicly available microarray and RNA-seq experiments.
* [COMPASS](https://compass.readthedocs.io) (**COM**pendia **P**rogrammatic **A**ccess **S**upport **S**oftware) is a software layer that provides a 
  [GraphQL](https://graphql.org/) endpoint to query compendia built using [COMMAND>_](https://command.readthedocs.io>) technology.
* [Dash](https://dash.plotly.com/introduction) *is a productive Python framework for building web applications.*

#### Warning!
This application is meant to showcase the usage of [COMPASS](https://compass.readthedocs.io) interface through a [Dash](https://dash.plotly.com/introduction) application.
This application is not meant for serious data analysis on VESPUCCI. You should rely on [pyCOMPASS](https://pycompass.readthedocs.io/) or [rCOMPASS](https://onertipaday.github.io/rcompass/) for that.
Have a look at the [use cases for VESPUCCI](https://vespucci.readthedocs.io/en/latest/use_cases.html)!

'''
is_open = False

###
# Get available compendia
compendia = []
for c in app.compass_connect.describe_compendia()['compendia']:
    if c['name'] != 'vespucci':
        continue
    for v in c['versions']:
        for d in v['databases']:
            for n in d['normalizations']:
                norm=n.replace('(default)', '').strip()
                label = "{full_name} - v {version} ({version_alias}), {database} {normalization} normalized ".format(
                    full_name=c['fullName'],
                    version=v['versionNumber'],
                    version_alias=v['versionAlias'],
                    database=d['name'],
                    normalization=norm
                )
                value = "__{name}__{version}__{database}__{normalization}__".format(
                    name=c['name'],
                    version=v['versionNumber'],
                    database=d['name'],
                    normalization=norm
                )
                compendia.append({'label': label, 'value': value})

####
# LAYOUT

advanced_search_layout = html.Div([
    dbc.Card([
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        f"Search by experiment",
                        color="link",
                        id=f"group-1-search-exp-toggle",
                    )
                ),
            ),
            dbc.Collapse(
                dbc.CardBody([
                    dcc.Textarea(
                        id='overview-textarea-experiment',
                        value='GSE36128, GSE41633',
                        style={'width': '100%', 'height': 200},
                    ),
                    dbc.Button('Search', id='overview-textarea-search-exp', n_clicks=0, className="mb-3", color="primary",),
                ],id="card-1-search-exp"),
                id=f"collapse-1-search-exp"
            )
        ],
    ),
    dbc.Card([
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        f"Search by annotation using SPARQL",
                        color="link",
                        id=f"group-2-sparql-toggle",
                    )
                )
            ),
            dbc.Collapse(
                dbc.CardBody([
                    dcc.Textarea(
                        id='overview-textarea-sparql',
                        value='',
                        style={'width': '100%', 'height': 200},
                    ),
                    html.Br(),
                    dcc.Dropdown(
                        id='overview-dropdown-sparql-target',
                        options=[{'label': 'Sample', 'value': 'sample'}, {'label': 'Biological Features', 'value': ' biofeature'}],
                        placeholder="Select a target for the SPARQL query",
                        value='sample'
                    ),
                    html.Br(),
                    dbc.Button('Search', id='overview-textarea-search-sparql', n_clicks=0, className="mb-3", color="primary",),
                ],id="card-2-sparql-exp"),
                id=f"collapse-2-sparql"
            )
        ]
    ),
], className="p-5")

layout = html.Div([
    dcc.Markdown(children=[markdown_text]),
    dcc.Markdown('''
    ### Select Compendium version
    '''),
    html.Div(id='overview-select-compendium', children=[
        dcc.Dropdown(
            id='overview-dropdown',
            options=compendia,
            placeholder="Select a compendium",
            value=compendia[2]['value']
        )
    ]),
    html.Br(),
    dcc.Markdown('''
        ### Quick search
        
        Create new module searching by gene ids. Insert comma-separated gene ids and press SEARCH'''),
    dcc.Textarea(
        id='overview-textarea-biofeatures',
        value='B9S8R7,Q7M2G6,D7SZ93,B8XIJ8,Vv00s0125g00280,Vv00s0187g00140,Vv00s0246g00010,Vv00s0246g00080,Vv00s0438g00020,Vv00s0246g00200,VIT_00s0246g00220,VIT_00s0332g00060,VIT_00s0332g00110,VIT_00s0332g00160,VIT_00s0396g00010,VIT_00s0505g00030,VIT_00s0505g00060,VIT_00s0873g00020,VIT_00s0904g00010',
        style={'width': '100%', 'height': 200},
    ),
    dbc.Button('Search', id='overview-textarea-biofeatures-search', n_clicks=0, className="mb-3", color="primary",),
    dcc.Loading(
        id="overview-confirm-loading",
        children=[html.Div([dbc.Alert("", color="primary", id="overview-textarea-biofeatures-search-confirm"),])],
        type="default",
    ),
    html.Br(),
    html.Br(),
    html.Div(
        [
            dbc.Button(
                "Advanced Search Options",
                id="advanced-search-options-button",
                className="mb-3",
                color="info",
            ),
            dbc.Collapse(
                dbc.Card(
                    dbc.CardBody([advanced_search_layout])
                ),
                id="advanced-search-options",
            ),
        ]
    ),
    dbc.Modal([
            dbc.ModalHeader("Create quick module"),
            dbc.ModalBody("Searching genes and creating module ... Please wait!"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal-create-quick-module", className="ml-auto")
            ),
        ],
        id="modal-create-quick-module",
    ),
], className="p-5")
