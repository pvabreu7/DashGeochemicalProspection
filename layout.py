import dash_core_components as dcc  # São componentes interativos gerados com js, html e css através do reactjs
import dash_html_components as html # Possui um componente para cada tag html
import dash_bootstrap_components as dbc # Bootstrap
import dash_table
import plotly.express as px

init_fig = px.scatter(x=None, y=None, log_x=True, log_y=True, labels={'x':'x axis', 'y':'y axis'})
init_fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10}, paper_bgcolor='#f9f9f9')
map_init_fig = px.choropleth_mapbox(locations=[0], center={"lat": -13.5, "lon": -48.5}, mapbox_style="carto-positron", zoom=4)
map_init_fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10}, paper_bgcolor='#f9f9f9')

dash = html.Div(children=[
    dcc.Store(id="aggregate_data"),
    # empty Div to trigger javascript file for graph resizing
    html.Div(id="output-clientside"),
    html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                        html.Img(src='assets/icone.png', style={'height':'120px', 'width':'120px', 'display': 'inline-block', 'float':'left'})
                        ]
                    ),
                    html.Div(
                        [
                            html.H3(
                                "Geochemical Prospection",
                                style={"margin-bottom": "0px", 'display': 'inline-block'},
                            ),
                            html.P(
                                "Workflow for Geochemical Prospecting utilizing Dash and K-means Clustering", style={'font-size':'16px',"margin-top": "0px", "margin-bottom": "0px", 'display': 'inline-block', 'font-style':'italic'}
                            ),
                            html.P(
                                ["Application developed by Pedro Vitor Abreu ", " | ",
                                 "Email: pvabreu7@gmail.com ", " | ",
                                 html.A('LinkedIn', href='https://www.linkedin.com/in/pedro-vitor-abreu-63ba6214a/', target="_blank"), ' | ',
                                 html.A('Github', href='https://github.com/pvabreu7', target="_blank"), ' | ',
                                 html.A('About the app', id='about'),
                                 dbc.Modal(
                                     [
                                         dbc.ModalHeader("About the Geochemical Prospection App "),
                                         dbc.ModalBody(['The main idea behind the development of this app was born after I simplificated a workflow of geochemical prospecting with python code during a course of Mineral Exploration at the Federal University of Rio de Janeiro. The approach of the workflow is foccused in the classification of stream sediments samples in classes of anomolous or background samples in order to target possible areas of mineral interest.',
                                                        html.P(' '),
                                                        html.P('The idea of the code was to simplify the management of the data that was very time consuming, and give  more focus to the statistical and geological insights of the data rather than the "know hows" of the many distinct softwares that were being utilized for this purpose. By exporting the final generated tables, the user could then utilize a GIS software to further work with the data.'),
                                                        html.P(' '),
                                                        html.P('Based on that, I felt motivated to also develop a friendly user interface to support geoscience students and researchers that are not into python programming, and thus this app has been created.  '),
                                                        html.P(' '),
                                                        html.P('Feel free to contact me to suggest improvements on the app, or to develop something new with me. I hope the app is useful!'),
                                                        html.P(' '),
                                                        html.P('Pedro Vitor Abreu')
                                                        ]),
                                         dbc.ModalFooter(
                                             dbc.Button("Close", id="close-sm", className="ml-auto")
                                         ),
                                     ],
                                     id="modal-sm",
                                     centered=True,
                                     size="lg",
                                 )
                                 ],
                                style={'font-size': '14px', "margin-top": "0px"}
                            )
                        ]
                    ),
                ], className='row'
            )
        ],
        id="title", style={'display':'flex'}
    ),

    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.P(children=['1. Load .csv data:', html.Span(['?'], id='tooltip-loadcsv', style={'textAlign':'center', 'color':'white', "cursor": "pointer"}, className='dot')], style={'textAlign': 'center', 'color': 'rgb(5, 75, 102)', 'font-size':'16px'}),
                    dbc.Tooltip(
                        'Your data must be of the csv format. '
                        'Be sure that your data is formated correctly, with "." instead of "," for decimal values, and only with numerical values in the column that you want to prospect the data.',
                        target="tooltip-loadcsv", placement='right', style={'font-size': '14px', 'border-radius': '6px', 'opacity': '0.9',
                                                                            'background-color': '#3275a8'}
                    ),
                    html.Div(dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        className='dragdrop',
                        # Allow multiple files to be uploaded
                        multiple=True
                    )),

                    dbc.Alert("No csv data loaded.", id="alert-csv", fade=True, is_open=True, color="light"),

                    html.P(children='1.2 Select Geochemical Element:', style={'textAlign': 'center', 'font-size':'14px'}),

                    dcc.Dropdown(id='select-element', style={'margin-bottom':'5px'}, placeholder='Select Geochemical Element...'),

                    html.P(children=['2. Load Geojson data:', html.Span(['?'], id='tooltip-loadgeojson', style={'textAlign':'center', 'color':'white', "cursor": "pointer"}, className='dot')], style={'textAlign': 'center', 'font-size':'16px',  'color': 'rgb(5, 75, 102)'}),
                    dbc.Tooltip(
                        'GeoJSON is a format for encoding a variety of geographic data structures. '
                        'It is similar to a ESRI shapefile, and can be exported from any GIS software. '
                        'Be sure that your data utilyze a geographic coordinate system in order to be plotted.',
                        target="tooltip-loadgeojson", placement='right',
                        style={'font-size': '14px', 'border-radius': '6px', 'opacity': '0.9',
                               'background-color': '#3275a8'}
                    ),

                    html.Div(dcc.Upload(
                        id='upload-shapes',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        className='dragdrop',
                        # Allow multiple files to be uploaded
                        multiple=True
                    )),

                    dbc.Alert("No geojson data loaded.", id="alert-geojson", fade=True, is_open=True, color="light")

                ], className='row')

                ], className='start column', style={'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey', 'width':'20%', 'height':'420.6px'})]),

        html.Div([  # Classe Caixa
            html.Div([  # classe 7 colunas
                html.P(children=['2. Nº of Clusters by Elbow Method:', html.Span(['?'], id='tooltip-elbow', style={'textAlign':'center', 'color':'white', "cursor": "pointer"}, className='dot')], style={'textAlign': 'center', 'font-size':'16px',  'color': 'rgb(5, 75, 102)'}),
                dbc.Tooltip(
                    ' If the line chart resembles an arm, then the “elbow” (the point of inflection on the curve) is a good indication that the underlying model fits best at that point.',
                    target="tooltip-elbow", placement='right',
                    style={'font-size': '14px', 'border-radius': '6px', 'opacity': '0.9',
                           'background-color': '#3275a8'}
                ),
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
                                html.P(children=['3. Log-probability curve:', html.Span(['?'], id='tooltip-logprob', style={'textAlign':'center', 'color':'white', "cursor": "pointer"}, className='dot')],
                                       style={'textAlign': 'left', 'width': '41%', 'font-size': '16px',  'color': 'rgb(5, 75, 102)',
                                              'display': 'inline-block', 'float': 'left'}),
                                dbc.Tooltip(
                                    'Toggle "Cluster" to utilize Kmeans clustering with the optimized  number "K" of classes.'
                                    'Toggle to "Select" to select the anomalous samples manually by selecting them on the graph.'
                                    'You can press the "Prob Scale" button to generate a graph with a probability scale axis.',
                                    target="tooltip-logprob",
                                    style={'font-size': '14px', 'border-radius': '6px', 'opacity': '0.9',
                                           'background-color': '#3275a8'}
                                )
                            ]
                        ),
                        html.Div(
                            [
                                dcc.RadioItems(id='logprob-mode', options=[{'label':'Clusters', 'value':'cluster-mode'}, {'label':'Selection', 'value':'select-mode'}], labelStyle={'display': 'inline-block', 'margin-top':'3px', 'float':'left'}, value='cluster-mode'),
                                html.Button('Prob Scale', id='prob-scale-button', style={'display': 'inline-block', 'width':'24%', 'margin-left':'8px', 'line-height':'3rem'}, className='button'),
                                dbc.Modal([
                                    dbc.ModalBody([html.Img(id='probscale-img')], style={'margin-left':'6px'}),
                                    dbc.ModalFooter(dbc.Button("Close", id="prob-scale-close", className="ml-auto"))
                                ], id='prob-scale-modal', size="lg", centered=True)
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
            html.P(children=['4. Spatial Overview:', html.Span(['?'], id='tooltip-spatial', style={'textAlign':'center', 'color':'white', "cursor": "pointer"}, className='dot')], style={'textAlign': 'center', 'color': 'rgb(5, 75, 102)', 'font-size':'16px'}),
            dbc.Tooltip(
                'All of the data must be utilizing geographic coordinate systems in order to be plotted on the map.',
                target="tooltip-spatial",
                style={'font-size': '14px', 'border-radius': '6px', 'opacity': '0.9',
                       'background-color': '#3275a8'}
            ),
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
                        dash_table.DataTable(id='Data Table', columns=[{"name": '', "id": ''} for i in range(0, 6)], data=[{"name": '', "id": ''} for i in range(0,11)],
                                             style_table={'height':'400px', 'overflowX': 'scroll', 'overflowY': 'scroll'},
                                             style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                                             style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'}, page_action='none')
                    ], label='Data Table', value='tab-1', style={'font-size':'12px'}),
                    dcc.Tab(children=[
                        dash_table.DataTable(id='Freq Table', columns=[{'name': 'Lower limit', 'id': 'Lower limit'},
                                                                       {'name': 'Upper limit', 'id': 'Upper limit'},
                                                                       {'name': 'Lower limit (log)', 'id': 'Lower limit (log)'},
                                                                       {'name': 'Absolut Frequency',
                                                                        'id': 'Absolut Frequency'},
                                                                       {'name': 'Relative Frequency (%)',
                                                                        'id': 'Relative Frequency (%)'},
                                                                       {'name': 'Count',
                                                                        'id': 'Count'},
                                                                       {'name': 'Direct Cumulative Frequency (%)',
                                                                        'id': 'Direct Cumulative Frequency (%)'}],
                                             style_table={'overflowX': 'scroll', 'overflowY': 'scroll',
                                                          'height': '400px'},
                                             style_data_conditional=[
                                                 {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                                             style_header={'backgroundColor': 'rgb(230, 230, 230)',
                                                           'fontWeight': 'bold'},
                                             data=[{"name": '', "id": ''} for i in range(0,11)], page_action='none'
                    )
                    ], label='Frequency Table', value='tab-2', style={'font-size':'12px'}), # Frequency Table
                    dcc.Tab(children=[  # Data-Table
                        dash_table.DataTable(id='Clustered Table', columns=[{"name": '', "id": ''} for i in range(0, 6)],
                                             style_table={'overflowX': 'scroll', 'overflowY': 'scroll',
                                                          'height': '400px'},
                                             style_data_conditional=[
                                                 {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                                             style_header={'backgroundColor': 'rgb(230, 230, 230)',
                                                           'fontWeight': 'bold'},
                                             data=[{"name": '', "id": ''} for i in range(0,11)], page_action='none'
                    )
                    ], label='Clustered Table', value='tab-3', style={'font-size':'12px'}),
                    dcc.Tab(children=[  # Data-Table
                        dash_table.DataTable(id='Geojson Table',
                                             columns=[{"name": '', "id": ''} for i in range(0, 6)],
                                             style_table={'overflowX': 'scroll', 'overflowY': 'scroll',
                                                          'height': '400px'},
                                             style_data_conditional=[
                                                 {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                                             style_header={'backgroundColor': 'rgb(230, 230, 230)',
                                                           'fontWeight': 'bold'},
                                             data=[{"name": '', "id": ''} for i in range(0,11)], page_action='none')
                    ], label='Geojson Data', value='tab-4', style={'font-size':'12px'})
                ]),
                html.Div([
                    html.Div([dcc.Dropdown(id='select-download', placeholder='Select Table for Download...', value='All samples', options=[{'label':'Frequency Table', 'value':'freq-table'}, {'label':'Clustered Table', 'value':'cluster-table'}])],
                             style={'margin-top': '14px', 'margin-bottom': '10px', 'width': '48%', 'float': 'left', 'display': 'inline-block'}),

                    #dbc.Button('Download Table as Csv', id='download-link', href="", target="_blank",  style={'margin-top': '10px', 'margin-bottom': '10px', 'width': '48%', 'display': 'inline-block', 'float': 'right'})
                    html.A(['Download Table as csv'], id='download-link',
                             style={'margin-top': '10px', 'margin-bottom': '10px', 'width': '48%', 'display': 'inline-block', 'float': 'right'}, className='button',download="datatable.csv", href="", target="_blank")
                ]),

            ]),
            html.Span(['How is the frequency table calculated?'], id='tooltip-freq', style={"textDecoration": "underline", "cursor": "pointer", 'font-size':'14px', 'display':'inline-block', 'width':'100%'}),
            dbc.Tooltip(
                'Frequency Table is calculated by the Sturges and Doane rules for determining classes intervals. '
                'Doane rule is applied when the data is not normally distributed.',
                target="tooltip-freq",
                style={'font-size': '14px', 'border-radius': '6px', 'opacity': '0.9',
                       'background-color': '#3275a8'}
            )
        ], className='five columns', style={'height':'620px','border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'})
    ], className='row'),

    html.Div([
        html.Div([
            html.Div([
                html.Div(['Distribution Plot:', html.Span(['?'], id='tooltip-dist', style={'textAlign':'center', 'color':'white', "cursor": "pointer"}, className='dot')],
                         style={'line-height':'2.2', 'margin-bottom': '10px', 'width': '48%', 'display': 'inline-block', 'textAlign': 'center', 'color': 'rgb(5, 75, 102)', 'font-size':'16px'}),
                dbc.Tooltip(
                    'Visualize the distribution of the clustered table with bar charts and boxplots.',
                    target="tooltip-dist",
                    style={'font-size': '14px', 'border-radius': '6px', 'opacity': '0.9',
                           'background-color': '#3275a8'}
                ),
                html.Div(
                    [dcc.Dropdown(id='select-classes', placeholder='Select Class...', value='All samples')],
                    style={'margin-bottom': '10px', 'width': '48%', 'float': 'right', 'display': 'inline-block'})
            ]),

            dcc.Graph(id='dist-plot', figure=init_fig, style={'height':'350px', 'margin-top':'10px'})
        ], className='six columns', style={'border-radius':'5px', 'background-color':'#f9f9f9', 'margin':'10px', 'padding':'15px', 'position':'relative', 'box-shadow':'6px 6px 2px lightgrey'}),

        html.Div([
            html.Div([
                html.Div(['Spatial Join Plot:', html.Span(['?'], id='tooltip-spjoin', style={'textAlign':'center', 'color':'white', "cursor": "pointer"}, className='dot')],
                         style={'line-height':'2.2', 'margin-bottom': '10px', 'width': '48%', 'display': 'inline-block', 'textAlign':'center', 'color': 'rgb(5, 75, 102)', 'font-size':'16px'}),
                dbc.Tooltip(
                    'The spatial join verifies how many samples of the selected class are inside of the selected polygon label.',
                    target="tooltip-spjoin",
                    style={'font-size': '14px', 'border-radius': '6px', 'opacity': '0.9',
                           'background-color': '#3275a8'}
                ),
                html.Div([dcc.Dropdown(id='select-join-classes', placeholder='Select Class...', value='Anomalous Sample')],
                         style={'margin-bottom': '10px', 'width': '48%', 'float': 'right', 'display': 'inline-block'})
            ]),

            dcc.Graph(id='bar-plot', figure=init_fig, style={'height':'350px', 'margin-top':'10px'})
        ], className='six columns', style={'border-radius': '5px', 'background-color': '#f9f9f9', 'margin': '10px', 'padding': '15px', 'position': 'relative', 'box-shadow': '6px 6px 2px lightgrey'})
    ], className='row')

], style={'background-color':'#f2f2f2', 'padding-left':'5%', 'padding-right':'5%', 'padding-bottom':'5%'})