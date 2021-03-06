import base64
import io
import dash
import dash_html_components as html # Possui um componente para cada tag html

from dash.dependencies import Input, Output, State
from yellowbrick.cluster import KElbowVisualizer
from sklearn.cluster import KMeans
from layout import dash as dashboard
import pandas as pd
import vislogprob
from shapely import wkt
import geo
import numpy as np
import urllib
import plotly.express as px

init_fig = px.scatter(x=None, y=None, log_x=True, log_y=True, labels={'x':'x axis', 'y':'y axis'})
init_fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10}, paper_bgcolor='#f9f9f9')
map_init_fig = px.choropleth_mapbox(locations=[0], center={"lat": -13.5, "lon": -48.5}, mapbox_style="carto-positron", zoom=4)
map_init_fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10}, paper_bgcolor='#f9f9f9')

# Style:
external_stylesheets = 'https://codepen.io/pvabreu7/pen/ZEbgQpd.css'
app = dash.Dash(__name__, external_stylesheets=[external_stylesheets])

app.layout = dashboard
app.title = 'DEBUG Geochemical Prospection'

# Download table Callback
@app.callback(
    Output('download-link', 'href'),
    [Input('select-download', 'value'),
     Input('Freq Table', 'data'),
     Input('Clustered Table', 'data')])
def update_download_link(selected_table, freq_dict, cluster_dict):
    if selected_table == None:
        raise dash.exceptions.PreventUpdate
    if selected_table == 'freq-table':
        df = pd.DataFrame.from_dict(freq_dict, 'columns')
        csv_string = df.to_csv(index=False, encoding='ISO-8859-1')
        csv_string = "data:text/csv;charset=iso-8859-1," + '\uFEFF'  + urllib.parse.quote(csv_string)

        return csv_string
    if selected_table == 'cluster-table':
        df = pd.DataFrame.from_dict(cluster_dict, 'columns')
        csv_string = df.to_csv(index=False, encoding='ISO-8859-1')
        csv_string = "data:text/csv;charset=iso-8859-1," + '\uFEFF'  + urllib.parse.quote(csv_string)

        return csv_string

# Distribution Callback
@app.callback(
    [Output('dist-plot', 'figure'),
     Output('select-classes', 'options')],
    [Input('select-element', 'value'),
     Input('Clustered Table', 'data'),
     Input('select-classes', 'value')]
)
def update_dists(element_column, cluster_dict, selected_plot):
    if element_column == None:
        raise dash.exceptions.PreventUpdate
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

# Bar-plot Callback
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
        raise dash.exceptions.PreventUpdate
    else:
        try:
            cluster_df = pd.DataFrame.from_dict(cluster_dict, 'columns')
            geojson_df = pd.DataFrame.from_dict(geojson_dict, 'columns')

            markdowns = [{"label": i, "value": i} for i in cluster_df.Class.unique()]
            markdowns.append({"label": 'All samples', "value": 'All samples'})

            geojson_df['geometry'] = geojson_df['geometry'].apply(wkt.loads)

            joined = geo.spatial_join(cluster_df, lon, lat, geojson_df)
            counts = []
            if select_class == 'All samples':
                for i in joined[polygon_label].unique():
                    count = round(len(joined[joined[polygon_label] == i])/len(joined[polygon_label].unique()), ndigits=3)
                    counts.append(count*10)
            else:
                for i in joined[polygon_label][joined.Class == select_class].unique():
                    count = round(len(joined[joined[polygon_label] == i][joined.Class == select_class])/len(joined[joined.Class == select_class]), ndigits=3)
                    counts.append(count*100)
            if select_class == 'All samples':
                bar = px.bar(y=joined[polygon_label].unique(), x=counts, orientation='h', labels={'x':'Relative Frequency (%)', 'y':'Polygon Label'}, color=joined[polygon_label].unique())
                bar.update_layout(margin={'l': 60, 'b': 30, 't': 40, 'r': 60}, paper_bgcolor='#f9f9f9', showlegend=False)
            else:
                bar = px.bar(y=joined[polygon_label][joined.Class == select_class].unique(), x=counts, orientation='h', labels={'x':'Relative Frequency (%)', 'y':'Polygon Label'}, color=joined[polygon_label][joined.Class == select_class].unique())
                bar.update_layout(margin={'l': 60, 'b': 30, 't': 40, 'r': 60}, paper_bgcolor='#f9f9f9', showlegend=False)

            return bar, markdowns

        except ValueError as e:
            print('Got Value error')
            print(e)
            return init_fig, [{"label": '', "value": ''} for i in range(0,1)]
        except AttributeError as e:
            print('Got Attribute error')
            print(e)
            return init_fig, [{"label": '', "value": ''} for i in range(0,1)]
        except KeyError as e:
            print('Got Key error')
            print(e)
            return init_fig, [{"label": '', "value": ''} for i in range(0,1)]

