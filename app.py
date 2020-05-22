import base64
import io
import dash
import dash_table
import dash_core_components as dcc  # São componentes interativos gerados com js, html e css através do reactjs
import dash_html_components as html # Possui um componente para cada tag html
from dash.dependencies import Input, Output, State
from yellowbrick.cluster import KElbowVisualizer
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import pandas as pd
import vislogprob
from shapely import wkt
import geo
import numpy as np
import plotly.express as px
import urllib
from flask import send_file
import flask


# Style:
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# two columns  = 13.3333333333%
# four columns = 30.6666666667%
# five columns = 39.3333333333%
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Empty Graphs
init_fig = px.scatter(x=[], y=[], log_x=True, log_y=True, labels={'x':'x axis', 'y':'y axis'})
init_fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10}, paper_bgcolor='#f9f9f9')
map_init_fig = px.choropleth_mapbox(locations=[0], center={"lat": -13.5, "lon": -48.5}, mapbox_style="carto-positron", zoom=4)
map_init_fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10}, paper_bgcolor='#f9f9f9')

app.layout = html.Div(children=[
    dcc.Store(id="aggregate_data"),
    # empty Div to trigger javascript file for graph resizing
    html.Div(id="output-clientside"),
    html.Div(
        [
            html.Div(
                [
                    html.H3(
                        "Geochemical Prospection",
                        style={"margin-bottom": "0px"},
                    ),
                    html.H5(
                        "Workflow for Geochemical Prospection utilyzing Dash and K-means Clustering", style={"margin-top": "0px"}
                    ),
                ]
            )
        ],
        id="title", style={'display':'flex', 'margin-bottom':'25px'}
    ),

    html.Div([  # classe ROW -> dois containers
        html.Div([  # classe caixa
            html.Div([  # classe 5 colunas
                html.Div([
                    html.P(children='1. Load .csv data:', style={'textAlign': 'center', 'color': 'rgb(5, 75, 102)', 'font-size':'16px'}),

                    html.Div(dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin-top':'10px',
                            'margin-bottom':'10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    )),

                    html.P(children='1.2 Select Geochemical Element:', style={'textAlign': 'center', 'font-size':'14px'}),

                    dcc.Dropdown(id='select-element', style={'margin-bottom':'5px'}, placeholder='Select Geochemical Element...'),

                    html.P(children='2. Load Geojson data:', style={'textAlign': 'center', 'font-size':'16px',  'color': 'rgb(5, 75, 102)'}),

                    html.Div(dcc.Upload(
                        id='upload-shapes',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin-top':'10px',
                            'margin-bottom':'10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    )),

                    html.P(['Obs: all coordinates of both sample data and shapefiles must be geographic'], style={'font-style':'italic', 'font-size':'12px'})

                ], className='row')

                ], className='start column', style={'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey', 'width':'20%', 'height':'420.6px'})]),

        html.Div([  # Classe Caixa
            html.Div([  # classe 7 colunas
                html.P(children='2. Nº of Clusters by Elbow Method:', style={'textAlign': 'center', 'font-size':'16px',  'color': 'rgb(5, 75, 102)'}),
                dcc.Graph(
                    id='cluster-graph', figure=init_fig, style={'height':'370px'}
                )
            ], className='elbow column',
                style={'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey', 'width':'30%', 'height':'420.6px'})]),

        html.Div([   # Classe Caixa
            html.Div([   # classe 7 colunas
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(children='3. Log-probability curve:',
                                       style={'textAlign': 'center', 'width': '50%', 'font-size': '16px',  'color': 'rgb(5, 75, 102)',
                                              'display': 'inline-block', 'float': 'left'})
                            ]
                        ),
                        html.Div(
                            [
                                dcc.RadioItems(id='logprob-mode', options=[{'label':'Cluster Mode', 'value':'cluster-mode'}, {'label':'Select Mode', 'value':'select-mode'}], labelStyle={'display': 'inline-block'}, style={'margin-top':'3px'}, value='cluster-mode')
                            ]
                        )

                    ], className='row'
                ),
                dcc.Graph(
                    id='prob-graph', figure=init_fig, style={'height':'370px'}
                )
            ], className='logprob column', style={'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey', 'width':'44.5%','height':'420.6px'})])

    ], className='row'),

    html.Div([            # Row div
        html.Div([
            html.P(children='4. Spatial Overview:', style={'textAlign': 'center', 'color': 'rgb(5, 75, 102)', 'font-size':'16px'}),

            html.Div(
                [
                    html.Div(
                    [
                        html.P(children='Select Coordinates Columns from Data:', style={'textAlign': 'center', 'width':'50%','font-size': '14px',
                                                                                        'display': 'inline-block', 'float':'left', 'line-height':'2.2'})
                    ]
                         ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Dropdown(id='select-lon', placeholder='Longitude (x)...'),
                                    ], style = {'width': '23.4%', 'display': 'inline-block', 'margin-right':'5px', 'float':'left'}
                                ),
                                html.Div(
                                    [
                                        dcc.Dropdown(id='select-lat', placeholder='Latitude (y)...')
                                    ], style = {'width': '25%', 'float': 'right', 'display': 'inline-block'}
                                )
                            ]
                        )
                    ]
                        )

                ], className='row'
            ),

            html.Div(
                [
                    html.Div(
                        [
                            html.P(children='Select Geojson Polygon from Data:',
                                   style={'textAlign': 'center', 'width': '49%', 'font-size': '14px',
                                          'display': 'inline-block', 'float': 'left', 'line-height': '2.2'})
                        ]
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            dcc.Dropdown(id='select-poly', placeholder='Select Polygon Label...'),
                                        ], style={'width': '50%', 'display': 'inline-block',
                                                  'margin-left': '6px'}
                                    )
                                ]
                            )
                        ]
                    )

                ], className='row'
            ),

            dcc.Graph(id='map', figure=map_init_fig, style={'height':'475px'})
        ], className='seven columns', style={'height':'620px', 'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'}),

        html.Div([
            html.Div([  # Div para as tabs
                dcc.Tabs(id='tabs', value='tab-1', children=[  # componente tabs
                    dcc.Tab(children=[  # Data-Table
                        dash_table.DataTable(id='Data Table', columns=[{"name": '', "id": ''} for i in range(0, 6)],
                                             style_table={'height':'400px', 'overflowX': 'scroll', 'overflowY': 'scroll'})
                    ], label='Data Table', value='tab-1'),
                    dcc.Tab(children=[
                        dash_table.DataTable(id='Freq Table', columns=[{'name': 'Mínimo', 'id': 'Mínimo'},
                                                                       {'name': 'Máximo', 'id': 'Máximo'},
                                                                       {'name': 'Mínimo (log)', 'id': 'Mínimo (log)'},
                                                                       {'name': 'Frequência Absoluta',
                                                                        'id': 'Frequência Absoluta'},
                                                                       {'name': 'Frequência Relativa (%)',
                                                                        'id': 'Frequência Relativa (%)'},
                                                                       {'name': 'Frequência Acumulada',
                                                                        'id': 'Frequência Acumulada'},
                                                                       {'name': 'Frequência Acumulada Direta (%)',
                                                                        'id': 'Frequência Acumulada Direta (%)'},
                                                                       {'name': 'Frequência Acumulada Invertida (%)',
                                                                        'id': 'Frequência Acumulada Invertida (%)'}],
                                             style_table={'overflowX': 'scroll', 'overflowY': 'scroll',
                                                          'height': '400px'})
                    ], label='Frequencies Table', value='tab-2'), # Frequency Table
                    dcc.Tab(children=[  # Data-Table
                        dash_table.DataTable(id='Clustered Table', columns=[{"name": '', "id": ''} for i in range(0, 6)],
                                             style_table={'overflowX': 'scroll', 'overflowY': 'scroll',
                                                          'height': '400px'})
                    ], label='Clustered Table', value='tab-3'),
                    dcc.Tab(children=[  # Data-Table
                        dash_table.DataTable(id='Geojson Table',
                                             columns=[{"name": '', "id": ''} for i in range(0, 6)],
                                             style_table={'overflowX': 'scroll', 'overflowY': 'scroll',
                                                          'height': '400px'})
                    ], label='Geojson Data', value='tab-4')
                ]),
                html.Div([
                    html.Div([dcc.Dropdown(id='select-download', placeholder='Select Table for Download...', value='All samples', options=[{'label':'Frequency Table', 'value':'freq-table'}, {'label':'Clustered Table', 'value':'cluster-table'}])],
                             style={'margin-top': '10px', 'margin-bottom': '10px', 'width': '48%', 'float': 'left', 'display': 'inline-block'}),
                    html.A(['Download Table as csv'], id='download-link',
                             style={'margin-top': '10px', 'margin-bottom': '10px', 'width': '48%', 'display': 'inline-block', 'float': 'right'}, className='button', download="rawdata.csv", href="", target="_blank")
                ]),

            ]),
            html.P(['Frequency Table is calculated by Freedman–Diaconis Law for determining classes intervals.'], style={'font-style':'italic', 'font-size':'12px'})
        ], className='five columns', style={'height':'620px','border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'})
    ], className='row'),

    html.Div([
        html.Div([
            html.H5(children='Distribution Plot:',
                    style={'textAlign': 'center', 'color': 'rgb(5, 75, 102)', 'font-size':'16px'}),

            html.Div([
                html.Div(['Select Longitude (x)...'],
                         style={'margin-bottom': '10px', 'width': '48%', 'display': 'inline-block'}),

                html.Div([dcc.Dropdown(id='select-classes', placeholder='Select Class...', value= 'All samples')],
                         style={'margin-bottom': '10px', 'width': '48%', 'float': 'right', 'display': 'inline-block'})
            ]),

            dcc.Graph(id='dist-plot', figure=init_fig)
        ], className='six columns', style={'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'}),

        html.Div([
            html.H5(children='Spatial Join Plot:',
                    style={'textAlign': 'center', 'color': 'rgb(5, 75, 102)', 'font-size':'16px'}),

            html.Div([
                html.Div(['Select Samples Class to Join:'],
                         style={'margin-bottom': '10px', 'width': '48%', 'display': 'inline-block', 'textAlign':'center'}),

                html.Div([dcc.Dropdown(id='select-join-classes', placeholder='Select Class...', value='Anomalous samples')],
                         style={'margin-bottom': '10px', 'width': '48%', 'float': 'right', 'display': 'inline-block'})
            ]),

            dcc.Graph(id='bar-plot', figure=init_fig)
        ], className='six columns', style={'border-radius': '5px', 'background-color': '#f9f9f9', 'margin': '10px', 'padding': '15px', 'position': 'relative', 'box-shadow': '6px 6px 2px lightgrey'})
    ], className='row')

], style={'background-color':'#f2f2f2', 'padding-left':'5%', 'padding-right':'5%', 'padding-bottom':'5%'})

