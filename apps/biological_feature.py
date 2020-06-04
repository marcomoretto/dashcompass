import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from pycompass import Compendium, Connect, BiologicalFeature
from dash.dependencies import Input, Output, State

from app import app
import dash_table

markdown_text = '''
### Biological Features (genes)

'''

columns = []

layout = html.Div([
    dcc.Markdown(children=[markdown_text]),
    html.Div(id='biofeature-container'),
    html.Div(id='biofeature-dummy')
],
className="p-5")