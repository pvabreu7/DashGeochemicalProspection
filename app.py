import dash
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
#fig = plt.figure()
#plt.loglog(x[::-1], y)
#plt.xlabel('Probability (%)')
#plt.ylabel('Bi (ppm)')
#plt.title('Bi (PPM) x Cumulative Probability')

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ]),

    ])

app.layout = html.Div(children=[
    html.H1(children='Geochemical Prospection', style={'textAlign': 'left', 'color': '#054b66'}), # no Html, "style" é um string separado por ;
                                                                                       # No dash, basta passar um dicionário
    html.Div(children='''
        Workflow for Geochemical Prospection utilyzing Dash and K-means Clustering
    '''),

    html.Hr(),
    html.Div([
        html.Div([
            dcc.Graph(
                id='example-graph',
                figure=fig,
                style={'color': '#054b66'}, className='six columns'
        )]),
        html.Div([
            generate_table(data, max_rows=20)
        ], className='six columns')
])])

if __name__ == '__main__':
    app.run_server(debug=True)   # Atualiza a página automaticamente com modificações do código fonte