@app.callback(
    Output('download-link', 'href'),
    [Input('select-download', 'value'),
     Input('Freq Table', 'data'),
     Input('Clustered Table', 'data')])
def update_download_link(selected_table, cluster_dict, freq_dict):
    if selected_table == None:
        return None
    if selected_table == 'freq-table':
        df = pd.DataFrame.from_dict(freq_dict, 'columns')
        csv_string = df.to_csv(index=False, encoding='ISO-8859-1')
        csv_string = "data:text/csv;charset=ISO-8859-1," + urllib.parse.quote(csv_string)

        return csv_string
    if selected_table == 'cluster-table':
        df = pd.DataFrame.from_dict(cluster_dict, 'columns')
        csv_string = df.to_csv(index=False, encoding='ISO-8859-1')
        csv_string = "data:text/csv;charset=ISO-8859-1," + urllib.parse.quote(csv_string)

        return csv_string


@app.callback(                                     # Distribution Callback
    [Output('dist-plot', 'figure'),
     Output('select-classes', 'options')],
    [Input('select-element', 'value'),
     Input('Clustered Table', 'data'),
     Input('select-classes', 'value')]
)
def update_dists(element_column, cluster_dict, selected_plot):
    if element_column == None:
        return init_fig, [{"label": '', "value": ''} for i in range(0,1)]
    if element_column != None:
        try:
            df = pd.DataFrame.from_dict(cluster_dict, 'columns')
            markdowns = [{"label": i, "value": i} for i in df.Class.unique()]
            markdowns.append({"label": 'All samples', "value": 'All samples'})

            if selected_plot == 'All samples':
                dist = px.histogram(df, element_column, marginal='box', title=element_column+' Distribution')
                dist.update_layout(margin={'l': 60, 'b': 30, 't': 40, 'r': 60}, paper_bgcolor='#f9f9f9')

            else:
                dist = px.histogram(df, df[element_column][df.Class == selected_plot], marginal='box', title=element_column+' '+selected_plot+' Distribution')
                dist.update_layout(margin={'l': 60, 'b': 30, 't': 40, 'r': 60}, paper_bgcolor='#f9f9f9')

            return dist, markdowns
        except ValueError:
            return init_fig, [{"label": '', "value": ''} for i in range(0,1)]
        except AttributeError:
            return init_fig, [{"label": '', "value": ''} for i in range(0,1)]
    else:
        return init_fig, init_fig, [{"label": '', "value": ''} for i in range(0,1)]