# Logprob and Cluster Callback
@app.callback(
    [Output('prob-graph', 'figure'),
     Output('cluster-graph', 'figure'),
     Output('Clustered Table', 'data'),
     Output('Clustered Table', 'columns')],
    [Input('select-element', 'value'),
     Input('Data Table', 'data'),
     Input('prob-graph', 'selectedData'),
     Input('logprob-mode', 'value')])
def update_graph(element_column, data_dict, selectedData, mode):
    if element_column is None:
        raise dash.exceptions.PreventUpdate

    if selectedData != None and mode == 'select-mode':
        df = pd.DataFrame.from_dict(data_dict, 'columns')
        x, y = vislogprob.logprob(df[element_column])

        X = np.array([x,y])
        visualizer = KElbowVisualizer(KMeans(), k=(1, 8))
        visualizer.fit(X.transpose())

        originalData = pd.DataFrame()
        originalData.insert(0, 'Relative Frequency (%)', x)
        originalData.insert(1, 'Value', y[::-1])

        selected_x = []
        for point in selectedData['points']:
            selected_x.append(point['x'])

        max_prob = np.max(selected_x)*0.01
        originalData['Class'] = originalData.apply(
            lambda row: 'Anomalous Sample' if row['Relative Frequency (%)'] <= max_prob else 'Background Sample', axis=1)

        probgraf_fig = px.scatter(x=originalData['Relative Frequency (%)']*100, y=originalData.Value, color=originalData.Class, log_y=True, log_x=True,
                                  labels={'x':'Relative Frequency (%) ', 'y':str(element_column)+''})
        probgraf_fig.update_layout(margin={'l': 10, 'b': 10, 't': 10, 'r': 10}, paper_bgcolor='#f9f9f9', legend_orientation="h", legend=dict(x=-.1, y=1.2))

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
        merged_df = merged_df.drop(axis=1, labels=['Value', 'Relative Frequency (%)'])
        merged_df.drop_duplicates(inplace=True)
        merged_df.sort_values(axis=0, by=element_column, inplace=True)

        cluster_columns = [{"name": i, "id": i} for i in merged_df.columns]

        return probgraf_fig, cluster_fig, merged_df.to_dict('records'), cluster_columns

    else:
        df = pd.DataFrame.from_dict(data_dict, 'columns')
        x, y = vislogprob.logprob(df[element_column])
        X = np.array([x,y])

        visualizer = KElbowVisualizer(KMeans(), k=(1, 8))
        visualizer.fit(X.transpose())

        df_clustered = vislogprob.clustered_df(X.transpose(), visualizer.elbow_value_)

        probgraf_fig = px.scatter(x=df_clustered['Relative Frequency (%)'], y=df_clustered.Value, color=df_clustered.Class, log_y=True, log_x=True,
                                  labels={'x':'Relative Frequency (%) ', 'y':str(element_column)+''})
        probgraf_fig.update_layout(margin={'l': 10, 'b': 10, 't': 10, 'r': 10}, paper_bgcolor='#f9f9f9', legend_orientation="h", legend=dict(x=-.1, y=1.2))

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
        merged_df = merged_df.drop(axis=1, labels=['Value', 'Relative Frequency (%)'])
        merged_df.drop_duplicates(inplace=True)
        merged_df.sort_values(axis=0, by=element_column, inplace=True)
        cluster_columns = [{"name": i, "id": i} for i in merged_df.columns]
        return probgraf_fig, cluster_fig, merged_df.to_dict('records'), cluster_columns

