import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from pycompass import Compendium, Connect
from dash.dependencies import Input, Output, State

from app import app

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

layout = html.Div([
    html.H1("About"),
    html.Br(),
    dcc.Markdown('''
                [COMPASS](https://compass.readthedocs.io) version: {compass_version}
                '''.format(compass_version=app.compass_version)),
    html.Br(),
    dcc.Markdown('''
                [pyCOMPASS](https://pycompass.readthedocs.io) version: {compass_version}
                '''.format(compass_version=app.pycompass_version)),
    html.Br(),
    html.H3("Compendium stats"),
    html.Div(id='about-select-compendium', children=[
        dcc.Dropdown(
            id='about-dropdown',
            options=compendia,
            placeholder="Select a compendium",
            value=compendia[0]['value']
        )
    ]),
    html.Br(),
    html.Br(),
    dcc.Loading(
        id="about-description-loading",
        children=[html.Div([html.Div(id="about-description")])],
        type="default",
    )
], className="p-5")