@app.callback(
    [Output('bar-plot', 'figure'),
    Output('select-join-classes', 'options')],
    [Input('select-element', 'value'),
     Input('Clustered Table', 'data'),
     Input('Geojson Table', 'data'),
     Input('select-lon', 'value'),
     Input('select-lat', 'value'),
     Input('select-poly', 'value'),
     Input('select-join-classes', 'value')]
)
def update_spatialjoin(select_element, cluster_dict, geojson_dict, lon, lat, polygon_label, select_class):
    if select_element == None or geojson_dict == None or polygon_label == None or lon == None or lat == None:
        return init_fig, [{"label": '', "value": ''} for i in range(0,1)]
    else:
        try:
            cluster_df = pd.DataFrame.from_dict(cluster_dict, 'columns')
            geojson_df = pd.DataFrame.from_dict(geojson_dict, 'columns')

            markdowns = [{"label": i, "value": i} for i in cluster_df.Class.unique()]
            markdowns.append({"label": 'All samples', "value": 'All samples'})

            geojson_df['geometry'] = geojson_df['geometry'].apply(wkt.loads)

            joined = geo.spatial_join(cluster_df, lon, lat, geojson_df)
            counts = []
            for i in joined[polygon_label][joined.Class == select_class].unique():
                count = round(len(joined[joined[polygon_label] == i][joined.Class == select_class])/len(joined[joined.Class == select_class]), ndigits=3)
                counts.append(count)
            print(counts)
            print(joined[polygon_label][joined.Class == select_class].unique())
            bar = px.bar(y=joined[polygon_label][joined.Class == select_class].unique(), x=counts, orientation='h')
            bar.update_layout(margin={'l': 60, 'b': 30, 't': 40, 'r': 60}, paper_bgcolor='#f9f9f9')

            return bar, markdowns

        except ValueError as e:
            print('deu value error')
            print(e)
            return init_fig, [{"label": '', "value": ''} for i in range(0,1)]
        except AttributeError as e:
            print('deu attribute error')
            print(e)
            return init_fig, [{"label": '', "value": ''} for i in range(0,1)]
        except KeyError as e:
            print('deu key error')
            print(e)
            return init_fig, [{"label": '', "value": ''} for i in range(0,1)]

