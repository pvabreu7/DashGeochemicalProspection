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
# Style:
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Empty Graphs
init_fig = px.scatter(x=[], y=[], title='Load Data First', log_x=True, log_y=True, labels={'x':'x axis', 'y':'y axis'})
init_fig.update_layout(margin={'l': 60, 'b': 40, 't': 40, 'r': 60}, paper_bgcolor='#f9f9f9')
map_init_fig = px.choropleth_mapbox(locations=[0], center={"lat": -13.5, "lon": -48.5}, mapbox_style="carto-positron", zoom=4)
map_init_fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10})

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

    html.Hr(), # Linha Divisória -> Começo da aplicação

    html.Div([  # classe ROW -> dois containers
        html.Div([  # classe caixa
            html.Div([  # classe 5 colunas
                html.Div([
                    html.Div([html.H5(children='1. Load table:', style={'textAlign': 'center', 'color': '#054b66'})]),

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

                    html.H4('1.2 Select Geochemical Element:', style={'textAlign': 'center', 'font-size':'20px'}),
                    dcc.Dropdown(id='select-element', style={'margin-bottom':'20px'}, placeholder='Select Geochemical Element...'),

                    html.Div([
                        html.Div([dcc.Dropdown(id='select-lon', placeholder='Select Longitude (x)...')],
                                 style={'margin-bottom':'10px', 'width':'48%', 'display': 'inline-block'}),

                        html.Div([dcc.Dropdown(id='select-lat', placeholder='Select Latitude (y)...')],
                                 style={'margin-bottom':'10px', 'width':'48%',  'float': 'right', 'display': 'inline-block'})
                    ]),

                    html.H5('2. Load your Litology Geojson:', style={'textAlign': 'center', 'color': '#054b66'}),

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

                    html.H4('2.2 Select Geojson Label:', style={'textAlign': 'center', 'font-size': '20px'}),
                    dcc.Dropdown(id='select-poly', style={'margin-bottom': '20px'},
                                 placeholder='Select Polygon Label...'),

                    html.P(['Obs: all coordinates of both sample data and shapefiles must be geographic'], style={'font-style':'italic'})

                ], className='row')

                ], className='three columns', style={'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'})]),

        html.Div([  # Classe Caixa
            html.Div([  # classe 7 colunas
                html.H5(children='2. Number of Clusters by Elbow Method:',
                        style={'textAlign': 'center', 'color': '#054b66'}),

                dcc.Graph(
                    id='cluster-graph', figure=init_fig
                )
            ], className='four columns',
                style={'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'})]),

        html.Div([   # Classe Caixa
            html.Div([   # classe 7 colunas
                html.H5(children='3. Visualize Log-Probability curve:', style={'textAlign': 'center', 'color': '#054b66'}),

                dcc.Graph(
                    id='prob-graph', figure=init_fig
                )
            ], className='five columns', style={'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'})])

    ], className='row'),

    html.Div([            # Row div
        html.Div([
            dcc.Graph(id='map', figure=map_init_fig, style={'height':'600px'})
        ], className='seven columns', style={'height':'620px', 'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'}),

        html.Div([
            html.Div([  # Div para as tabs
                dcc.Tabs(id='tabs', value='tab-1', children=[  # componente tabs
                    dcc.Tab(children=[  # Data-Table
                        dash_table.DataTable(id='Data Table', columns=[{"name": '', "id": ''} for i in range(0, 6)],
                                             style_table={'height':'500px', 'overflowX': 'scroll', 'overflowY': 'scroll'})
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
                ])])
        ], className='five columns', style={'height':'620px','border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'})
    ], className='row'),

    html.Div([
        html.Div([
            dcc.Graph(id='dist-plot', figure=init_fig)
        ], className='six columns', style={'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'}),

        html.Div([
            dcc.Graph(id='box-plot', figure=init_fig)
        ], className='six columns', style={'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'})
    ], className='row')

], style={'background-color':'#f2f2f2', 'padding-left':'5%', 'padding-right':'5%', 'padding-bottom':'5%'})

@app.callback(
    [Output('prob-graph', 'figure'),
     Output('cluster-graph', 'figure'),
     Output('Clustered Table', 'data'),
     Output('Clustered Table', 'columns')],        # A saída é a figura do gráfico
    [Input('select-element', 'value'),
     Input('Data Table', 'data')])             # Entrada: valor da tabela,
