import dash
import dash_table
import dash_core_components as dcc  # São componentes interativos gerados com js, html e css através do reactjs
import dash_html_components as html # Possui um componente para cada tag html
import plotly.express as px
from matplotlib import pyplot as plt
import pandas as pd
import vislogprob
import numpy as np

# Style:
external_stylesheets = ['https://codepen.io/amyoshino/pen/jzXypZ.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Load data:
data = pd.read_csv('C:/Users/Pedro/PycharmProjects/Geochemical-Prospection/DashGeochemicalProspection/Data/data_asbi.csv')
x, y = vislogprob.logprob(data['Bi (PPM)'])

fig = px.scatter(x=x[::-1]*100, y=y, title='Bi (PPM) x Cumulative Probability', log_x=True, log_y=True, labels={'x':'Probability (%)', 'y': 'Bi (ppm)'})



app.layout = html.Div(children=[
    html.H1(children='Geochemical Prospection', style={'textAlign': 'left', 'color': '#054b66'}),

    html.Div(children='''
        Workflow for Geochemical Prospection utilyzing Dash and K-means Clustering
    '''),

    html.Hr(),

    html.Div([
        html.Div([
            html.Div([
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in data.columns],
                    data=data.to_dict('records'),
                    style_table={'overflowX': 'scroll',
                                 'overflowY': 'scroll',
                                 'height':'380px'}
                )
            ], className='five columns'),

            html.Div([
                dcc.Graph(
                    id='example-graph',
                    figure=fig,
                    style={'color': '#054b66'}, className='seven columns'
            )])
        ])
    ], className='row'
    ),
    html.Hr()
])

if __name__ == '__main__':
    app.run_server(debug=True)   # Atualiza a página automaticamente com modificações do código fonte