@app.callback(
    [Output('prob-graph', 'figure'),
     Output('cluster-graph', 'figure'),
     Output('Clustered Table', 'data'),
     Output('Clustered Table', 'columns')],        # A saída é a figura do gráfico
    [Input('select-element', 'value'),
     Input('Data Table', 'data'),
     Input('prob-graph', 'selectedData'),
     Input('logprob-mode', 'value')])                 # Entrada: valor da tabela,
def update_graph(element_column, data_dict, selectedData, mode):
    if element_column == None:
        return init_fig, init_fig, [{"name": '', "id": ''} for i in range(0, 6)], [{"name": '', "id": ''} for i in range(0,6)]

    if selectedData != None and mode == 'select-mode':
        df = pd.DataFrame.from_dict(data_dict, 'columns')
        x, y = vislogprob.logprob(df[element_column])

        X = np.array([x,y])
        visualizer = KElbowVisualizer(KMeans(), k=(1, 8))
        visualizer.fit(X.transpose())

        originalData = pd.DataFrame()
        originalData.insert(0, 'Probability', x)
        originalData.insert(1, 'Value', y[::-1])

        selected_x = []
        for point in selectedData['points']:
            selected_x.append(point['x'])

        max_prob = np.max(selected_x)*0.01
        originalData['Class'] = originalData.apply(
            lambda row: 'Anomalous Sample' if row['Probability'] <= max_prob else 'Background Sample', axis=1)

        probgraf_fig = px.scatter(x=originalData.Probability*100, y=originalData.Value, color=originalData.Class, log_y=True, log_x=True,
                                  labels={'x':'Probability (%) ', 'y':str(element_column)+''})
        probgraf_fig.update_layout(margin={'l': 10, 'b': 10, 't': 10, 'r': 10}, paper_bgcolor='#f9f9f9', legend_orientation="h")

        cluster_fig = px.line(x=visualizer.k_values_, y=visualizer.k_scores_, labels={'x':'Number of K clusters', 'y':'Distortion Score'}, range_y=[-5, np.max(visualizer.k_scores_)+np.mean(visualizer.k_scores_)/3])
        cluster_fig.update_traces(mode="markers+lines", hovertemplate=None)
        cluster_fig.add_shape(dict(type='line',
                                   x0=visualizer.elbow_value_,
                                   y0=-np.mean(visualizer.k_scores_),
                                   x1=visualizer.elbow_value_,
                                   y1=np.max(visualizer.k_scores_)+np.mean(visualizer.k_scores_),
                                   line=dict(dash='dashdot', color='#EF553B')))
        cluster_fig.update_layout(margin={'l': 10, 'b': 10, 't': 10, 'r': 10}, paper_bgcolor='#f9f9f9', legend_orientation="h")

        merged_df = df.merge(originalData, left_on=element_column, right_on='Value')
        merged_df = merged_df.drop(axis=1, labels='Value')
        cluster_columns = [{"name": i, "id": i} for i in merged_df.columns]

        return probgraf_fig, cluster_fig, merged_df.to_dict('records'), cluster_columns

    else:
        df = pd.DataFrame.from_dict(data_dict, 'columns')
        x, y = vislogprob.logprob(df[element_column])
        X = np.array([x,y])

        visualizer = KElbowVisualizer(KMeans(), k=(1, 8))
        visualizer.fit(X.transpose())

        df_clustered = vislogprob.clustered_df(X.transpose(), visualizer.elbow_value_)

        probgraf_fig = px.scatter(x=df_clustered.Prob[::-1], y=df_clustered.Value, color=df_clustered.Class, log_y=True, log_x=True,
                                  labels={'x':'Probability (%) ', 'y':str(element_column)+''})
        probgraf_fig.update_layout(margin={'l': 10, 'b': 10, 't': 10, 'r': 10}, paper_bgcolor='#f9f9f9', legend_orientation="h")

        cluster_fig = px.line(x=visualizer.k_values_, y=visualizer.k_scores_, labels={'x':'Number of K clusters', 'y':'Distortion Score'}, range_y=[-5, np.max(visualizer.k_scores_)+np.mean(visualizer.k_scores_)/3])
        cluster_fig.update_traces(mode="markers+lines", hovertemplate=None)
        cluster_fig.add_shape(dict(type='line',
                                   x0=visualizer.elbow_value_,
                                   y0=-np.mean(visualizer.k_scores_),
                                   x1=visualizer.elbow_value_,
                                   y1=np.max(visualizer.k_scores_)+np.mean(visualizer.k_scores_),
                                   line=dict(dash='dashdot', color='#EF553B')))
        cluster_fig.update_layout(margin={'l': 10, 'b': 10, 't': 10, 'r': 10}, paper_bgcolor='#f9f9f9', legend_orientation="h")

        merged_df = df.merge(df_clustered, left_on=element_column, right_on='Value')
        merged_df = merged_df.drop(axis=1, labels='Value')
        cluster_columns = [{"name": i, "id": i} for i in merged_df.columns]
        return probgraf_fig, cluster_fig, merged_df.to_dict('records'), cluster_columns


