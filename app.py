import base64
import io
import dash
import dash_table
import dash_core_components as dcc  # São componentes interativos gerados com js, html e css através do reactjs
import dash_html_components as html # Possui um componente para cada tag html
from dash.dependencies import Input, Output, State
import plotly.express as px

from matplotlib import pyplot as plt
import pandas as pd
import vislogprob
import numpy as np

# Style:
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Load data:
#data = pd.read_csv('C:/Users/Pedro/PycharmProjects/Geochemical-Prospection/DashGeochemicalProspection/Data/data_asbi.csv')
#x, y = vislogprob.logprob(data['Bi (PPM)'])
#freq_df = vislogprob.tabela_frequencias(data['Bi (PPM)'])
init_fig = {
            'data': [dict(
                x = [],
                y=[],
                mode='markers'
            )],
            'layout': dict(
                xaxis={
                    'title': 'Cumulative Probability (%)',
                    'type': 'log'
                },
                yaxis={
                    'title': 'Element axis',
                    'type': 'log'
                },
                title= 'Load your Data first',
                margin={'l': 60, 'b': 40, 't': 40, 'r': 60},
                hovermode='closest'
            )
        }


app.layout = html.Div(children=[
    html.H1(children='Geochemical Prospection', style={'textAlign': 'left', 'color': '#054b66'}),

    html.Div(children='''
        Workflow for Geochemical Prospection utilyzing Dash and K-means Clustering
    '''),

    html.Hr(), # Linha Divisória -> Começo da aplicação

    html.Div([  # classe ROW -> dois containers
        html.Div([  # classe caixa
            html.Div([  # classe 5 colunas
                html.Div([
                    html.Div([html.H3(children='1. Load table:', style={'textAlign': 'center', 'color': '#054b66'})]),

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
                            'textAlign': 'center'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    )),

                    html.H4('1.2 Select Geochemical Element:', style={'textAlign': 'center', 'font-size':'20px'}),
                    dcc.Dropdown(id='select-element', style={'margin-bottom':'20px'})



                ], className='row'),
                    html.Div([       # Div para as tabs
                        dcc.Tabs(id='tabs', value='tab-1', children=[  # componente tabs
                            dcc.Tab(children=[                              # Data-Table
                                dash_table.DataTable(id='Data Table', columns=[{"name": '', "id": ''} for i in range(0,6)], style_table={'overflowX':'scroll', 'overflowY':'scroll', 'height':'250px'})
                            ], label='Data Table', value='tab-1'),
                            dcc.Tab(children=[
                                dash_table.DataTable(id='Freq Table', columns=[{'name':'Mínimo', 'id':'Mínimo'}, {'name':'Máximo', 'id':'Máximo'}, {'name':'Mínimo (log)', 'id':'Mínimo (log)'}, {'name':'Frequência Absoluta', 'id':'Frequência Absoluta'}, {'name':'Frequência Relativa (%)', 'id':'Frequência Relativa (%)'}, {'name':'Frequência Acumulada', 'id':'Frequência Acumulada'}, {'name':'Frequência Acumulada Direta (%)', 'id':'Frequência Acumulada Direta (%)'}, {'name':'Frequência Acumulada Invertida (%)', 'id':'Frequência Acumulada Invertida (%)'}], style_table={'overflowX':'scroll', 'overflowY':'scroll', 'height':'250px'})
                            ], label='Frequencies Table', value='tab-2')      # Frequency Table
                        ])])
                ], className='four columns', style={'border-style':'solid','border-width':'thin', 'padding':'5px', 'border-radius':'8px', 'height':'auto'})]),

        html.Div([   # Classe Caixa
            html.Div([   # classe 7 colunas
                html.H3(children='2. Visualize Log-Probability curve:', style={'textAlign': 'center', 'color': '#054b66'}),

                dcc.Graph(
                    id='prob-graph', figure=init_fig
                )
            ], className='six columns', style={'border-style':'solid','border-width':'thin', 'margin': '20px', 'border-radius':'8px', 'height':'550px'})])

    ], className='row'),

    html.Hr()
])

@app.callback(
    Output('prob-graph', 'figure'),        # A saída é a figura do gráfico
    [Input('select-element', 'value'),
     Input('Data Table', 'data')])             # Entrada: valor da tabela,
def update_graph(element_column, data_dict):
    if element_column == None:
        return init_fig
    else:
        df = pd.DataFrame.from_dict(data_dict, 'columns')
        x, y = vislogprob.logprob(df[element_column])

        return {
            'data': [dict(
                x = x[::-1] * 100,
                y=y,
                mode='markers',
                marker={
                    'size': 5,
                    'opacity': 1
                }
            )],
            'layout': dict(
                xaxis={
                    'title': 'Cumulative Probability (%)',
                    'type': 'log'
                },
                yaxis={
                    'title': str(element_column),
                    'type': 'log'
                },
                title= str(element_column)+' x Cumulative Probability',
                margin={'l': 60, 'b': 40, 't': 40, 'r': 60},
                hovermode='closest'
            )
        }

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
        print(freq_df.columns)
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

@app.callback([Output('Data Table', 'data'),
              Output('Data Table', 'columns'),
              Output('select-element', 'options'),
              Output('select-element', 'value')],   # Output('select-element', 'options')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(list_of_contents, list_of_names):
    if list_of_contents is None:
        return [{"name": '', "id": ''} for i in range(0,6)], [{"name": '', "id": ''} for i in range(0,6)], [{"label": '', "value": ''} for i in range(0,6)], None
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

        return data, columns, markdowns, None

if __name__ == '__main__':
    app.run_server(debug=True)   # Atualiza a página automaticamente com modificações do código fonte