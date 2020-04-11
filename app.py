import dash
import dash_core_components as dcc  # São componentes interativos gerados com js, html e css através do reactjs
import dash_html_components as html # Possui um componente para cada tag html
import plotly.express as px
import pandas as pd
import vislogprob
import numpy as np

# Style:
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Load data:
data = pd.read_csv('C:/Users/Pedro/PycharmProjects/Geochemical-Prospection/DashGeochemicalProspection/Data/data_asbi.csv')
x, y= vislogprob.logprob(data['As (PPM)'])

fig = px.scatter(x=x, y=y[::-1])

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

app.layout = html.Div(children=[
    html.H1(children='Geochemical Prospection', style={'textAlign': 'left', 'color': '#054b66'}), # no Html, "style" é um string separado por ;
                                                                                       # No dash, basta passar um dicionário
    html.Div(children='''
        Workflow for Geochemical Prospection utilyzing Dash and K-means Clustering
    '''),

    html.Hr(),

    dcc.Graph(
        id='example-graph',
        figure=fig,
        style={'color': '#054b66'}
    ),

    generate_table(data)
])

if __name__ == '__main__':
    app.run_server(debug=True)   # Atualiza a página automaticamente com modificações do código fonte