@app.callback(
    [Output('Freq Table', 'data'),
     Output('logprob-mode', 'value')], # A saída são as dados da tabela
    [Input('select-element', 'value'),
     Input('Data Table', 'data')])             # Entrada: valor da tabela
def update_freq(element_column, data_dict):
    if element_column == None:
        return [{"name": '', "id": ''} for i in range(0,6)], 'cluster-mode'
    else:
        df = pd.DataFrame.from_dict(data_dict, 'columns')
        freq_df = vislogprob.tabela_frequencias(df[element_column])
        return freq_df.to_dict('records'), 'cluster-mode'

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    data = df.to_dict('records')
    columns = [{'name': i, 'id': i} for i in df.columns]

    return columns, data

@app.callback([Output('select-poly', 'options'),
               Output('select-poly', 'value'),
               Output('Geojson Table', 'data'),
               Output('Geojson Table', 'columns')],
               [Input('upload-shapes', 'contents')],
               [State('upload-shapes', 'filename')])
def update_geojson(list_of_contents, list_of_names):
    if list_of_contents is None:
        return [{"label": '', "value": ''} for i in range(0,1)], None, [{"name": '', "id": ''} for i in range(0,6)], [{"name": '', "id": ''} for i in range(0,6)]
    else:
        children = [
            geo.parse_geojson(c, n) for c, n in
            zip(list_of_contents, list_of_names)]
        columns, data = children[0]
        values = []
        for i in columns:
            if i['name'][0:7] != 'Unnamed' and i['name'][0:7] != 'geometry':
                values.append(i['name'])
        markdowns = [{"label": i, "value": i} for i in values]
        columns = [{"name": i, "id": i} for i in values]

        return markdowns, None, data, columns