def update_graph(element_column, data_dict):
    if element_column == None:
        return init_fig, init_fig, [{"name": '', "id": ''} for i in range(0, 6)], [{"name": '', "id": ''} for i in range(0,6)]
    else:
        df = pd.DataFrame.from_dict(data_dict, 'columns')
        x, y = vislogprob.logprob(df[element_column])
        X = np.array([x,y])

        visualizer = KElbowVisualizer(KMeans(), k=(1, 8))
        visualizer.fit(X.transpose())

        df_clustered = vislogprob.clustered_df(X.transpose(), visualizer.elbow_value_)

        probgraf_fig = px.scatter(x=df_clustered.Prob[::-1], y=df_clustered.Value, color=df_clustered.Class, log_y=True, log_x=True,
                                  labels={'x':'Probability (%) ', 'y':str(element_column)+''}, title=str(element_column)+' x Cumulative Probability')
        probgraf_fig.update_layout(margin={'l': 60, 'b': 30, 't': 40, 'r': 60}, paper_bgcolor='#f9f9f9', legend_orientation="h")

        cluster_fig = px.line(x=visualizer.k_values_, y=visualizer.k_scores_, labels={'x':'Number of K clusters', 'y':'Distortion Score'}, range_y=[-5, np.max(visualizer.k_scores_)+np.mean(visualizer.k_scores_)/3])
        cluster_fig.update_traces(mode="markers+lines", hovertemplate=None)
        cluster_fig.add_shape(dict(type='line',
                                   x0=visualizer.elbow_value_,
                                   y0=-np.mean(visualizer.k_scores_),
                                   x1=visualizer.elbow_value_,
                                   y1=np.max(visualizer.k_scores_)+np.mean(visualizer.k_scores_),
                                   line=dict(dash='dashdot', color='#EF553B')))
        cluster_fig.update_layout(margin={'l': 60, 'b': 30, 't': 40, 'r': 60}, paper_bgcolor='#f9f9f9', legend_orientation="h")

        merged_df = df.merge(df_clustered, left_on=element_column, right_on='Value')
        merged_df = merged_df.drop(axis=1, labels='Value')
        cluster_columns = [{"name": i, "id": i} for i in merged_df.columns]

        return probgraf_fig, cluster_fig, merged_df.to_dict('records'), cluster_columns

@app.callback(
    Output('Freq Table', 'data'),                   # A saída são as dados da tabela
    [Input('select-element', 'value'),
     Input('Data Table', 'data')])             # Entrada: valor da tabela
def update_freq(element_column, data_dict):
    if element_column == None:
        return [{"name": '', "id": ''} for i in range(0,6)]
    else:
        df = pd.DataFrame.from_dict(data_dict, 'columns')
        freq_df = vislogprob.tabela_frequencias(df[element_column])
        return freq_df.to_dict('records')

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
        print(type(data[0]))
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
    map_init_fig.update_layout(margin={"r": 10, "t": 10, "l": 10, "b": 10})
    geodf = pd.DataFrame.from_dict(geo_dict, 'columns')

    if lon == None or lat == None:
        print('sem long e sem lat')
        if geo_column == None:
            print('sem seleção do geojson')
            return map_init_fig
        if geo_column != None:
            print('selecionou o geojson')
            geodf['geometry'] = geodf['geometry'].apply(wkt.loads)
            geojson = geo.add_ids(geodf, list(geodf.index), geo_column)
            map = px.choropleth_mapbox(geodf, geojson=geojson, color=geo_column,
                                       locations=list(geodf.index),
                                       center={"lat": -13.499799951999933, "lon": -48.57199078199994},
                                       mapbox_style="carto-positron", zoom=9, opacity=0.3)
            map.update_layout(margin={"r": 10, "t": 10, "l": 10, "b": 10})
            return map

    if lon != None and lat != None:
        print('tem lat e long')
        if geo_column == None:    # Mapa com pontos e sem polígonos
            if element_column == None:        # Retorna Mapa de pontos sem cluster
                print('sem seleção do elemento')
                df = pd.DataFrame.from_dict(data_dict, 'columns')
                map_init_fig.add_scattermapbox(lat=df[lat], lon=df[lon])
                map_init_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

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
                map.update_layout(margin={"r": 10, "t": 10, "l": 10, "b": 10})
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
                map.update_layout(margin={"r": 10, "t": 10, "l": 10, "b": 10})
                return map

    else:
        return map_init_fig

if __name__ == '__main__':
    app.run_server(debug=True)   # Atualiza a página automaticamente com modificações do código fonte