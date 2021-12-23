import base64
import os
import uuid
from collections import OrderedDict

import dash
import json
import dash_core_components as dcc
import dash_dangerously_set_inner_html
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from numpy import DataSource

from app import app
from apps import overview, heatmap, network, biological_feature, sample_sets, about, tools

from pycompass import Compendium, Connect, BiologicalFeature, Module, SampleSet, Plot, Annotation, Experiment, Sample, \
    Platform, Ontology

import pandas as pd
import numpy as np

N_CLICKS = OrderedDict([('overview-textarea-search-exp',0), ('overview-textarea-biofeatures-search',0),
                        ('overview-textarea-search-sparql', 0)])


server = app.server

app.layout = html.Div([
    dcc.Tabs(
        id="tabs-with-classes",
        value='overview',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(
                label='Overview',
                value='overview',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Heatmap',
                value='heatmap',
                className='custom-tab',
                selected_className='custom-tab--selected',
                id='heatmap-tab',
                disabled=True
            ),
            dcc.Tab(
                label='Network',
                value='network', className='custom-tab',
                selected_className='custom-tab--selected',
                id='network-tab',
                disabled=True
            ),
            dcc.Tab(
                label='Biological Features',
                value='biological_features',
                className='custom-tab',
                selected_className='custom-tab--selected',
                id='biological_features-tab',
                disabled=True
            ),
            dcc.Tab(
                label='Sample Sets',
                value='sample_sets',
                className='custom-tab',
                selected_className='custom-tab--selected',
                id='sample_sets-tab',
                disabled=True
            ),
            dcc.Tab(
                label='Tools',
                value='tools',
                className='custom-tab',
                selected_className='custom-tab--selected',
                id='tools-tab',
                disabled=True
            ),
            dcc.Tab(
                label='About',
                value='about',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
        ]),
    html.Div(id='tabs-content-classes')
])

table_filter_operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

def split_filter_part(filter_part):
    for operator_type in table_filter_operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3

###
# CALLBACK
@app.callback(Output('tabs-edit-module-content', 'children'),
              [Input('tabs-edit-module', 'value')])
def render_content(tab):
    if tab == 'bf-edit-module':
        return tools.edit_module_bf_layout
    elif tab == 'ss-edit-module':
        return tools.edit_module_ss_layout


@app.callback(Output('tabs-content-classes', 'children'),
              [Input('tabs-with-classes', 'value')])
def render_content(tab):
    if tab == 'overview':
        return overview.layout
    elif tab == 'heatmap':
        return heatmap.layout
    elif tab == 'network':
        return network.layout
    elif tab == 'biological_features':
        return biological_feature.layout
    elif tab == 'sample_sets':
        return sample_sets.layout
    elif tab == 'tools':
        return tools.layout
    elif tab == 'about':
        return about.layout

@app.callback(
    [Output('network-slider-output-container', 'children'), Output('network-json', 'figure')],
    [Input('network-correlation-slider', 'value')])
def update_network_output(value):
    if app.compass_module:
        return 'Pearson correlation threshold: {}'.format(value), json.loads(Plot(app.compass_module).plot_network(output_format='json', threshold=value))
    return '', None

@app.callback(
    Output('bf-annotation-network-json', 'figure'),
    [Input('bf-annotation-network-json', 'value')])
def update_annotation_network_bf(value):
    if app.compass_module:
        return json.loads(Plot(app.compass_module).plot_network(output_format='json', threshold=0.5))
    return '', None