@app.callback([Output('Data Table', 'data'),
              Output('Data Table', 'columns'),
              Output('select-element', 'options'),
              Output('select-element', 'value'),
              Output('select-lon', 'options'),
              Output('select-lon', 'value'),
              Output('select-lat', 'options'),
              Output('select-lat', 'value')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(list_of_contents, list_of_names):
    if list_of_contents is None:
        return [{"name": '', "id": ''} for i in range(0,15)], [{"name": '', "id": ''} for i in range(0,6)], [{"label": '', "value": ''} for i in range(0,1)], None, [{"label": '', "value": ''} for i in range(0,1)], None, [{"label": '', "value": ''} for i in range(0,6)], None
    if list_of_contents is not None:
        children = [
            parse_contents(c, n) for c, n in
            zip(list_of_contents, list_of_names)]
        columns, data = children[0]
        values = []
        for i in columns:
            if i['name'][0:7] != 'Unnamed':
                values.append(i['name'])
        markdowns = [{"label": i, "value": i} for i in values]
        columns = [{"name": i, "id": i} for i in values]
        return data, columns, markdowns, None, markdowns, None, markdowns, None

# Map Callbacks:
@app.callback(
    Output('map', 'figure'),
    [Input('Data Table', 'data'),
    Input('Clustered Table', 'data'),
    Input('select-lon', 'value'),
    Input('select-lat', 'value'),
    Input('select-element', 'value'),
    Input('Geojson Table', 'data'),
    Input('select-poly', 'value')]
)
def update_map(data_dict, cluster_dict, lon, lat, element_column, geo_dict, geo_column):
    map_init_fig = px.choropleth_mapbox(locations=[0], center={"lat": -13.5, "lon": -48.5},
                                        mapbox_style="carto-positron", zoom=3)
    map_init_fig.update_layout(margin={"r": 10, "t": 10, "l": 10, "b": 10}, paper_bgcolor='#f9f9f9')
    geodf = pd.DataFrame.from_dict(geo_dict, 'columns')

    if lon == None or lat == None:
        if geo_column == None:
            return map_init_fig
        if geo_column != None:
            geodf['geometry'] = geodf['geometry'].apply(wkt.loads)
            geojson = geo.add_ids(geodf, list(geodf.index), geo_column)
            map = px.choropleth_mapbox(geodf, geojson=geojson, color=geo_column,
                                       locations=list(geodf.index),
                                       center={"lat": -13.499799951999933, "lon": -48.57199078199994},
                                       mapbox_style="carto-positron", zoom=9, opacity=0.3)
            map.update_layout(margin={"r": 10, "t": 10, "l": 10, "b": 10}, paper_bgcolor='#f9f9f9')
            return map

    if lon != None and lat != None:
        if geo_column == None:    # Mapa com pontos e sem polígonos
            try:
                if element_column == None:        # Retorna Mapa de pontos sem cluster
                    df = pd.DataFrame.from_dict(data_dict, 'columns')
                    map_init_fig.add_scattermapbox(lat=df[lat], lon=df[lon])
                    map_init_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, paper_bgcolor='#f9f9f9')

                    return map_init_fig
                if element_column != None:        # Retorna Mapa de pontos com cluster
                    df = pd.DataFrame.from_dict(cluster_dict, 'columns')
                    classes_list = list(df.Class.unique())
                    classes_list.sort(reverse=True)
                    for cluster in classes_list:
                        map_init_fig.add_scattermapbox(lat=df[lat][df.Class == cluster], lon=df[lon][df.Class == cluster],
                                                       name=cluster)
                    map_init_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, legend_orientation="h",
                                               paper_bgcolor='#f9f9f9')

                    return map_init_fig
            except AttributeError:
                return map_init_fig
        if geo_column != None:      # Se tiverem polígonos selecionados
            if element_column == None:       # Sem clusters
                geodf['geometry'] = geodf['geometry'].apply(wkt.loads)
                geojson = geo.add_ids(geodf, list(geodf.index), geo_column)
                map = px.choropleth_mapbox(geodf, geojson=geojson, color=geo_column,
                                           locations=list(geodf.index),
                                           center={"lat": -13.499799951999933, "lon": -48.57199078199994},
                                           mapbox_style="carto-positron", zoom=9, opacity=0.3)
                df = pd.DataFrame.from_dict(data_dict, 'columns')
                map.add_scattermapbox(lat=df[lat], lon=df[lon])
                map.update_layout(margin={"r": 10, "t": 10, "l": 10, "b": 10}, paper_bgcolor='#f9f9f9')
                return map

            if element_column != None:       # Com clusters
                geodf['geometry'] = geodf['geometry'].apply(wkt.loads)
                geojson = geo.add_ids(geodf, list(geodf.index), geo_column)
                map = px.choropleth_mapbox(geodf, geojson=geojson, color=geo_column,
                                           locations=list(geodf.index),
                                           center={"lat": -13.499799951999933, "lon": -48.57199078199994},
                                           mapbox_style="carto-positron", zoom=9, opacity=0.3)
                df = pd.DataFrame.from_dict(cluster_dict, 'columns')
                classes_list = list(df.Class.unique())
                classes_list.sort(reverse=True)
                for cluster in classes_list:
                    map.add_scattermapbox(lat=df[lat][df.Class == cluster], lon=df[lon][df.Class == cluster],
                                                   name=cluster)
                map.update_layout(margin={"r": 10, "t": 10, "l": 10, "b": 10}, paper_bgcolor='#f9f9f9')
                return map

    else:
        return map_init_fig

if __name__ == '__main__':
    app.run_server(debug=True)   # Atualiza a página automaticamente com modificações do código fonte