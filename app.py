import dash
from pycompass import Compendium, Connect
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pycompass

app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.MINTY])
server = app.server

app.compass_connect = Connect('http://compass.fmach.it/graphql')
app.compass_compendium = None
app.compass_module = None

app.compass_version = app.compass_connect.get_compass_version()
app.pycompass_version = pycompass.__version__
