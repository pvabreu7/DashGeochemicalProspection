import dash
import dash_core_components as dcc  # São componentes interativos gerados com js, html e css através do reactjs
import dash_html_components as html # Possui um componente para cada tag html
import plotly.express as px
import pandas as pd
import numpy as np

# Style:
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# Load data:
data = pd.read_csv('C:/Users/Pedro/PycharmProjects/Geochemical-Prospection/DashGeochemicalProspection/Data/data_asbi.csv')
print(data.columns)
fig = px.scatter(data, 'As (PPM)', 'Bi (PPM)')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Geochemical Prospection', style={'textAlign': 'left', 'color': '#054b66'}), # no Html, "style" é um string separado por ;
                                                                                       # No dash, basta passar um dicionário
    html.Div(children='''
        Workflow for Geochemical Prospection utilyzing Dash and K-means Clustering
    '''),

    html.Hr(),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)   # Atualiza a página automaticamente com modificações do código fonte