@app.callback(
    Output("advanced-search-options", "is_open"),
    [Input("advanced-search-options-button", "n_clicks")],
    [State("advanced-search-options", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    [Output("overview-textarea-biofeatures-search-confirm", "is_open"), Output("overview-textarea-biofeatures-search-confirm", "children"),
     Output("heatmap-tab", "disabled"), Output("network-tab", "disabled"), Output("sample_sets-tab", "disabled"),
     Output("biological_features-tab", "disabled"), Output("tools-tab", "disabled")],
    [Input('overview-textarea-biofeatures-search', 'n_clicks'), Input('overview-textarea-search-exp', 'n_clicks'),
     Input('overview-textarea-search-sparql', 'n_clicks')],
    [State('overview-textarea-biofeatures', 'value'), State('overview-textarea-experiment', 'value'),
     State('overview-textarea-sparql', 'value'), State('overview-dropdown-sparql-target', 'value')]
)
def biofeatures_quick_search(n_clicks1, n_clicks2, n_clicks3, value1, value2, value3, value4):
    global N_CLICKS
    _n_clicks1 = n_clicks1 - N_CLICKS['overview-textarea-biofeatures-search']
    _n_clicks2 = n_clicks2 - N_CLICKS['overview-textarea-search-exp']
    _n_clicks3 = n_clicks3 - N_CLICKS['overview-textarea-search-sparql']
    N_CLICKS['overview-textarea-biofeatures-search'] = n_clicks1
    N_CLICKS['overview-textarea-search-exp'] = n_clicks2
    N_CLICKS['overview-textarea-search-sparql'] = n_clicks3
    if not app.compass_compendium:
        return False, '', True, True, True, True, True
    elif _n_clicks1 == 0 and _n_clicks2 == 0 and  _n_clicks3 == 0 and not app.compass_module:
        return False, '', True, True, True, True, True
    elif _n_clicks1 == 0 and _n_clicks2 == 0 and  _n_clicks3 == 0 and app.compass_module:
        return True, 'Module ready! The size is {bf} biological features and {ss} sample sets. Check the other Tabs!'.format(
            bf=len(app.compass_module.biological_features),
            ss=len(app.compass_module.sample_sets),
        ), False, False, False, False, False
    elif _n_clicks1 == 1 and _n_clicks2 == 0 and _n_clicks3 == 0:
        names = [x.strip() for x in value1.split(',')]
        bf = BiologicalFeature.using(app.compass_compendium).get(filter={'name_In': names})
        bf_ids = [b.id for b in bf]
        alias = []
        for n in names:
            alias.append("{{?s <http://purl.obolibrary.org/obo/NCIT_C41095> '{n}'}}".format(n=n))
        sparql = 'SELECT ?s ?p ?o WHERE {{ {alias} }}'.format(alias=' UNION '.join(alias))
        for _bf in BiologicalFeature.using(app.compass_compendium).by(sparql=sparql):
            if _bf.id not in bf_ids:
                bf.append(_bf)
        app.compass_module = Module.using(app.compass_compendium).create(biofeatures=bf)
        return True, 'Module ready! The size is {bf} biological features and {ss} sample sets. Check the other Tabs!'.format(
            bf=len(app.compass_module.biological_features),
            ss=len(app.compass_module.sample_sets),
        ), False, False, False, False, False
    elif _n_clicks1 == 0 and _n_clicks2 == 1 and _n_clicks3 == 0:
        exp_id = [x.strip() for x in value2.split(',')]
        e = Experiment.using(app.compass_compendium).get(filter={'experimentAccessId_In': exp_id})
        ss = SampleSet.using(app.compass_compendium).get(filter={"experiments": [x.id for x in e]})
        app.compass_module = Module.using(app.compass_compendium).create(samplesets=ss)
        return True, 'Module ready! The size is {bf} biological features and {ss} sample sets. Check the other Tabs!'.format(
            bf=len(app.compass_module.biological_features),
            ss=len(app.compass_module.sample_sets),
        ), False, False, False, False, False
    elif _n_clicks1 == 0 and _n_clicks2 == 0 and _n_clicks3 == 1:
        sparql = []
        for x in value3.strip().split('\n'):
            if x.strip().startswith('#'):
                continue
            sparql.append(x)
        if value4 == 'sample':
            s = Sample.using(app.compass_compendium).by(sparql=' '.join(sparql))
            ss = SampleSet.using(app.compass_compendium).by(samples=s)
            app.compass_module = Module.using(app.compass_compendium).create(samplesets=ss)
        else:
            bf = BiologicalFeature.using(app.compass_compendium).by(sparql=' '.join(sparql))
            app.compass_module = Module.using(app.compass_compendium).create(biofeatures=bf)
        return True, 'Module ready! The size is {bf} biological features and {ss} sample sets. Check the other Tabs!'.format(
            bf=len(app.compass_module.biological_features),
            ss=len(app.compass_module.sample_sets),
        ), False, False, False, False, False
    else:
        return False, '', True, True, True, True, True


@app.callback(
    [Output("bf-rdf-annotation-table", "data"), Output("ss-rdf-annotation-table", "data")],
    [Input('heatmap-json', 'clickData')],
    [State("heatmap-json", "children")],
)
def toggle_annotation(data, is_open):
    if data and app.compass_module:
        bf = next((x for x in app.compass_module.biological_features if x.id == data['points'][0]['y']), None)
        ss = next((x for x in app.compass_module.sample_sets if x.id == data['points'][0]['x']), None)
        ss_anno = []
        bf_anno = []
        for s in ss:
            for t in Annotation(s).get_triples():
                geo = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='
                sra = 'https://www.ncbi.nlm.nih.gov/sra/?term='
                if s.sampleName.startswith('GSM'):
                    url = geo + s.sampleName.split('.')[0]
                else:
                    url = sra + s.sampleName.split('.')[0]
                ss_anno.append({'sample': '[' + s.sampleName + '](' + url + ')', 'subject': t[0], 'predicate': t[1], 'object': t[2]})
        for t in Annotation(bf).get_triples():
            bf_anno.append({'subject': t[0], 'predicate': t[1], 'object': t[2]})

        return bf_anno, ss_anno
    return [], []

@app.callback(
    Output("modal-create-quick-module", "is_open"),
    [Input('overview-textarea-biofeatures-search', 'n_clicks'), Input("close-modal-create-quick-module", "n_clicks")],
    [State("modal-create-quick-module", "is_open")],
)
def toggle_modal_create_quick_module(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    dash.dependencies.Output('overview-dropdown', 'children'),
    [dash.dependencies.Input('overview-dropdown', 'value')])
def select_compendium(value):
    if not value:
        return
    compendium, version, db, normalization = value.split('__')[1:-1]
    app.compass_compendium = app.compass_connect.get_compendium(compendium, version, db, normalization)

@app.callback(
    dash.dependencies.Output('overview-textarea-sparql', 'value'),
    [dash.dependencies.Input('overview-dropdown-sparql-target', 'value')])
def select_sparql_target(value):
    if not value:
        return ''
    sparql_sample = '''
    # Get all seed samples
                        
    SELECT ?s ?p ?o 
    WHERE { ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.obolibrary.org/obo/NCIT_C19157> . 
            ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.obolibrary.org/obo/PO_0009010>}
    '''
    sparql_biofeature = '''
    # Get all hydrolase
    
    SELECT ?s ?p ?o 
    WHERE {?s <http://purl.obolibrary.org/obo/NCIT_C41095> '3.4.24.-'}
    '''
    if value == 'sample':
        return sparql_sample
    return sparql_biofeature

@app.callback(
    Output('biofeature-container', 'children'),
    [Input('biofeature-dummy', "children")])
def update_table_biological_features(page_current):
    if not app.compass_module:
        return None
    if len(app.compass_module.biological_features) == 0:
        return None
    columns = [{'name': x, 'id': x} for x in app.compass_module.biological_features[0].__dict__.keys() if x in ('id', 'name', 'description')]
    return dash_table.DataTable(
        id='biofeature-table',
        page_current=0,
        page_size=20,
        page_action='custom',
        columns=columns,

        filter_action='custom',
        filter_query='',

        sort_action='custom',
        sort_mode='multi',
        sort_by=[],

        editable=True
    )

@app.callback(
    Output('biofeature-table', 'data'),
    [Input('biofeature-table', "page_current"),
     Input('biofeature-table', "page_size"),
     Input('biofeature-table', 'sort_by'),
     Input('biofeature-table', 'filter_query')])
def update_table_biological_features(page_current, page_size, sort_by, filter):
    if not app.compass_module:
        return None
    if len(app.compass_module.biological_features) == 0:
        return None
    columns = [{'name': x, 'id': x} for x in app.compass_module.biological_features[0].__dict__.keys() if x in ('id', 'name', 'description')]
    data = pd.DataFrame([x.__dict__ for x in app.compass_module.biological_features], columns=[x['name'] for x in columns])
    filtering_expressions = filter.split(' && ')
    dff = data
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    page = page_current
    size = page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records')

@app.callback(
    Output('sample-sets-container', 'children'),
    [Input('sample-sets-dummy', "children")])
def update_table_sample_sets(page_current):
    if not app.compass_module:
        return None
    if len(app.compass_module.sample_sets) == 0:
        return None
    columns = [{'name': x, 'id': x} for x in app.compass_module.sample_sets[0].__dict__.keys() if x in ('id', 'name')]
    return dash_table.DataTable(
        id='sample-sets-table',
        page_current=0,
        page_size=20,
        page_action='custom',
        columns=columns,

        filter_action='custom',
        filter_query='',

        sort_action='custom',
        sort_mode='multi',
        sort_by=[],

        editable=True
    )

@app.callback(
    Output('sample-sets-table', 'data'),
    [Input('sample-sets-table', "page_current"),
     Input('sample-sets-table', "page_size"),
     Input('sample-sets-table', 'sort_by'),
     Input('sample-sets-table', 'filter_query')])
def update_table_sample_sets(page_current, page_size, sort_by, filter):
    if not app.compass_module:
        return None
    if len(app.compass_module.biological_features) == 0:
        return None
    columns = [{'name': x, 'id': x} for x in app.compass_module.sample_sets[0].__dict__.keys() if x in ('id', 'name')]
    data = pd.DataFrame([x.__dict__ for x in app.compass_module.sample_sets], columns=[x['name'] for x in columns])
    filtering_expressions = filter.split(' && ')
    dff = data
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    page = page_current
    size = page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records')

@app.callback(
    [Output('heatmap-json', 'figure'), Output('heatmap-json', 'style')],
              [Input('heatmap-json', 'value')])
def render_heatmap(heatmap):
    if app.compass_module:
        w = '100%'
        h = '100%'
        min = -5
        max = 5
        if app.compass_compendium.normalization == 'tpm':
            min = np.percentile(app.compass_module.values[~np.isnan(app.compass_module.values)], 1)
            max = np.percentile(app.compass_module.values[~np.isnan(app.compass_module.values)], 95)
        plot, sorted_bf, sorted_ss = Plot(app.compass_module).plot_heatmap(output_format='json', min=min, max=max)
        js = json.loads(plot)
        js['layout']['plot_bgcolor'] = "rgba(100,100,100,100)" # add gray background to missing values
        return js, {"height" : h, "width" : w}
    return {}

@app.callback(
    Output(component_id='about-description', component_property='children'),
    [Input(component_id='about-dropdown', component_property='value')])
def update_value(value):
    if value:
        data_source = {}
        compendium, version, db, normalization = value.split('__')[1:-1]
        compass_compendium = app.compass_connect.get_compendium(compendium, version, db, normalization)
        for e in Experiment.using(compass_compendium).get():
            ds = e.dataSource['sourceName']
            if ds not in data_source:
                data_source[ds] = 0
            data_source[ds] += 1
        bf_num = BiologicalFeature.using(compass_compendium).aggregate.total_count()
        ss_num = SampleSet.using(compass_compendium).aggregate.total_count()
        exp_num = sum([v for k,v in data_source.items()])
        sample_num = Sample.using(compass_compendium).aggregate.total_count()
        plt_num = Platform.using(compass_compendium).aggregate.total_count()
        ontologies = [o.name for o in Ontology.using(compass_compendium).get()]
        data_source = ["**{n}** experiments were retrieved from **{ds}**".format(n=n, ds=ds) for ds, n in data_source.items()]
        return dcc.Markdown('''
                The **{compendium_full_name}** compendium, *{description}* (version: **{version}**, database: **{db}**) contains 
                *{normalization}* normalized values for **{bf_num}** biological features, 
                measured for **{ss_num}** sample sets. This corresponds to a total of **{exp_num}** experiments 
                and **{sample_num}** samples measured on **{platform_num}** different platforms. Of these, {data_source}. 
                For annotations, **{compendium_full_name}** relies on the following Ontologies: **{ontologies}**.
                '''.format(compendium_full_name=compass_compendium.compendium_full_name,
                           description=compass_compendium.description,
                           version=version,
                           db=db,
                           normalization=normalization,
                           bf_num=bf_num,
                           ss_num=ss_num,
                           exp_num=exp_num,
                           sample_num=sample_num,
                           platform_num=plt_num,
                           data_source=", ".join(data_source),
                           ontologies=", ".join(ontologies)
                           )),

@app.callback(
    Output("upload-file-list", "children"),
    [Input("upload-module-data", "filename"), Input("upload-module-data", "contents")],
)
def upload_file(uploaded_filenames, uploaded_file_contents):
    upload_directory = 'static/upload/'
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            data = data.encode("utf8").split(b";base64,")[1]
            with open(os.path.join(upload_directory, name), "wb") as fp:
                fp.write(base64.decodebytes(data))
            app.compass_module = Module.read_from_file(os.path.join(upload_directory, name))
            bf = len(app.compass_module.biological_features)
            ss = len(app.compass_module.sample_sets)
            return [html.Li("File uploaded!"), html.Li("The size is {bf} biological features and {ss} sample sets. Check the other Tabs!".format(bf=bf, ss=ss))]

@app.callback(
    Output("download-file-list", "children"),
    [Input('tool-download-module-button', 'n_clicks')],
)
def download_module(n_clicks):
    if n_clicks:
        if app.compass_module:
            _id = str(uuid.uuid4())
            filename = 'module-' + _id + '.tsv'
            folder = 'static/download/'
            ss_names = [ss.name for ss in app.compass_module.sample_sets]
            s_names = [','.join([s.sampleName for s in ss]) for ss in app.compass_module.sample_sets]
            tuples = list(zip(ss_names, s_names))
            columns = pd.MultiIndex.from_tuples(tuples, names=["SampleSets", "Samples"])
            module_df = pd.DataFrame(app.compass_module.values,
                                     columns=columns,
                                     index=[bf.name for bf in app.compass_module.biological_features])
            module_df.to_csv(folder + filename, sep='\t')
            #app.compass_module.write_to_file(folder + filename)
            location = folder + filename
            return [html.Li(html.A(filename, href=location))]
        else:
            return [html.Li('You need to create a module first!')]
    return ''

@app.callback(
    [Output(f"collapse-1-io", "is_open"), Output(f"collapse-2-edit", "is_open")],
    [Input(f"group-1-io-toggle", "n_clicks"), Input(f"group-2-edit-toggle", "n_clicks")],
    [State(f"collapse-1-io", "is_open"), State(f"collapse-2-edit", "is_open")],
)
def toggle_accordion(n1, n2, is_open1, is_open2):
    ctx = dash.callback_context

    if not ctx.triggered:
        return "", ""
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "group-1-io-toggle" and n1:
        return not is_open1, False
    if button_id == "group-2-edit-toggle" and n2:
        return False, not is_open2
    return False, False

@app.callback(
    [Output(f"collapse-1-search-exp", "is_open"), Output(f"collapse-2-sparql", "is_open")],
    [Input(f"group-1-search-exp-toggle", "n_clicks"), Input(f"group-2-sparql-toggle", "n_clicks")],
    [State(f"collapse-1-search-exp", "is_open"), State(f"collapse-2-sparql", "is_open")],
)
def toggle_accordion_advanced(n1, n2, is_open1, is_open2):
    ctx = dash.callback_context

    if not ctx.triggered:
        return "", ""
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "group-1-search-exp-toggle" and n1:
        return not is_open1, False
    if button_id == "group-2-sparql-toggle" and n2:
        return False, not is_open2
    return False, False

@app.callback(
    [Output(f"collapse-1-bf", "is_open"), Output(f"collapse-2-bf", "is_open")],
    [Input(f"group-1-bf-toggle", "n_clicks"), Input(f"group-2-bf-toggle", "n_clicks")],
    [State(f"collapse-1-bf", "is_open"), State(f"collapse-2-bf", "is_open")],
)
def toggle_accordion_tool_bf(n1, n2, is_open1, is_open2):
    ctx = dash.callback_context

    if not ctx.triggered:
        return "", ""
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "group-1-bf-toggle" and n1:
        return not is_open1, False
    if button_id == "group-2-bf-toggle" and n2:
        return False, not is_open2
    return False, False

@app.callback(
    Output('ss-add-graph-json', 'children'),
    [Input(f"ss-edit-dropdown", "value")],
)
def toggle_ss_plot_type(value):
    if app.compass_module:
        plot = json.loads(
            Plot(app.compass_module).plot_distribution(plot_type=value, output_format='json'))
        p = dcc.Graph(
            id="ss-edit-json",
            figure=plot
        )
        return p
    return {}

@app.callback(
    Output('ss-add-graph-option-json', 'children'),
    [Input(f"ss-add-graph-option-json", "state")],
)
def toggle_accordion_tool_ss(value):
    if app.compass_module:
        plot_type = [{'label': p, 'value': p} for p in Plot(app.compass_module).plot_types['distribution'] if p.startswith('sample_sets_')]
        d = dcc.Dropdown(
            id='ss-edit-dropdown',
            options=plot_type,
            value=plot_type[0]['value']
        )
        return d
    return ''

@app.callback(
    Output("tool-textarea-samplesets", "value"),
    [Input('ss-edit-json', 'clickData'), Input('ss-edit-dropdown', 'value')],
    [State("ss-edit-json", "children")],
)
def toggle_ss_distribution(data, value, open):
    if data:
        cutoff = data['points'][0]['x']
        rank_method = Plot(app.compass_module).plot_rank_name[value]
        rank = app.compass_compendium.rank_sample_sets(app.compass_module, rank_method=rank_method, cutoff=cutoff)['ranking']['name']
        return ','.join(rank)

@app.callback(
    Output('bf-add-graph-json', 'children'),
    [Input(f"bf-edit-dropdown", "value")],
)
def toggle_bf_plot_type(value):
    if app.compass_module:
        plot = json.loads(
            Plot(app.compass_module).plot_distribution(plot_type=value, output_format='json'))
        p = dcc.Graph(
            id="bf-edit-json",
            figure=plot
        )
        return p
    return {}

@app.callback(
    Output('bf-add-graph-option-json', 'children'),
    [Input(f"bf-add-graph-json", "value")],
)
def toggle_accordion_tool_bf(value):
    if app.compass_module:
        plot_type = [{'label': p, 'value': p} for p in Plot(app.compass_module).plot_types['distribution'] if p.startswith('biological_features_')]
        d = dcc.Dropdown(
            id='bf-edit-dropdown',
            options=plot_type,
            value=plot_type[0]['value']
        )
        return d
    return ''

@app.callback(
    Output("tool-textarea-biologicalfeatures", "value"),
    [Input('bf-edit-json', 'clickData'), Input('bf-edit-dropdown', 'value')],
    [State("bf-edit-json", "children")],
)
def toggle_bf_distribution(data, value, open):
    if data:
        cutoff = data['points'][0]['x']
        rank_method = Plot(app.compass_module).plot_rank_name[value]
        rank = app.compass_compendium.rank_biological_features(app.compass_module, rank_method=rank_method, cutoff=cutoff)['ranking']['name']
        return ','.join(rank)

@app.callback(
    Output("modal-tool-modify-module-ss-add", "is_open"),
    [Input('tools-ss-add', 'n_clicks'), Input('close-modal-modify-module-ss-add', 'n_clicks')],
    [State("modal-tool-modify-module-ss-add", "is_open"), State('tool-textarea-samplesets', 'value')],
)
def tool_add_ss(n1, n2, is_open, value):
    if app.compass_module and value:
        ss = SampleSet.using(app.compass_compendium).get(filter={'name_In': [x.strip() for x in value.split(',')]})
        app.compass_module.add_sample_sets(ss)
        if n1 or n2:
            return not is_open
        return is_open
    return False

@app.callback(
    Output("modal-tool-modify-module-bf-add", "is_open"),
    [Input('tools-bf-add', 'n_clicks'), Input('close-modal-modify-module-bf-add', 'n_clicks')],
    [State("modal-tool-modify-module-bf-add", "is_open"), State('tool-textarea-biologicalfeatures', 'value')],
)
def tool_add_bf(n1, n2, is_open, value):
    if app.compass_module and value:
        bf = BiologicalFeature.using(app.compass_compendium).get(filter={'name_In': [x.strip() for x in value.split(',')]})
        app.compass_module.add_biological_features(bf)
        if n1 or n2:
            return not is_open
        return is_open
    return False

@app.callback(
    Output("modal-tool-modify-module-ss-remove", "is_open"),
    [Input('tools-ss-remove', 'n_clicks'), Input('close-modal-modify-module-ss-remove', 'n_clicks')],
    [State("modal-tool-modify-module-ss-remove", "is_open"), State('tool-textarea-samplesets', 'value')],
)
def tool_remove_ss(n1, n2, is_open, value):
    if app.compass_module and value:
        ss = SampleSet.using(app.compass_compendium).get(filter={'name_In': [x.strip() for x in value.split(',')]})
        app.compass_module.remove_sample_sets(ss)
        if n1 or n2:
            return not is_open
        return is_open
    return False

@app.callback(
    Output("modal-tool-modify-module-bf-remove", "is_open"),
    [Input('tools-bf-remove', 'n_clicks'), Input('close-modal-modify-module-bf-remove', 'n_clicks')],
    [State("modal-tool-modify-module-bf-remove", "is_open"), State('tool-textarea-biologicalfeatures', 'value')],
)
def tool_remove_bf(n1, n2, is_open, value):
    if app.compass_module and value:
        bf = BiologicalFeature.using(app.compass_compendium).get(filter={'name_In': [x.strip() for x in value.split(',')]})
        app.compass_module.remove_biological_features(bf)
        if n1 or n2:
            return not is_open
        return is_open
    return False

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)