import dash
import dash_table
import dash_core_components as dcc  # São componentes interativos gerados com js, html e css através do reactjs
import dash_html_components as html # Possui um componente para cada tag html
from dash.dependencies import Input, Output
import plotly.express as px

from matplotlib import pyplot as plt
import pandas as pd
import vislogprob
import numpy as np

# Style:
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
layout_table = dict(
    autosize=True,
    height=500,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
)
layout_table['font-size'] = '12'
layout_table['margin-top'] = '20'
# Load data:
data = pd.read_csv('C:/Users/Pedro/PycharmProjects/Geochemical-Prospection/DashGeochemicalProspection/Data/data_asbi.csv')
x, y = vislogprob.logprob(data['Bi (PPM)'])

fig = px.scatter(x=x[::-1]*100, y=y, title='Bi (PPM) x Cumulative Probability', log_x=True, log_y=True, labels={'x':'Probability (%)', 'y': 'Bi (ppm)'})



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

                    html.Div([dcc.Upload(html.Button('Upload your data', style={'width':'100%'}))]),

                    html.H4('1.2 Select Geochemical Element:', style={'textAlign': 'center', 'font-size':'20px'}),
                    dcc.Dropdown(options=[{"label": i, "value": i} for i in data.columns], id='select-element', style={'margin-bottom':'20px'})



                ], className='row'),

                    dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in data.columns],
                        data=data.to_dict('records'),
                        style_table={'overflowX': 'scroll',
                                     'overflowY': 'scroll',
                                     'height':'380px'}
                    )
                ], className='five columns', style={'border-style':'solid','border-width':'thin', 'padding':'5px', 'border-radius':'8px'})]),

        html.Div([   # Classe Caixa
            html.Div([   # classe 7 colunas
                html.H3(children='2. Visualize Log-Probability curve:', style={'textAlign': 'center', 'color': '#054b66'}),

                dcc.Graph(
                    id='prob-graph',
                    figure=fig,
                    style={'color': '#054b66'}
                )
            ], className='seven columns', style={'border-style':'solid','border-width':'thin', 'margin': '20px', 'border-radius':'8px', 'height':'550px'})])

    ], className='row'),

    html.Hr()
])

@app.callback(
    Output('prob-graph', 'figure'),        # A saída é a figura do gráfico
    [Input('select-element', 'value')])             # Entrada: valor do slider
def update_graph(element_column):
    x, y = vislogprob.logprob(data[element_column])

    return {
        'data': [dict(
            x = x[::-1] * 100,
            y=y,
            mode='markers',
            marker={
                'size': 5,
                'opacity': 1,
                'line': {'width': 0.5, 'color': 'white'}
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
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)   # Atualiza a página automaticamente com modificações do código fonte