# Frequency Table Callback
@app.callback(
    [Output('Freq Table', 'data'),
     Output('logprob-mode', 'value')],
    [Input('select-element', 'value'),
     Input('Data Table', 'data')])
def update_freq(element_column, data_dict):
    if element_column == None:
        raise dash.exceptions.PreventUpdate
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

@app.callback([Output('select-poly', 'options'),        # Geojson Callback
               Output('select-poly', 'value'),
               Output('Geojson Table', 'data'),
               Output('Geojson Table', 'columns'),
               Output('alert-geojson', 'color'),
               Output('alert-geojson', 'children')],
               [Input('upload-shapes', 'contents')],
               [State('upload-shapes', 'filename')])
def update_geojson(list_of_contents, list_of_names):
    if list_of_contents is None:
        raise dash.exceptions.PreventUpdate
    else:
        try:
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

            return markdowns, None, data, columns, 'success', "Geojson data loaded!"
        except:
            return [{"label": '', "value": ''} for i in range(0, 1)], \
                   None, [{"name": '', "id": ''} for i in range(0, 6)], \
                   [{"name": '', "id": ''} for i in range(0, 6)], 'danger', "Error loading Geojson."

# Upload Data Callback
@app.callback([Output('Data Table', 'data'),
              Output('Data Table', 'columns'),
              Output('select-element', 'options'),
              Output('select-element', 'value'),
              Output('select-lon', 'options'),
              Output('select-lon', 'value'),
              Output('select-lat', 'options'),
              Output('select-lat', 'value'),
              Output('alert-csv', 'color'),
              Output('alert-csv', 'children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(list_of_contents, list_of_names):
    if list_of_contents is None:
        raise dash.exceptions.PreventUpdate
    if list_of_contents is not None:
        try:
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
            return data, columns, markdowns, None, markdowns, None, markdowns, None, "success", "Csv data loaded!"
        except:
            return [{"name": '', "id": ''} for i in range(0, 15)], [{"name": '', "id": ''} for i in range(0, 6)],\
                   [{"label": '', "value": ''} for i in range(0, 1)], None, [{"label": '', "value": ''} for i in range(0, 1)],\
                   None, [{"label": '', "value": ''} for i in range(0,6)], None, 'danger', "Error loading csv data"


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

    if data_dict is None and geo_dict is None:
        raise dash.exceptions.PreventUpdate

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

# Modal callbacks
@app.callback(Output("modal-sm", "is_open"),
             [Input("about", "n_clicks"), Input("close-sm", "n_clicks")],
             [State("modal-sm", "is_open")])
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(Output('prob-scale-modal', 'is_open'),
              [Input('prob-scale-button', 'n_clicks'), Input('prob-scale-close', 'n_clicks')],
              [State('prob-scale-modal', 'is_open')])
def toggle_probscale(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Matplotlib probability scale:

@app.callback(
    Output('probscale-img', 'src'), # src attribute
    [Input('select-element', 'value'),
     Input('Clustered Table', 'data')]
)
def update_figure(var, data_dict):
    if data_dict is None or var is None:
        raise dash.exceptions.PreventUpdate
    df = pd.DataFrame.from_dict(data_dict, 'columns')
    if len(df.columns) == 2:
        raise dash.exceptions.PreventUpdate
    data = vislogprob.probscale_plot(df, var)
    return "data:image/png;base64,{}".format(data)

if __name__ == '__main__':
    app.run_server(debug=True)   # Atualiza a página automaticamente com modificações do código fonte